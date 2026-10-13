import ipaddress
import json
import math
import re
import socket
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


MAX_PAGE_SIZE = 2 * 1024 * 1024
REQUEST_TIMEOUT = 8


class PriceLookupError(ValueError):
    pass


def _validate_public_url(url):
    parsed = urlsplit(url)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname:
        raise PriceLookupError('Enter a public HTTP or HTTPS product URL.')
    if parsed.username or parsed.password:
        raise PriceLookupError('Product URLs cannot contain login credentials.')

    try:
        port = parsed.port
    except ValueError as exc:
        raise PriceLookupError('The product URL has an invalid port.') from exc
    if port not in (None, 80, 443):
        raise PriceLookupError('Product URLs must use the standard web port.')

    try:
        addresses = socket.getaddrinfo(
            parsed.hostname,
            port or (443 if parsed.scheme == 'https' else 80),
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as exc:
        raise PriceLookupError('The product website could not be reached.') from exc

    if not addresses or any(
        not ipaddress.ip_address(address[4][0]).is_global
        for address in addresses
    ):
        raise PriceLookupError('The product URL must point to a public website.')


class _SafeRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, request, file_pointer, code, message, headers, new_url):
        _validate_public_url(urljoin(request.full_url, new_url))
        return super().redirect_request(
            request, file_pointer, code, message, headers, new_url
        )


class _PriceHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.json_ld = []
        self.meta_prices = []
        self.itemprop_prices = []
        self.offscreen_prices = []
        self.data_prices = []
        self.meta_titles = []
        self.title_parts = []
        self._in_json_ld = False
        self._json_ld_parts = []
        self._price_depth = 0
        self._price_parts = []
        self._offscreen_price_depth = 0
        self._offscreen_price_parts = []
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == 'script' and 'ld+json' in attributes.get('type', '').lower():
            self._in_json_ld = True
            self._json_ld_parts = []
        if tag == 'meta':
            key = (
                attributes.get('itemprop', '')
                or attributes.get('property', '')
                or attributes.get('name', '')
            ).lower()
            if key in ('price', 'product:price:amount', 'og:price:amount'):
                self.meta_prices.append(
                    attributes.get('content', '')
                )
            if key in ('og:title', 'twitter:title'):
                self.meta_titles.append(attributes.get('content', ''))
        for key in ('data-price', 'data-current-price', 'data-sale-price'):
            if attributes.get(key):
                self.data_prices.append(attributes[key])
        if tag == 'title':
            self._in_title = True
        if attributes.get('itemprop', '').lower() == 'price':
            candidate = attributes.get('content') or attributes.get('value')
            if candidate:
                self.itemprop_prices.append(candidate)
            elif tag not in ('meta', 'link', 'input'):
                self._price_depth = 1
                self._price_parts = []
        elif self._price_depth:
            self._price_depth += 1
        if 'a-offscreen' in attributes.get('class', '').split():
            self._offscreen_price_depth = 1
            self._offscreen_price_parts = []
        elif self._offscreen_price_depth:
            self._offscreen_price_depth += 1

    def handle_endtag(self, tag):
        if tag == 'title':
            self._in_title = False
        if self._in_json_ld and tag == 'script':
            self.json_ld.append(''.join(self._json_ld_parts))
            self._in_json_ld = False
        if self._price_depth:
            self._price_depth -= 1
            if not self._price_depth:
                self.itemprop_prices.append(''.join(self._price_parts))
        if self._offscreen_price_depth:
            self._offscreen_price_depth -= 1
            if not self._offscreen_price_depth:
                self.offscreen_prices.append(
                    ''.join(self._offscreen_price_parts)
                )

    def handle_data(self, data):
        if self._in_json_ld:
            self._json_ld_parts.append(data)
        if self._in_title:
            self.title_parts.append(data)
        if self._price_depth:
            self._price_parts.append(data)
        if self._offscreen_price_depth:
            self._offscreen_price_parts.append(data)


def _number_from_value(value):
    if isinstance(value, (int, float)):
        price = float(value)
    elif isinstance(value, str):
        match = re.search(r'[-+]?\d[\d.,\s]*', value)
        if not match:
            return None
        number = match.group().replace(' ', '')
        if ',' in number and '.' in number:
            decimal_separator = ',' if number.rfind(',') > number.rfind('.') else '.'
            thousands_separator = '.' if decimal_separator == ',' else ','
            number = number.replace(thousands_separator, '')
            number = number.replace(decimal_separator, '.')
        elif ',' in number:
            chunks = number.split(',')
            number = (
                ''.join(chunks)
                if len(chunks[-1]) == 3
                else '.'.join(chunks)
            )
        try:
            price = float(number)
        except ValueError:
            return None
    else:
        return None

    if not math.isfinite(price) or price <= 0:
        return None
    return price


def _json_ld_prices(data):
    if isinstance(data, list):
        for item in data:
            yield from _json_ld_prices(item)
    elif isinstance(data, dict):
        product_type = data.get('@type', [])
        if isinstance(product_type, str):
            product_type = [product_type]
        if any(str(value).lower() == 'product' for value in product_type):
            offers = data.get('offers', [])
            if isinstance(offers, dict):
                offers = [offers]
            for offer in offers:
                if isinstance(offer, dict):
                    for key in ('price', 'lowPrice'):
                        if key in offer:
                            yield offer[key]
        for key in ('@graph', 'mainEntity'):
            if key in data:
                yield from _json_ld_prices(data[key])


def _json_ld_product_names(data):
    if isinstance(data, list):
        for item in data:
            yield from _json_ld_product_names(item)
    elif isinstance(data, dict):
        product_type = data.get('@type', [])
        if isinstance(product_type, str):
            product_type = [product_type]
        if any(str(value).lower() == 'product' for value in product_type):
            name = data.get('name')
            if isinstance(name, str) and name.strip():
                yield name.strip()
        for key in ('@graph', 'mainEntity'):
            if key in data:
                yield from _json_ld_product_names(data[key])


def _product_name_from_url(product_url):
    path_parts = [part for part in urlsplit(product_url).path.split('/') if part]
    if 'dp' in path_parts:
        product_slug = path_parts[path_parts.index('dp') - 1]
    elif path_parts:
        product_slug = path_parts[-1]
    else:
        product_slug = urlsplit(product_url).hostname or 'Website product'
    name = unquote(product_slug).replace('-', ' ').replace('_', ' ').strip()
    return name[:100] or 'Website product'


def _extract_product_details(page, product_url):
    parser = _PriceHTMLParser()
    try:
        parser.feed(page)
    except (TypeError, ValueError) as exc:
        raise PriceLookupError('The product page contains invalid price data.') from exc

    candidates = []
    product_names = []
    for block in parser.json_ld:
        try:
            data = json.loads(block)
            candidates.extend(_json_ld_prices(data))
            product_names.extend(_json_ld_product_names(data))
        except (json.JSONDecodeError, TypeError):
            continue

    candidates.extend(parser.meta_prices)
    candidates.extend(parser.itemprop_prices)
    candidates.extend(parser.offscreen_prices)
    candidates.extend(parser.data_prices)
    product_name = (
        next(iter(product_names), None)
        or next(iter(parser.meta_titles), None)
        or ''.join(parser.title_parts).strip()
        or _product_name_from_url(product_url)
    )
    for candidate in candidates:
        price = _number_from_value(candidate)
        if price is not None:
            return product_name[:100], price

    raise PriceLookupError(
        'Could not find a product price on that page. '
        'The page must publish its price in structured product data.'
    )


def fetch_product_details(product_url):
    _validate_public_url(product_url)
    request = Request(
        product_url,
        headers={
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/131.0.0.0 Safari/537.36'
            ),
            'Accept': (
                'text/html,application/xhtml+xml,application/xml;q=0.9,'
                'image/avif,image/webp,*/*;q=0.8'
            ),
            'Accept-Language': 'en-IN,en;q=0.9',
            'Accept-Encoding': 'identity',
            'Connection': 'close',
        },
    )
    opener = build_opener(_SafeRedirectHandler())
    try:
        with opener.open(request, timeout=REQUEST_TIMEOUT) as response:
            content_type = response.headers.get('Content-Type', '')
            if 'html' not in content_type.lower():
                raise PriceLookupError(
                    'The product URL did not return an HTML product page.'
                )
            page = response.read(MAX_PAGE_SIZE + 1)
    except PriceLookupError:
        raise
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        if isinstance(exc, HTTPError) and exc.code in (401, 403, 429):
            raise PriceLookupError(
                'This website is blocking automatic price checks. '
                'Try again later or use a product page that is publicly accessible.'
            ) from exc
        raise PriceLookupError(
            'Could not fetch the product page. Check the URL and try again.'
        ) from exc

    if len(page) > MAX_PAGE_SIZE:
        raise PriceLookupError('The product page is too large to inspect.')

    return _extract_product_details(
        page.decode('utf-8', errors='replace'),
        product_url,
    )


def fetch_product_price(product_url):
    return fetch_product_details(product_url)[1]


def _extract_product_price(page):
    return _extract_product_details(page, 'https://example.com/product')[1]

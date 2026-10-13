from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

from .models import CompetitorPrice, Product
from .price_scraper import (
    PriceLookupError,
    _extract_product_details,
    _extract_product_price,
)


class ProductAndPageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='page-user')
        self.product = Product.objects.create(
            owner=self.user,
            name='Test product',
            current_price=12.0,
            stock_quantity=8,
        )

    def test_core_pages_render(self):
        self.client.force_login(self.user)
        paths = [
            reverse('home'),
            reverse('product_list'),
            reverse('add_product'),
            reverse('add_product_from_url'),
            reverse('edit_product', args=[self.product.pk]),
            reverse('delete_product', args=[self.product.pk]),
            reverse('product_detail', args=[self.product.pk]),
            reverse('compare_prices', args=[self.product.pk]),
            reverse('add_competitor_price', args=[self.product.pk]),
            reverse(
                'edit_competitor_price',
                args=[
                    CompetitorPrice.objects.create(
                        product=self.product,
                        website_name='Test shop',
                    ).pk,
                ],
            ),
            reverse(
                'delete_competitor_price',
                args=[
                    CompetitorPrice.objects.create(
                        product=self.product,
                        website_name='Another shop',
                    ).pk,
                ],
            ),
            reverse('demand_analysis', args=[self.product.pk]),
            reverse('pricing_recommendation', args=[self.product.pk]),
            reverse('dashboard'),
        ]

        for path in paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertContains(
                    response,
                    'aria-label="Go back to the previous page"',
                )

    def test_pricing_comparison_url_redirects_to_website_comparison(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('pricing_comparison', args=[self.product.pk])
        )

        self.assertRedirects(
            response,
            reverse('compare_prices', args=[self.product.pk]),
        )

    @patch(
        'pricing_app.views.fetch_product_details',
        return_value=('Fastrack Striker Watch', 1299.0),
    )
    def test_create_product_from_amazon_url_adds_offer_and_initial_target(
        self, fetch_details
    ):
        self.client.force_login(self.user)
        amazon_url = (
            'https://www.amazon.in/Fastrack-Striker-Stainless-Material-'
            'Watches/dp/B0FLV5BLKN?th=1'
        )
        form_response = self.client.get(reverse('add_product_from_url'))
        self.assertContains(form_response, amazon_url)

        response = self.client.post(
            reverse('add_product_from_url'),
            {'product_url': amazon_url},
        )

        product = Product.objects.get(owner=self.user, name='Fastrack Striker Watch')
        offer = CompetitorPrice.objects.get(product=product)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse('compare_prices', args=[product.pk]),
        )
        self.assertEqual(product.target_buying_price, 1299.0)
        self.assertEqual(product.current_price, 1299.0)
        self.assertEqual(offer.website_name, 'Amazon.in')
        self.assertEqual(offer.competitor_price, 1299.0)
        self.assertEqual(offer.product_url, amazon_url)
        fetch_details.assert_called_once_with(amazon_url)

    def test_add_product_page_links_to_create_from_url_flow(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('add_product'))

        self.assertContains(response, 'Create a product from an Amazon URL')
        self.assertContains(response, reverse('add_product_from_url'))

    def test_market_analysis_uses_competitor_offers_not_inventory(self):
        self.client.force_login(self.user)
        self.product.target_buying_price = 10.0
        self.product.save(update_fields=['target_buying_price'])
        CompetitorPrice.objects.create(
            product=self.product,
            website_name='Market Shop',
            competitor_price=8.5,
        )

        response = self.client.get(
            reverse('demand_analysis', args=[self.product.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Market Price Analysis')
        self.assertContains(response, 'Market Shop')
        self.assertContains(response, 'Meets target')
        self.assertNotContains(response, 'Available Stock')
        self.assertNotContains(response, 'Current Price')

    def test_price_recommendation_uses_lowest_website_offer(self):
        self.client.force_login(self.user)
        self.product.target_buying_price = 10.0
        self.product.save(update_fields=['target_buying_price'])
        CompetitorPrice.objects.create(
            product=self.product,
            website_name='Higher Shop',
            competitor_price=12.0,
        )
        CompetitorPrice.objects.create(
            product=self.product,
            website_name='Best Shop',
            competitor_price=9.5,
            product_url='https://example.com/best',
        )

        response = self.client.get(
            reverse('pricing_recommendation', args=[self.product.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lowest Website Offer')
        self.assertContains(response, 'Best Shop')
        self.assertContains(response, '₹9.50')
        self.assertContains(response, 'Visit Lowest-Priced Website')
        self.assertNotContains(response, 'Available stock')
        self.assertNotContains(response, 'Current Price')

    def test_product_detail_shows_requested_price_actions(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('product_detail', args=[self.product.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertContains(response, 'Compare Prices')
        self.assertContains(response, 'Get Price Recommendations')
        self.assertContains(
            response,
            reverse('compare_prices', args=[self.product.pk]),
        )
        self.assertContains(
            response,
            reverse('pricing_recommendation', args=[self.product.pk]),
        )

    def test_dashboard_has_no_sales_links(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Target Buying Price')
        self.assertContains(response, 'Website Offers')
        self.assertContains(
            response,
            reverse('product_detail', args=[self.product.pk]),
        )
        self.assertNotContains(response, 'Current Price')
        self.assertNotContains(response, 'Available Stock')
        self.assertNotContains(response, 'sales_history')
        self.assertNotContains(response, 'sales_entry')
        self.assertNotContains(response, 'Sales')

    def test_homepage_has_no_sales_links(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'sales_history')
        self.assertNotContains(response, 'sales_chart')
        self.assertNotContains(response, 'Sales Chart')

    def test_product_list_has_matching_headers_and_product_actions(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('product_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Product Name')
        self.assertContains(response, 'Target Buying Price')
        self.assertContains(response, 'Actions')
        self.assertContains(
            response,
            reverse('product_detail', args=[self.product.pk]),
        )
        self.assertContains(response, reverse('edit_product', args=[self.product.pk]))
        self.assertContains(response, reverse('delete_product', args=[self.product.pk]))
        self.assertNotContains(response, 'Lowest Website Price')
        self.assertNotContains(response, 'Stock Quantity')
        self.assertNotContains(response, 'Compare Prices')

    def test_price_comparison_identifies_lowest_website_offer(self):
        self.client.force_login(self.user)
        CompetitorPrice.objects.create(
            product=self.product,
            website_name='Higher Shop',
            competitor_price=20.0,
        )
        lowest = CompetitorPrice.objects.create(
            product=self.product,
            website_name='Lowest Shop',
            competitor_price=8.25,
            product_url='https://example.com/product',
        )

        response = self.client.get(
            reverse('compare_prices', args=[self.product.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['best_offer'], lowest)
        self.assertContains(response, 'Lowest Shop')
        self.assertContains(response, '₹8.25')
        self.assertContains(response, 'Lowest')

    def test_price_comparison_table_shows_target_and_difference(self):
        self.client.force_login(self.user)
        self.product.target_buying_price = 10.0
        self.product.save(update_fields=['target_buying_price'])
        CompetitorPrice.objects.create(
            product=self.product,
            website_name='Above Target Shop',
            competitor_price=12.5,
        )

        response = self.client.get(
            reverse('compare_prices', args=[self.product.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Product Name')
        self.assertContains(response, 'Website Name')
        self.assertContains(response, 'Fetched Price')
        self.assertContains(response, 'Target Buying Price')
        self.assertContains(response, 'Difference')
        self.assertContains(response, '₹10.00')
        self.assertContains(response, '₹2.50 above target')

    @patch('pricing_app.views.fetch_product_price', return_value=10.75)
    def test_adding_competitor_url_fetches_price_and_returns_to_comparison(self, fetch_price):
        self.client.force_login(self.user)
        self.product.target_buying_price = 10.0
        self.product.save(update_fields=['target_buying_price'])

        form_response = self.client.get(
            reverse('add_competitor_price', args=[self.product.pk])
        )
        self.assertContains(form_response, 'Product URL')
        self.assertNotContains(form_response, 'name="competitor_price"')
        self.assertContains(
            form_response,
            'Checked at will be set automatically when you save.',
        )

        response = self.client.post(
            reverse('add_competitor_price', args=[self.product.pk]),
            {
                'product': self.product.pk,
                'website_name': 'Example Shop',
                'product_url': 'https://example.com/product',
            },
        )

        self.assertRedirects(
            response,
            reverse('compare_prices', args=[self.product.pk]),
        )
        offer = CompetitorPrice.objects.get(product=self.product)
        self.assertEqual(offer.competitor_price, 10.75)
        fetch_price.assert_called_once_with('https://example.com/product')

        comparison_response = self.client.get(
            reverse('compare_prices', args=[self.product.pk])
        )
        self.assertContains(comparison_response, 'Example Shop')
        self.assertContains(comparison_response, '₹10.75')
        self.assertContains(comparison_response, '₹0.75 above target')

    @patch('pricing_app.views.fetch_product_price', return_value=899.0)
    def test_competitor_listing_derives_website_name_and_accepts_long_url(
        self, fetch_price
    ):
        self.client.force_login(self.user)
        long_url = (
            'https://www.amazon.in/product/dp/B0FLV5BLKN?'
            + '&'.join('tracking{}={}'.format(index, 'x' * 50)
                      for index in range(6))
        )

        response = self.client.post(
            reverse('add_competitor_price', args=[self.product.pk]),
            {
                'product': self.product.pk,
                'website_name': '',
                'product_url': long_url,
            },
        )

        self.assertRedirects(
            response,
            reverse('compare_prices', args=[self.product.pk]),
        )
        listing = CompetitorPrice.objects.get(product=self.product)
        self.assertEqual(listing.website_name, 'amazon.in')
        self.assertEqual(listing.product_url, long_url)
        self.assertEqual(listing.competitor_price, 899.0)
        fetch_price.assert_called_once_with(long_url)

    @patch('pricing_app.views.fetch_product_price', return_value=11.25)
    def test_edit_competitor_url_refreshes_price(self, fetch_price):
        self.client.force_login(self.user)
        listing = CompetitorPrice.objects.create(
            product=self.product,
            website_name='Example Shop',
            competitor_price=10.75,
            product_url='https://example.com/product',
        )

        response = self.client.get(
            reverse('edit_competitor_price', args=[listing.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Product URL')
        self.assertNotContains(response, 'name="competitor_price"')
        self.assertContains(response, 'Last checked:')
        self.assertNotContains(response, 'name="checked_at"')

        response = self.client.post(
            reverse('edit_competitor_price', args=[listing.pk]),
            {
                'product': self.product.pk,
                'website_name': 'Example Shop',
                'product_url': 'https://example.com/product',
            },
        )

        self.assertRedirects(
            response,
            reverse('compare_prices', args=[self.product.pk]),
        )
        listing.refresh_from_db()
        self.assertEqual(listing.competitor_price, 11.25)
        fetch_price.assert_called_once_with('https://example.com/product')

    @patch(
        'pricing_app.views.fetch_product_price',
        side_effect=PriceLookupError('Could not find a product price.'),
    )
    def test_failed_price_fetch_shows_error_and_does_not_save(self, fetch_price):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('add_competitor_price', args=[self.product.pk]),
            {
                'product': self.product.pk,
                'website_name': 'Example Shop',
                'product_url': 'https://example.com/product',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Could not find a product price.')
        self.assertFalse(CompetitorPrice.objects.filter(product=self.product).exists())
        fetch_price.assert_called_once_with('https://example.com/product')

    def test_price_scraper_reads_structured_product_price(self):
        page = '''
            <script type="application/ld+json">
            {"@type":"Product","offers":{"price":"₹1,299.50"}}
            </script>
        '''

        self.assertEqual(_extract_product_price(page), 1299.5)

    def test_price_scraper_reads_product_name_and_price(self):
        page = '''
            <script type="application/ld+json">
            {"@type":"Product","name":"Fastrack Striker Watch",
             "offers":{"price":"1299.50"}}
            </script>
        '''

        self.assertEqual(
            _extract_product_details(
                page,
                'https://www.amazon.in/Fastrack-Striker/dp/B0FLV5BLKN',
            ),
            ('Fastrack Striker Watch', 1299.5),
        )

    def test_price_scraper_reads_meta_price_and_rejects_missing_price(self):
        self.assertEqual(
            _extract_product_price(
                '<meta property="product:price:amount" content="1,299">'
            ),
            1299.0,
        )
        with self.assertRaises(PriceLookupError):
            _extract_product_price('<html><body>No price here</body></html>')

    def test_price_scraper_reads_amazon_offscreen_price(self):
        self.assertEqual(
            _extract_product_price(
                '<span class="a-price"><span class="a-offscreen">₹1,299</span></span>'
            ),
            1299.0,
        )

    def test_price_scraper_reads_generic_data_price(self):
        self.assertEqual(
            _extract_product_price(
                '<div data-price="₹2,499.00">Price</div>'
            ),
            2499.0,
        )

    def test_target_buying_price_is_saved_and_compared_with_lowest_offer(self):
        self.client.force_login(self.user)
        original_reference_price = self.product.current_price
        original_stock_quantity = self.product.stock_quantity

        edit_response = self.client.get(
            reverse('edit_product', args=[self.product.pk])
        )
        self.assertNotContains(edit_response, 'Reference Price')
        self.assertNotContains(edit_response, 'Stock Quantity')

        response = self.client.post(
            reverse('edit_product', args=[self.product.pk]),
            {
                'name': self.product.name,
                'target_buying_price': '10.0',
            },
        )
        self.assertRedirects(
            response,
            reverse('product_detail', args=[self.product.pk]),
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.target_buying_price, 10.0)
        self.assertEqual(self.product.current_price, original_reference_price)
        self.assertEqual(self.product.stock_quantity, original_stock_quantity)

        CompetitorPrice.objects.create(
            product=self.product,
            website_name='Target Shop',
            competitor_price=9.5,
        )
        response = self.client.get(
            reverse('compare_prices', args=[self.product.pk])
        )
        self.assertContains(response, 'Your Target Buying Price')
        self.assertContains(response, 'At or below your target')

        response = self.client.get(reverse('product_list'))
        self.assertContains(response, 'Target Buying Price')

    def test_adding_product_uses_target_as_reference_and_starts_with_zero_stock(self):
        self.client.force_login(self.user)
        form_response = self.client.get(reverse('add_product'))
        self.assertContains(form_response, 'Product Name')
        self.assertContains(form_response, 'Target Buying Price')
        self.assertContains(
            form_response,
            reverse('product_list'),
        )
        self.assertNotContains(form_response, 'Stock Quantity')
        self.assertNotContains(form_response, 'Reference Price')

        response = self.client.post(
            reverse('add_product'),
            {
                'name': 'New product',
                'target_buying_price': '24.50',
            },
        )

        product = Product.objects.get(name='New product')
        self.assertRedirects(response, reverse('product_list'))
        self.assertEqual(product.target_buying_price, 24.5)
        self.assertEqual(product.current_price, 24.5)
        self.assertEqual(product.stock_quantity, 0)

    def test_edit_product_back_link_targets_product_details(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('edit_product', args=[self.product.pk])
        )

        self.assertContains(
            response,
            reverse('product_detail', args=[self.product.pk]),
        )
        self.assertContains(response, 'Back to Product Details')

    def test_adding_product_requires_target_buying_price(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('add_product'),
            {'name': 'Product without target'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Product.objects.filter(name='Product without target').exists())
        self.assertContains(response, 'This field is required.')

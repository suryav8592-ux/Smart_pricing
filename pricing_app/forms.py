import math
from urllib.parse import urlsplit

from django import forms

from .models import CompetitorPrice, Product


class ProductForm(forms.ModelForm):
    target_buying_price = forms.FloatField(
        min_value=0.01,
        required=False,
        label='Target buying price (₹)',
    )

    class Meta:
        model = Product
        fields = (
            'name',
            'target_buying_price',
        )

    def __init__(self, *args, **kwargs):
        adding = kwargs.pop('adding', False)
        super().__init__(*args, **kwargs)
        if adding:
            self.fields['target_buying_price'].required = True

    def clean_target_buying_price(self):
        price = self.cleaned_data['target_buying_price']
        if price is not None and not math.isfinite(price):
            raise forms.ValidationError('Enter a valid positive target price.')
        return price


class ProductURLForm(forms.Form):
    product_url = forms.URLField(
        max_length=2048,
        label='Amazon product URL',
        help_text=(
            'The product name and current price are fetched from this page. '
            'The fetched price is used as the initial target buying price.'
        ),
    )

    def __init__(self, *args, **kwargs):
        super(ProductURLForm, self).__init__(*args, **kwargs)
        self.fields['product_url'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'https://www.amazon.in/product/dp/...',
        })


class CompetitorPriceForm(forms.ModelForm):
    product_url = forms.URLField(max_length=2048, required=True)

    class Meta:
        model = CompetitorPrice
        fields = (
            'product',
            'website_name',
            'product_url',
        )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(CompetitorPriceForm, self).__init__(*args, **kwargs)
        if user is not None:
            self.fields['product'].queryset = Product.objects.filter(
                owner=user
            ).order_by('name')
        self.fields['website_name'].widget.attrs['placeholder'] = (
            'Filled automatically from the product URL'
        )
        self.fields['website_name'].required = False
        self.fields['website_name'].help_text = (
            'We will use the website name from the product URL if left blank.'
        )
        self.fields['product_url'].required = True
        self.fields['product_url'].label = 'Product URL'
        self.fields['product_url'].help_text = (
            'The current price will be fetched from this product page.'
        )
        self.fields['product_url'].widget.attrs['placeholder'] = (
            'https://example.com/product'
        )
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super(CompetitorPriceForm, self).clean()
        website_name = cleaned_data.get('website_name')
        product_url = cleaned_data.get('product_url')
        if not website_name and product_url:
            hostname = urlsplit(product_url).hostname
            if hostname:
                website_name = hostname.lower()
                if website_name.startswith('www.'):
                    website_name = website_name[4:]
                cleaned_data['website_name'] = website_name[:100]
        return cleaned_data

from django.contrib import admin
from .models import Product, PriceOffer


class PriceOfferInline(admin.TabularInline):
    model = PriceOffer
    extra = 1
    readonly_fields = ('last_updated',)
    fields = ('platform_name', 'price', 'platform_image', 'product_url', 'availability', 'last_updated')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'brand', 'model_name', 'category', 'created_at', 'updated_at')
    search_fields = ('name', 'brand', 'model_name', 'category')
    list_filter = ('brand', 'category', 'created_at')
    inlines = [PriceOfferInline]


@admin.register(PriceOffer)
class PriceOfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'platform_name', 'price', 'availability', 'last_updated')
    search_fields = ('product__name', 'product__model_name', 'product__brand', 'platform_name')
    list_filter = ('platform_name', 'availability', 'last_updated')

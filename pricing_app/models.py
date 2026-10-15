from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=200, help_text="e.g. AirPods, iPhone, Galaxy Watch")
    brand = models.CharField(max_length=100, help_text="e.g. Apple, Samsung, Sony")
    model_name = models.CharField(max_length=150, help_text="e.g. Pro 2nd Gen, S24 Ultra, WH-1000XM5")
    category = models.CharField(max_length=100, blank=True, help_text="e.g. Electronics, Audio, Wearables")
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name', 'model_name']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return f"{self.brand} {self.name} - {self.model_name}"

    @property
    def lowest_offer(self):
        """Returns the lowest price offer among available offers or any offer."""
        available = self.offers.filter(availability__iexact='Available').order_by('price').first()
        if available:
            return available
        return self.offers.order_by('price').first()


class PriceOffer(models.Model):
    AVAILABILITY_CHOICES = [
        ('Available', 'Available'),
        ('Out of Stock', 'Out of Stock'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='offers')
    platform_name = models.CharField(max_length=100, help_text="Retailer name: Amazon, Flipkart, Croma, etc.")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in Indian Rupees (INR)")
    platform_image = models.ImageField(upload_to='platforms/', blank=True, null=True, help_text="Optional retailer logo")
    product_url = models.URLField(max_length=500, help_text="Direct link to buy product on retailer website")
    availability = models.CharField(max_length=50, choices=AVAILABILITY_CHOICES, default='Available')
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['price']
        verbose_name = 'Price Offer'
        verbose_name_plural = 'Price Offers'

    def __str__(self):
        return f"{self.platform_name} - ₹{self.price} for {self.product.name} ({self.product.model_name})"

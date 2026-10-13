from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Product(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='products',
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)
    current_price = models.FloatField()
    target_buying_price = models.FloatField(null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class CompetitorPrice(models.Model):

    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='competitor_prices')
    website_name = models.CharField(max_length=100)
    competitor_price = models.FloatField(null=True, blank=True)
    product_url = models.URLField(blank=True, max_length=2048)
    checked_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.product.name} - {self.website_name}"


class QValue(models.Model):
    state_key = models.CharField(max_length=100)
    action = models.CharField(max_length=20)
    value = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['state_key', 'action'],
                name='unique_qvalue_state_action'
            )
        ]

    def __str__(self):
        return f"{self.state_key} - {self.action}: {self.value}"
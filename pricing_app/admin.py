from django.contrib import admin
from .models import Product, CompetitorPrice, QValue

# Register your models here.

admin.site.register(Product)
admin.site.register(CompetitorPrice)
admin.site.register(QValue)
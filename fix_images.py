import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dynamic_pricing.settings')
django.setup()

from pricing_app.models import Product, PriceOffer

# Assign placeholder images where fields are empty
for p in Product.objects.all():
    if not p.image:
        p.image.name = 'products/sample.png'
        p.save(update_fields=['image'])
        print(f'Set image for product {p.id}')

for o in PriceOffer.objects.all():
    if not o.platform_image:
        o.platform_image.name = 'platforms/sample.png'
        o.save(update_fields=['platform_image'])
        print(f'Set platform image for offer {o.id}')

print('All missing image fields have been updated.')

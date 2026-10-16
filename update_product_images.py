import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dynamic_pricing.settings')
django.setup()

from pricing_app.models import Product

# Mapping of product identifiers (name or part) -> image filename in media/products
image_map = {
    'AirPods Pro': 'airpods_pro.jpg',
    'AirPods Max': 'airpods_max.jpg',
    'AirPods': 'airpods_2.jpg',
    'Apple Watch Series 9': 'apple_watch_9.jpg',
    'Apple Watch Ultra 2': 'apple_watch_ultra2.jpg',
    'Bravia 55-inch': 'sony_bravia_55.jpg',
    'Dell XPS 13 Plus': 'dell_xps13.jpg',
    'Galaxy S24 Ultra': 'galaxy_s24_ultra.jpg',
    'Galaxy S24': 'galaxy_s24.jpg',
    'Galaxy Tab S9': 'galaxy_tab_s9.jpg',
    'Galaxy Watch 6': 'galaxy_watch6.jpg',
    'Galaxy Z Fold 5': 'galaxy_z_fold5.jpg',
    'MacBook Air M2': 'macbook_air_m2.jpg',
    'MacBook Pro M3': 'macbook_pro_m3.jpg',
    'Nintendo Switch': 'nintendo_switch.jpg',
    'OnePlus 12': 'oneplus_12.jpg',
    'Pixel 8 Pro': 'pixel_8_pro.jpg',
    'PlayStation 5': 'ps5_slim.jpg',
    'QuietComfort 45': 'bose_qc45.jpg',
    'ROG Zephyrus G14': 'asus_rog_g14.jpg',
    'WH-1000XM5': 'sony_wh1000xm5.jpg',
    'iPad Air M2': 'ipad_air_m2.jpg',
    'iPhone 14': 'iphone_14.jpg',
    'iPhone 15': 'iphone_15.jpg',
    'iPhone 15 Pro Max': 'iphone_15_pro_max.jpg',
    # fallback for any others – keep existing placeholder
}

for product in Product.objects.all():
    # Find a matching key in the map (exact or startswith)
    matched = None
    for key, filename in image_map.items():
        if product.name == key or product.name.startswith(key) or product.brand + ' ' + product.name == key:
            matched = filename
            break
    if matched:
        old = product.image.name
        product.image.name = f'products/{matched}'
        product.save(update_fields=['image'])
        print(f'Updated product {product.id} ({product.name}) image: {old} -> {product.image.name}')
    else:
        print(f'No specific image for product {product.id} ({product.name}); left as {product.image.name}')

print('✅ Image fields updated.')

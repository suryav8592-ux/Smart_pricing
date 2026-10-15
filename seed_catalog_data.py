import os
import django
import urllib.parse
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dynamic_pricing.settings')
django.setup()

from pricing_app.models import Product, PriceOffer
from django.contrib.auth.models import User

# Ensure Superuser exists and has known credentials
admin_user = User.objects.filter(username='admin').first()
if not admin_user:
    admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Created superuser 'admin' with password 'admin123'")
else:
    admin_user.set_password('admin123')
    admin_user.is_superuser = True
    admin_user.is_staff = True
    admin_user.save()

# Ensure customer account
cust_user = User.objects.filter(username='customer').first()
if not cust_user:
    cust_user = User.objects.create_user('customer', 'customer@example.com', 'customer123')
    print("Created demo customer 'customer' with password 'customer123'")
else:
    cust_user.set_password('customer123')
    cust_user.save()

# Clear existing records
PriceOffer.objects.all().delete()
Product.objects.all().delete()
print("Cleared old product and offer records.")

def make_store_url(platform, query):
    """Generate exact search / product landing URL for top stores."""
    q_encoded = urllib.parse.quote_plus(query)
    q_slug = urllib.parse.quote_plus(query).replace('+', '-')
    
    if 'Amazon' in platform:
        return f"https://www.amazon.in/s?k={q_encoded}"
    elif 'Flipkart' in platform:
        return f"https://www.flipkart.com/search?q={q_encoded}"
    elif 'Croma' in platform:
        return f"https://www.croma.com/searchB?q={q_encoded}"
    elif 'Reliance Digital' in platform:
        return f"https://www.reliancedigital.in/search?q={q_encoded}"
    elif 'Vijay Sales' in platform:
        return f"https://www.vijaysales.com/search/{q_slug}"
    elif 'Sony' in platform:
        return f"https://shopatsc.com/search?q={q_encoded}"
    elif 'Samsung' in platform:
        return f"https://www.samsung.com/in/search/?searchvalue={q_encoded}"
    elif 'OnePlus' in platform:
        return f"https://www.oneplus.in/search?q={q_encoded}"
    elif 'Dell' in platform:
        return f"https://www.dell.com/en-in/search/{q_encoded}"
    elif 'ASUS' in platform:
        return f"https://in.store.asus.com/catalogsearch/result/?q={q_encoded}"
    elif 'Mx2Games' in platform:
        return f"https://mx2games.com/?s={q_encoded}&post_type=product"
    return f"https://www.google.com/search?q={q_encoded}"

products_data = [
    # ------------------ AUDIO: AIRPODS ------------------
    {
        'name': 'AirPods',
        'brand': 'Apple',
        'model_name': 'AirPods 2nd Gen',
        'category': 'Audio',
        'description': 'Apple AirPods (2nd Generation) with Lightning Charging case. Effortless setup, in-ear detection, and quick switching between devices. Up to 24 hours of total listening time.',
        'search_term': 'Apple AirPods 2nd Generation with Charging Case',
        'offers': [
            {'platform_name': 'Amazon India', 'price': Decimal('10999.00'), 'availability': 'Available'},
            {'platform_name': 'Flipkart', 'price': Decimal('11499.00'), 'availability': 'Available'},
            {'platform_name': 'Croma', 'price': Decimal('11990.00'), 'availability': 'Available'},
            {'platform_name': 'Reliance Digital', 'price': Decimal('12900.00'), 'availability': 'Available'},
        ]
    },
    {
        'name': 'AirPods',
        'brand': 'Apple',
        'model_name': 'AirPods 3rd Gen',
        'category': 'Audio',
        'description': 'Apple AirPods (3rd Generation) with Lightning Charging Case, Personalized Spatial Audio with dynamic head tracking, sweat and water resistance (IPX4), and up to 30 hours of total listening time.',
        'search_term': 'Apple AirPods 3rd Generation',
        'offers': [
            {'platform_name': 'Amazon India', 'price': Decimal('17499.00'), 'availability': 'Available'},
            {'platform_name': 'Flipkart', 'price': Decimal('17999.00'), 'availability': 'Available'},
            {'platform_name': 'Croma', 'price': Decimal('18490.00'), 'availability': 'Available'},
            {'platform_name': 'Reliance Digital', 'price': Decimal('18900.00'), 'availability': 'Available'},
        ]
    },
    {
        'name': 'AirPods Pro',
        'brand': 'Apple',
        'model_name': 'Pro 2nd Gen (USB-C)',
        'category': 'Audio',
        'description': 'Apple AirPods Pro (2nd Generation) with MagSafe Case (USB-C). Features the H2 headphone chip, up to 2x more Active Noise Cancellation, Adaptive Audio, and Transparency mode.',
        'search_term': 'Apple AirPods Pro 2nd Gen USB C',
        'offers': [
            {'platform_name': 'Amazon India', 'price': Decimal('21990.00'), 'availability': 'Available'},
            {'platform_name': 'Flipkart', 'price': Decimal('22490.00'), 'availability': 'Available'},
            {'platform_name': 'Vijay Sales', 'price': Decimal('22990.00'), 'availability': 'Available'},
            {'platform_name': 'Croma', 'price': Decimal('23990.00'), 'availability': 'Available'},
            {'platform_name': 'Reliance Digital', 'price': Decimal('24900.00'), 'availability': 'Available'},
        ]
    },
    {
        'name': 'AirPods Max',
        'brand': 'Apple',
        'model_name': 'Wireless Over-Ear Space Gray',
        'category': 'Audio',
        'description': 'Apple-designed dynamic driver provides high-fidelity audio. Active Noise Cancellation blocks outside noise, while Transparency mode lets you hear and interact with the world around you.',
        'search_term': 'Apple AirPods Max Space Gray',
        'offers': [
            {'platform_name': 'Amazon India', 'price': Decimal('54990.00'), 'availability': 'Available'},
            {'platform_name': 'Croma', 'price': Decimal('56900.00'), 'availability': 'Available'},
            {'platform_name': 'Flipkart', 'price': Decimal('58990.00'), 'availability': 'Out of Stock'},
        ]
    },

    # ------------------ SMARTPHONES ------------------
    {
        'name': 'iPhone 15',
        'brand': 'Apple',
        'model_name': '128GB Black',
        'category': 'Smartphones',
        'description': 'Dynamic Island bubbles up alerts and Live Activities. 48MP Main camera with 2x Telephoto. Durable color-infused glass and aluminum design. USB-C with universal charging.',
        'search_term': 'Apple iPhone 15 128GB Black',
        'offers': [
            {'platform_name': 'Flipkart', 'price': Decimal('64999.00'), 'availability': 'Available'},
            {'platform_name': 'Amazon India', 'price': Decimal('65499.00'), 'availability': 'Available'},
            {'platform_name': 'Croma', 'price': Decimal('67900.00'), 'availability': 'Available'},
            {'platform_name': 'Reliance Digital', 'price': Decimal('68900.00'), 'availability': 'Available'},
        ]
    },
    {
        'name': 'iPhone 15 Pro Max',
        'brand': 'Apple',
        'model_name': '256GB Natural Titanium',
        'category': 'Smartphones',
        'description': 'Forged in titanium with lightweight aerospace-grade design. A17 Pro game-changing chip. 5x Telephoto optical zoom and customizable Action button.',
        'search_term': 'Apple iPhone 15 Pro Max 256GB Natural Titanium',
        'offers': [
            {'platform_name': 'Amazon India', 'price': Decimal('149900.00'), 'availability': 'Available'},
            {'platform_name': 'Flipkart', 'price': Decimal('151900.00'), 'availability': 'Available'},
            {'platform_name': 'Croma', 'price': Decimal('154900.00'), 'availability': 'Available'},
            {'platform_name': 'Vijay Sales', 'price': Decimal('152900.00'), 'availability': 'Available'},
        ]
    },
    {
        'name': 'iPhone 14',
        'brand': 'Apple',
        'model_name': '128GB Blue',
        'category': 'Smartphones',
        'description': '6.1-inch Super Retina XDR display, advanced dual-camera system, Action mode for smooth handheld videos, and all-day battery life.',
        'search_term': 'Apple iPhone 14 128GB Blue',
        'offers': [
            {'platform_name': 'Flipkart', 'price': Decimal('54999.00'), 'availability': 'Available'},
            {'platform_name': 'Amazon India', 'price': Decimal('55999.00'), 'availability': 'Available'},
            {'platform_name': 'Croma', 'price': Decimal('57900.00'), 'availability': 'Available'},
        ]
    },
    {
        'name': 'Galaxy S24 Ultra',
        'brand': 'Samsung',
        'model_name': '512GB Titanium Gray',
        'category': 'Smartphones',
        'description': 'Samsung Galaxy S24 Ultra 5G with Galaxy AI, Circle to Search, Live Translate, Note Assist, 200MP Quad Tele System camera, titanium frame, and built-in S Pen.',
        'search_term': 'Samsung Galaxy S24 Ultra 5G 512GB',
        'offers': [
            {'platform_name': 'Amazon India', 'price': Decimal('129999.00'), 'availability': 'Available'},
            {'platform_name': 'Flipkart', 'price': Decimal('131999.00'), 'availability': 'Available'},
            {'platform_name': 'Samsung Official Store', 'price': Decimal('134999.00'), 'availability': 'Available'},
            {'platform_name': 'Croma', 'price': Decimal('133990.00'), 'availability': 'Out of Stock'},
        ]
    },
    {
        'name': 'Galaxy S24',
        'brand': 'Samsung',
        'model_name': '256GB Onyx Black',
        'category': 'Smartphones',
        'description': 'Compact powerhouse with 6.2-inch Dynamic AMOLED 2X 120Hz display, Exynos 2400 / Snapdragon 8 Gen 3, and triple camera setup.',
        'search_term': 'Samsung Galaxy S24 5G 256GB Onyx Black',
        'offers': [
            {'platform_name': 'Amazon India', 'price': Decimal('74999.00'), 'availability': 'Available'},
            {'platform_name': 'Flipkart', 'price': Decimal('75999.00'), 'availability': 'Available'},
            {'platform_name': 'Samsung Official Store', 'price': Decimal('79999.00'), 'availability': 'Available'},
        ]
    },
    {
        'name': 'Galaxy Z Fold 5',
        'brand': 'Samsung',
        'model_name': '256GB Phantom Black',
        'category': 'Smartphones',
        'description': '7.6-inch Main Screen unfolds into an immersive tablet-like experience with Flex Hinge, multitasking taskbar, and S Pen Fold Edition support.',
        'search_term': 'Samsung Galaxy Z Fold 5 5G 256GB Phantom Black',
        'offers': [
            {'platform_name': 'Amazon India', 'price': Decimal('138999.00'), 'availability': 'Available'},
            {'platform_name': 'Flipkart', 'price': Decimal('141999.00'), 'availability': 'Available'},
            {'platform_name': 'Croma', 'price': Decimal('144990.00'), 'availability': 'Available'},
        ]
    },
    {
        'name': 'Pixel 8 Pro',
        'brand': 'Google',
        'model_name': '128GB Obsidian',
        'category': 'Smartphones',
        'description': 'Google Tensor G3 chip, best-in-class computational photography, Super Actua display, Pro camera controls, and 7 years of OS updates.',
        'search_term': 'Google Pixel 8 Pro 128GB Obsidian',
        'offers': [
            {'platform_name': 'Flipkart', 'price': Decimal('97999.00'), 'availability': 'Available'},
            {'platform_name': 'Croma', 'price': Decimal('99990.00'), 'availability': 'Available'},
            {'platform_name': 'Amazon India', 'price': Decimal('102499.00'), 'availability': 'Out of Stock'},
        ]
    },
    {
        'name': 'OnePlus 12',
        'brand': 'OnePlus',
        'model_name': '512GB Silky Black',
        'category': 'Smartphones',
        'description': 'Powered by Snapdragon 8 Gen 3, 16GB LPDDR5X RAM, 4th Gen Hasselblad Camera for Mobile, and 100W SUPERVOOC ultra-fast charging.',
        'search_term': 'OnePlus 12 5G 512GB Silky Black',
        'offers': [
            {'platform_name': 'Amazon India', 'price': Decimal('64999.00'), 'availability': 'Available'},
            {'platform_name': 'OnePlus Official Store', 'price': Decimal('64999.00'), 'availability': 'Available'},
            {'platform_name': 'Croma', 'price': Decimal('66990.00'), 'availability': 'Available'},
            {'platform_name': 'Reliance Digital', 'price': Decimal('67990.00'), 'availability': 'Available'},
        ]
    },

    # ------------------ LAPTOPS ------------------
    {
        'name': 'MacBook Air M2',
        'brand': 'Apple',
        'model_name': '13.6-inch 8GB/256GB Starlight',
        'category': 'Laptops',
        'description': 'Redesigned around the next-generation M2 chip, MacBook Air is strikingly thin and brings exceptional speed and power efficiency within its durable all-aluminum enclosure.',
        'search_term': 'Apple MacBook Air M2 13.6 inch 8GB 256GB',
        'offers': [
            {'platform_name': 'Amazon India', 'price': Decimal('89990.00'), 'availability': 'Available'},
            {'platform_name': 'Flipkart', 'price': Decimal('91990.00'), 'availability': 'Available'},
            {'platform_name': 'Croma', 'price': Decimal('93900.00'), 'availability': 'Available'},
            {'platform_name': 'Reliance Digital', 'price': Decimal('94900.00'), 'availability': 'Available'},
        ]
    },
    {
        'name': 'MacBook Pro M3',
        'brand': 'Apple',
        'model_name': '14-inch 18GB/512GB Space Black',
        'category': 'Laptops',
        'description': 'With the M3 Pro chip, MacBook Pro delivers game-changing performance for demanding workflows. Liquid Retina XDR display with ProMotion 120Hz.',
        'search_term': 'Apple MacBook Pro M3 14 inch 18GB 512GB',
        'offers': [
            {'platform_name': 'Amazon India', 'price': Decimal('189900.00'), 'availability': 'Available'},
            {'platform_name': 'Flipkart', 'price': Decimal('192900.00'), 'availability': 'Available'},
            {'platform_name': 'Croma', 'price': Decimal('196900.00'), 'availability': 'Available'},
        ]
    },
    {
        'name': 'Dell XPS 13 Plus',
        'brand': 'Dell',
        'model_name': '9320 OLED Intel i7 16GB/1TB',
        'category': 'Laptops',
        'description': 'Seamless capacitive touch row, zero-lattice keyboard, and seamless glass touchpad with 3.5K OLED InfinityEdge touch screen.',
        'search_term': 'Dell XPS 13 Plus 9320 Intel Core i7 16GB 1TB OLED',
        'offers': [
            {'platform_name': 'Amazon India', 'price': Decimal('148900.00'), 'availability': 'Available'},
            {'platform_name': 'Dell Official Store', 'price': Decimal('152000.00'), 'availability': 'Available'},
            {'platform_name': 'Croma', 'price': Decimal('154990.00'), 'availability': 'Out of Stock'},
        ]
    },
    {
        'name': 'ROG Zephyrus G14',
        'brand': 'ASUS',
        'model_name': 'Ryzen 9 / RTX 4060 / 16GB / 1TB',
        'category': 'Laptops',
        'description': 'Ultraportable 14-inch gaming laptop with ROG Nebula Display 120Hz OLED, AMD Ryzen 9 8945HS, NVIDIA GeForce RTX 4060, and AniMe Matrix LED lid.',
        'search_term': 'ASUS ROG Zephyrus G14 OLED Ryzen 9 RTX 4060',
        'offers': [
            {'platform_name': 'Amazon India', 'price': Decimal('154990.00'), 'availability': 'Available'},
            {'platform_name': 'Flipkart', 'price': Decimal('156990.00'), 'availability': 'Available'},
            {'platform_name': 'ASUS ROG Store', 'price': Decimal('159990.00'), 'availability': 'Available'},
        ]
    },

    # ------------------ TABLETS ------------------
    {
        'name': 'iPad Air M2',
        'brand': 'Apple',
        'model_name': '11-inch 128GB Wi-Fi Space Gray',
        'category': 'Tablets',
        'description': 'Redesigned iPad Air powered by the M2 chip. Features a Liquid Retina display, landscape 12MP front camera with Center Stage, and Wi-Fi 6E.',
        'search_term': 'Apple iPad Air M2 11 inch 128GB WiFi',
        'offers': [
            {'platform_name': 'Amazon India', 'price': Decimal('56999.00'), 'availability': 'Available'},
            {'platform_name': 'Flipkart', 'price': Decimal('57999.00'), 'availability': 'Available'},
            {'platform_name': 'Croma', 'price': Decimal('59900.00'), 'availability': 'Available'},
        ]
    },
    {
        'name': 'Galaxy Tab S9',
        'brand': 'Samsung',
        'model_name': '11-inch 128GB Wi-Fi Beige',
        'category': 'Tablets',
        'description': 'Dynamic AMOLED 2X display with 120Hz refresh rate. IP68 water and dust resistance, Snapdragon 8 Gen 2 for Galaxy, and included S Pen.',
        'search_term': 'Samsung Galaxy Tab S9 11 inch 128GB WiFi',
        'offers': [
            {'platform_name': 'Amazon India', 'price': Decimal('62999.00'), 'availability': 'Available'},
            {'platform_name': 'Flipkart', 'price': Decimal('64499.00'), 'availability': 'Available'},
            {'platform_name': 'Samsung Official Store', 'price': Decimal('67999.00'), 'availability': 'Available'},
        ]
    },

    # ------------------ WEARABLES / SMARTWATCHES ------------------
    {
        'name': 'Apple Watch Series 9',
        'brand': 'Apple',
        'model_name': 'GPS 45mm Midnight Aluminum',
        'category': 'Wearables',
        'description': 'Powered by the S9 SiP for a super-bright display and magical new way to interact using Double Tap without touching the screen. Advanced health, safety, and activity features.',
        'search_term': 'Apple Watch Series 9 GPS 45mm Midnight',
        'offers': [
            {'platform_name': 'Amazon India', 'price': Decimal('40990.00'), 'availability': 'Available'},
            {'platform_name': 'Flipkart', 'price': Decimal('41499.00'), 'availability': 'Available'},
            {'platform_name': 'Croma', 'price': Decimal('43900.00'), 'availability': 'Available'},
        ]
    },
    {
        'name': 'Apple Watch Ultra 2',
        'brand': 'Apple',
        'model_name': 'GPS+Cellular 49mm Titanium',
        'category': 'Wearables',
        'description': 'The most rugged and capable Apple Watch. 49mm aerospace-grade titanium case, precision dual-frequency GPS, up to 36 hours of battery life, and 100m water resistance.',
        'search_term': 'Apple Watch Ultra 2 GPS Cellular 49mm Titanium',
        'offers': [
            {'platform_name': 'Amazon India', 'price': Decimal('84900.00'), 'availability': 'Available'},
            {'platform_name': 'Flipkart', 'price': Decimal('86900.00'), 'availability': 'Available'},
            {'platform_name': 'Croma', 'price': Decimal('89900.00'), 'availability': 'Available'},
        ]
    },
    {
        'name': 'Galaxy Watch 6',
        'brand': 'Samsung',
        'model_name': 'Bluetooth 44mm Graphite',
        'category': 'Wearables',
        'description': 'Samsung Galaxy Watch 6 with slimmer bezel, 20% larger screen, custom heart rate zones, sleep coaching, and Samsung BioActive sensor.',
        'search_term': 'Samsung Galaxy Watch 6 Bluetooth 44mm Graphite',
        'offers': [
            {'platform_name': 'Flipkart', 'price': Decimal('21999.00'), 'availability': 'Available'},
            {'platform_name': 'Amazon India', 'price': Decimal('22490.00'), 'availability': 'Available'},
            {'platform_name': 'Croma', 'price': Decimal('23999.00'), 'availability': 'Available'},
        ]
    },

    # ------------------ HEADPHONES & SPEAKERS ------------------
    {
        'name': 'WH-1000XM5',
        'brand': 'Sony',
        'model_name': 'Wireless Noise Canceling Black',
        'category': 'Audio',
        'description': 'Industry-leading noise cancellation optimized to your environment. Crystal clear hands-free calling with 4 beamforming microphones. Up to 30-hour battery life with quick charging.',
        'search_term': 'Sony WH-1000XM5 Wireless Noise Cancelling Headphones Black',
        'offers': [
            {'platform_name': 'Amazon India', 'price': Decimal('26990.00'), 'availability': 'Available'},
            {'platform_name': 'Flipkart', 'price': Decimal('27490.00'), 'availability': 'Available'},
            {'platform_name': 'Croma', 'price': Decimal('28990.00'), 'availability': 'Available'},
            {'platform_name': 'Sony Official Center', 'price': Decimal('29990.00'), 'availability': 'Available'},
        ]
    },
    {
        'name': 'QuietComfort 45',
        'brand': 'Bose',
        'model_name': 'Wireless Noise Cancelling Triple Black',
        'category': 'Audio',
        'description': 'Iconic quiet, comfort, and sound. TriPort acoustic architecture offers depth and fullness. Quiet and Aware modes with 22-hour battery life.',
        'search_term': 'Bose QuietComfort 45 Wireless Noise Cancelling Headphones',
        'offers': [
            {'platform_name': 'Amazon India', 'price': Decimal('24900.00'), 'availability': 'Available'},
            {'platform_name': 'Flipkart', 'price': Decimal('25490.00'), 'availability': 'Available'},
            {'platform_name': 'Croma', 'price': Decimal('26990.00'), 'availability': 'Available'},
        ]
    },

    # ------------------ GAMING CONSOLES ------------------
    {
        'name': 'PlayStation 5',
        'brand': 'Sony',
        'model_name': 'Slim Disc Edition 1TB',
        'category': 'Gaming',
        'description': 'Experience lightning-fast loading with ultra-high speed SSD, deeper immersion with haptic feedback, adaptive triggers, and 3D Audio.',
        'search_term': 'Sony PlayStation 5 Slim Disc Edition',
        'offers': [
            {'platform_name': 'Amazon India', 'price': Decimal('49990.00'), 'availability': 'Available'},
            {'platform_name': 'Flipkart', 'price': Decimal('50990.00'), 'availability': 'Available'},
            {'platform_name': 'Sony Official Center', 'price': Decimal('54990.00'), 'availability': 'Available'},
            {'platform_name': 'Croma', 'price': Decimal('52990.00'), 'availability': 'Available'},
        ]
    },
    {
        'name': 'Nintendo Switch',
        'brand': 'Nintendo',
        'model_name': 'OLED Model White',
        'category': 'Gaming',
        'description': 'Features a vibrant 7-inch OLED screen, wide adjustable stand, dock with wired LAN port, 64GB of internal storage, and enhanced audio.',
        'search_term': 'Nintendo Switch OLED Model White Console',
        'offers': [
            {'platform_name': 'Amazon India', 'price': Decimal('29990.00'), 'availability': 'Available'},
            {'platform_name': 'Flipkart', 'price': Decimal('30499.00'), 'availability': 'Available'},
            {'platform_name': 'Mx2Games', 'price': Decimal('31999.00'), 'availability': 'Available'},
        ]
    },

    # ------------------ SMART TELEVISIONS ------------------
    {
        'name': 'Bravia 55-inch',
        'brand': 'Sony',
        'model_name': '4K Ultra HD Smart LED TV (KD-55X74L)',
        'category': 'Televisions',
        'description': 'Sony Bravia 55-inch 4K Google TV with X1 4K Processor, 4K X-Reality PRO, Live Color, and Open Baffle Speaker with Dolby Audio.',
        'search_term': 'Sony Bravia 55 inch 4K Ultra HD Smart LED Google TV KD-55X74L',
        'offers': [
            {'platform_name': 'Amazon India', 'price': Decimal('57990.00'), 'availability': 'Available'},
            {'platform_name': 'Flipkart', 'price': Decimal('58990.00'), 'availability': 'Available'},
            {'platform_name': 'Croma', 'price': Decimal('59990.00'), 'availability': 'Available'},
            {'platform_name': 'Reliance Digital', 'price': Decimal('60990.00'), 'availability': 'Available'},
        ]
    },
]

total_products = 0
total_offers = 0

for p_data in products_data:
    offers = p_data.pop('offers')
    search_term = p_data.pop('search_term')
    product = Product.objects.create(**p_data)
    total_products += 1

    for off in offers:
        platform = off['platform_name']
        product_url = make_store_url(platform, search_term)
        PriceOffer.objects.create(
            product=product,
            platform_name=platform,
            price=off['price'],
            product_url=product_url,
            availability=off['availability']
        )
        total_offers += 1

print(f"Successfully seeded {total_products} products and {total_offers} price offers with direct retailer links into MySQL!")

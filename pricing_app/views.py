from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Product, PriceOffer
from .forms import RegisterForm


def home(request):
    """
    Public landing page introducing Smart Price Catalog,
    with a featured preview of products and quick access to search.
    """
    featured_products = Product.objects.all().order_by('-created_at')[:6]
    return render(request, 'home.html', {
        'featured_products': featured_products,
    })


@login_required
def catalog(request):
    """
    Product catalog page where customers can search by:
    - Product name
    - Brand
    - Model name
    - Category
    Displays matching products with their model names.
    Prices are viewed upon clicking 'Compare Prices'.
    """
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    products = Product.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(brand__icontains=query) |
            Q(model_name__icontains=query) |
            Q(category__icontains=query)
        )

    if category:
        products = products.filter(category__iexact=category)

    products = products.order_by('name', 'model_name')
    categories = list(Product.objects.exclude(category='').values_list('category', flat=True).distinct().order_by('category'))

    return render(request, 'catalog.html', {
        'products': products,
        'query': query,
        'category_filter': category,
        'categories': categories,
        'total_count': products.count(),
    })



@login_required
def product_detail(request, product_id):
    """
    Individual product information and model details page.
    """
    product = get_object_or_404(Product, id=product_id)
    offers = product.offers.all().order_by('price')
    return render(request, 'product_detail.html', {
        'product': product,
        'offers': offers,
    })


@login_required
def price_comparison(request, product_id):
    """
    Compare prices from different online stores for the selected product model.
    Shows retailer offers sorted in ascending order of price, with:
    - Retailer name and optional logo
    - Price in Indian Rupees
    - Availability status
    - Last updated timestamp
    - Direct store link
    """
    product = get_object_or_404(Product, id=product_id)
    offers = product.offers.all().order_by('price')

    lowest_offer = offers.filter(availability__iexact='Available').first()
    if not lowest_offer and offers.exists():
        lowest_offer = offers.first()

    return render(request, 'price_comparison.html', {
        'product': product,
        'offers': offers,
        'lowest_offer': lowest_offer,
    })


def register(request):
    """
    Customer registration view with form validation.
    """
    if request.user.is_authenticated:
        return redirect('catalog')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {
        'form': form
    })


def user_login(request):
    """
    Customer login view using Django's authentication system.
    Redirects directly to catalog upon login.
    """
    if request.user.is_authenticated:
        return redirect('catalog')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next') or 'catalog'
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password. Please try again.')

    return render(request, 'login.html')


def user_logout(request):
    """
    Customer logout view.
    """
    logout(request)
    messages.info(request, 'You have been logged out safely.')
    return redirect('home')

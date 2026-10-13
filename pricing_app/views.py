import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import ExpressionWrapper, F, FloatField
from django.urls import reverse

from .forms import CompetitorPriceForm, ProductForm, ProductURLForm
from .models import Product, CompetitorPrice
from .price_scraper import (
    PriceLookupError,
    fetch_product_details,
    fetch_product_price,
)


# Home Page
def home(request):
    return render(request, 'home.html')


# Product List
@login_required
def product_list(request):
    products = Product.objects.filter(
        owner=request.user
    ).order_by('name')

    return render(request, 'product_list.html', {
        'products': products
    })


# User Registration
def register(request):

    if request.method == 'POST':

        form = UserCreationForm(request.POST)

        username = request.POST.get('username')
        email = request.POST.get('email')

        if form.is_valid():

            if User.objects.filter(email=email).exists():

                messages.error(request, 'Email already exists.')

            else:

                user = form.save(commit=False)

                user.email = email

                user.save()

                messages.success(
                    request,
                    'Registration successful. Please login.'
                )

                return redirect('login')

        else:

            for error in form.errors.values():
                messages.error(request, error)

    return render(request, 'register.html')


# User Login
def login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            auth_login(request, user)

            messages.success(request, 'Login successful.')

            return redirect('home')

        else:

            messages.error(
                request,
                'Invalid username or password.'
            )

    return render(request, 'login.html')


def logout(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


@login_required
def add_product(request):
    form = ProductForm(request.POST or None, adding=True)
    if request.method == 'POST' and form.is_valid():
        product = form.save(commit=False)
        product.owner = request.user
        product.current_price = form.cleaned_data['target_buying_price']
        product.stock_quantity = 0
        product.save()
        messages.success(request, 'Product added successfully.')
        return redirect('product_list')

    return render(request, 'add_product.html', {
        'form': form,
        'editing': False,
    })


@login_required
def add_product_from_url(request):
    form = ProductURLForm(
        request.POST or None,
        initial={
            'product_url': (
                'https://www.amazon.in/Fastrack-Striker-Stainless-Material-'
                'Watches/dp/B0FLV5BLKN?th=1'
            ),
        },
    )
    if request.method == 'POST' and form.is_valid():
        try:
            product_name, price = fetch_product_details(
                form.cleaned_data['product_url']
            )
        except PriceLookupError as exc:
            form.add_error('product_url', str(exc))
        else:
            with transaction.atomic():
                product = Product.objects.create(
                    owner=request.user,
                    name=product_name,
                    current_price=price,
                    target_buying_price=price,
                    stock_quantity=0,
                )
                CompetitorPrice.objects.create(
                    product=product,
                    website_name='Amazon.in',
                    competitor_price=price,
                    product_url=form.cleaned_data['product_url'],
                )
            messages.success(
                request,
                'Product created and its Amazon price added successfully.',
            )
            return redirect('compare_prices', product_id=product.pk)

    return render(request, 'add_product_from_url.html', {
        'form': form,
    })


@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id, owner=request.user)
    form = ProductForm(request.POST or None, instance=product)

    if request.method == 'POST':
        with transaction.atomic():
            product = get_object_or_404(
                Product.objects.select_for_update(),
                pk=product_id,
                owner=request.user,
            )
            form = ProductForm(request.POST, instance=product)
            if form.is_valid():
                form.save()
                messages.success(request, 'Product updated successfully.')
                return redirect('product_detail', product_id=product.pk)

    return render(request, 'add_product.html', {
        'form': form,
        'editing': True,
        'product': product,
    })


@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id, owner=request.user)
    if request.method == 'POST':
        with transaction.atomic():
            product = get_object_or_404(
                Product.objects.select_for_update(),
                pk=product_id,
                owner=request.user,
            )
            product.delete()
        messages.success(
            request,
            'Product and its related competitor prices were deleted.'
        )
        return redirect('product_list')

    return render(request, 'confirm_delete.html', {
        'object_name': product.name,
        'delete_title': 'Delete product',
        'warning': (
            'Deleting this product also deletes its competitor prices.'
        ),
        'cancel_url': reverse('product_detail', args=[product.pk]),
    })

@login_required
def product_detail(request, product_id):

    product = get_object_or_404(
        Product, id=product_id, owner=request.user
    )

    return render(request, 'product_detail.html', {
        'product': product
    })

@login_required
def compare_prices(request, product_id):

    product = get_object_or_404(
        Product, id=product_id, owner=request.user
    )

    competitor_listings = CompetitorPrice.objects.filter(
        product=product
    ).annotate(
        price_difference=ExpressionWrapper(
            F('competitor_price') - F('product__target_buying_price'),
            output_field=FloatField(),
        )
    ).order_by('website_name')
    priced_listings = competitor_listings.filter(
        competitor_price__isnull=False
    ).order_by('competitor_price', 'website_name')
    best_offer = priced_listings.first()

    return render(request, 'compare_prices.html', {
        'product': product,
        'competitor_listings': competitor_listings,
        'best_offer': best_offer,
    })


@login_required
def add_competitor_price(request, product_id):
    product = get_object_or_404(
        Product, pk=product_id, owner=request.user
    )
    form = CompetitorPriceForm(
        request.POST or None,
        user=request.user,
        initial={'product': product},
    )
    form.fields['product'].queryset = Product.objects.filter(
        pk=product.pk,
        owner=request.user,
    )
    if request.method == 'POST' and form.is_valid():
        try:
            competitor_price = fetch_product_price(
                form.cleaned_data['product_url']
            )
        except PriceLookupError as exc:
            form.add_error('product_url', str(exc))
        else:
            competitor_listing = form.save(commit=False)
            competitor_listing.competitor_price = competitor_price
            competitor_listing.save()
            messages.success(
                request,
                'Competitor listing added and its price fetched successfully.',
            )
            return redirect(
                'compare_prices',
                product_id=competitor_listing.product_id
            )

    return render(request, 'competitor_price_form.html', {
        'form': form,
        'editing': False,
        'product': product,
    })


@login_required
def edit_competitor_price(request, competitor_price_id):
    competitor_price = get_object_or_404(
        CompetitorPrice.objects.select_related('product'),
        pk=competitor_price_id,
        product__owner=request.user,
    )
    form = CompetitorPriceForm(
        request.POST or None,
        instance=competitor_price,
        user=request.user,
    )
    if request.method == 'POST' and form.is_valid():
        try:
            fetched_price = fetch_product_price(
                form.cleaned_data['product_url']
            )
        except PriceLookupError as exc:
            form.add_error('product_url', str(exc))
        else:
            competitor_price = form.save(commit=False)
            competitor_price.competitor_price = fetched_price
            competitor_price.save()
            messages.success(
                request,
                'Competitor listing updated and its price fetched successfully.',
            )
            return redirect(
                'compare_prices',
                product_id=competitor_price.product_id
            )

    return render(request, 'competitor_price_form.html', {
        'form': form,
        'editing': True,
        'product': competitor_price.product,
    })


@login_required
def delete_competitor_price(request, competitor_price_id):
    competitor_price = get_object_or_404(
        CompetitorPrice.objects.select_related('product'),
        pk=competitor_price_id,
        product__owner=request.user,
    )
    product_id = competitor_price.product_id
    if request.method == 'POST':
        competitor_price.delete()
        messages.success(request, 'Competitor price deleted successfully.')
        return redirect('compare_prices', product_id=product_id)

    return render(request, 'confirm_delete.html', {
        'object_name': '{} competitor price'.format(
            competitor_price.website_name
        ),
        'delete_title': 'Delete competitor price',
        'warning': 'This competitor price record will be permanently deleted.',
        'cancel_url': reverse('compare_prices', args=[product_id]),
    })

@login_required
def demand_analysis(request, product_id):
    product = get_object_or_404(
        Product, id=product_id, owner=request.user
    )
    offers = CompetitorPrice.objects.filter(
        product=product,
        competitor_price__isnull=False,
    ).order_by('competitor_price', 'website_name')
    best_offer = offers.first()

    context = {
        'product': product,
        'offer_count': CompetitorPrice.objects.filter(product=product).count(),
        'priced_offer_count': offers.count(),
        'best_offer': best_offer,
        'price_difference': (
            best_offer.competitor_price - product.target_buying_price
            if best_offer and product.target_buying_price is not None
            else None
        ),
    }

    return render(request, 'demand_analysis.html', context)



@login_required
def pricing_recommendation(request, product_id):
    product = get_object_or_404(
        Product, id=product_id, owner=request.user
    )
    best_offer = CompetitorPrice.objects.filter(
        product=product,
        competitor_price__isnull=False,
    ).order_by('competitor_price', 'website_name').first()

    context = {
        'product': product,
        'best_offer': best_offer,
        'price_difference': (
            best_offer.competitor_price - product.target_buying_price
            if best_offer and product.target_buying_price is not None
            else None
        ),
    }

    return render(request, 'pricing_recommendation.html', context)


@login_required
def dashboard(request):
    user_products = Product.objects.filter(owner=request.user)
    total_products = user_products.count()
    total_website_offers = CompetitorPrice.objects.filter(
        product__owner=request.user
    ).count()
    total_priced_offers = CompetitorPrice.objects.filter(
        product__owner=request.user,
        competitor_price__isnull=False,
    ).count()

    context = {
        'total_products': total_products,
        'total_website_offers': total_website_offers,
        'total_priced_offers': total_priced_offers,
        'products_with_targets': user_products.filter(
            target_buying_price__isnull=False
        ).count(),
        'products': user_products.order_by('-id')[:10],
    }

    return render(request, 'dashboard.html', context)

@login_required
def pricing_comparison(request, product_id):
    product = get_object_or_404(
        Product, id=product_id, owner=request.user
    )
    return redirect('compare_prices', product_id=product.pk)

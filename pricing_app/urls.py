from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),

    path('home/', views.home),

    path('product_list/', views.product_list, name='product_list'),

    path('add_product/', views.add_product, name='add_product'),

    path('add_product/from-url/', views.add_product_from_url,
         name='add_product_from_url'),

    path('product/<int:product_id>/edit/', views.edit_product, name='edit_product'),

    path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),

    path('product_detail/<int:product_id>/',views.product_detail,name='product_detail'),

    path('register/', views.register, name='register'),

    path('login/', views.login, name='login'),

    path('logout/', views.logout, name='logout'),

    path('compare_prices/<int:product_id>/',views.compare_prices,name='compare_prices'),

    path('product/<int:product_id>/competitor-prices/add/',
         views.add_competitor_price, name='add_competitor_price'),

    path('competitor-price/<int:competitor_price_id>/edit/',
         views.edit_competitor_price, name='edit_competitor_price'),

    path('competitor-price/<int:competitor_price_id>/delete/',
         views.delete_competitor_price, name='delete_competitor_price'),

    path('demand_analysis/<int:product_id>/',views.demand_analysis,name='demand_analysis'),

    path('pricing_recommendation/<int:product_id>/',views.pricing_recommendation,name='pricing_recommendation'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('pricing_comparison/<int:product_id>/',views.pricing_comparison,name='pricing_comparison'),

]
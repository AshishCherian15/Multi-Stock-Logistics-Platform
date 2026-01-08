from django.urls import path
from . import views
from greaterwms import views_guest

app_name = 'guest'

urlpatterns = [
    # Home -> redirect to dashboard
    path('', views.guest_home, name='home'),
    # Dashboard, Marketplace handled by greaterwms/views_guest.py
    path('dashboard/', views_guest.guest_dashboard, name='dashboard'),
    path('marketplace/', views_guest.guest_marketplace, name='marketplace'),
    path('forums/', views_guest.guest_forums, name='forums'),
    path('about/', views_guest.guest_about, name='about'),
    
    # Products
    path('products/', views.browse_products, name='products'),
    path('products/<int:product_id>/', views.product_detail_guest, name='product_detail'),
    
    # Services
    path('services/', views.view_services, name='services'),
    
    # Pricing
    path('pricing/', views.pricing_page, name='pricing'),
    
    # Contact
    path('contact/', views.contact_page, name='contact'),
    
    # Rentals, Storage, Lockers (view-only)
    path('rentals/', views.guest_rentals, name='rentals'),
    path('storage/', views.guest_storage, name='storage'),
    path('lockers/', views.guest_lockers, name='lockers'),
]

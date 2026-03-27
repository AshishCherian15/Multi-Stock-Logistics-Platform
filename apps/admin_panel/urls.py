from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard
    path('', views.admin_dashboard, name='dashboard'),
    
    # User Management
    path('users/', views.user_management, name='users'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/toggle-active/', views.user_toggle_active, name='user_toggle_active'),
    
    # Order Management
    path('orders/', views.order_management, name='orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/update-status/', views.order_update_status, name='order_update_status'),
    
    # Inventory Management
    path('inventory/', views.inventory_management, name='inventory'),
    
    # Customer Management
    path('customers/', views.customer_management, name='customers'),
    
    # Booking Management
    path('bookings/', views.booking_management, name='bookings'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
]

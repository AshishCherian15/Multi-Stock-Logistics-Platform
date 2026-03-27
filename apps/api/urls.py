from django.urls import path
from . import views, customer_apis, booking_payment_apis

urlpatterns = [
    path('dashboard/metrics/', views.dashboard_metrics, name='dashboard_metrics'),
    path('products/bulk/', views.bulk_product_action, name='bulk_products'),
    path('orders/stats/', views.order_statistics, name='order_stats'),
    path('inventory/alerts/', views.inventory_alerts, name='inventory_alerts'),
    path('audit/logs/', views.audit_logs, name='audit_logs'),
    path('settings/get/', views.get_settings, name='get_settings'),
    path('settings/save/', views.save_settings, name='save_settings'),
    
    # Customer APIs
    path('rentals/', customer_apis.rentals_list_api, name='customer_rentals_api'),
    path('storage-units/', customer_apis.storage_units_list_api, name='customer_storage_api'),
    path('lockers/', customer_apis.lockers_list_api, name='customer_lockers_api'),
    path('invoices/', customer_apis.invoices_list_api, name='customer_invoices_api'),
    
    # Booking & Payment APIs
    path('booking/rental/process/', booking_payment_apis.process_rental_booking, name='process_rental_booking'),
    path('booking/storage/process/', booking_payment_apis.process_storage_booking, name='process_storage_booking'),
    path('booking/locker/process/', booking_payment_apis.process_locker_booking, name='process_locker_booking'),
    path('agreement/rental/<int:item_id>/', booking_payment_apis.get_rental_agreement, name='get_rental_agreement'),
    path('agreement/storage/<int:unit_id>/', booking_payment_apis.get_storage_agreement, name='get_storage_agreement'),
    path('agreement/locker/<int:locker_id>/', booking_payment_apis.get_locker_agreement, name='get_locker_agreement'),
]

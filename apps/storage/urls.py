from django.urls import path
from . import views, api_views

app_name = 'storage'

urlpatterns = [
    path('', views.customer_storage_shop, name='list'),
    path('admin/', views.storage_list, name='storage_admin_list'),
    path('<int:unit_id>/', views.storage_detail, name='detail'),
    path('<int:unit_id>/book/', views.book_storage, name='book'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('api/analytics/', api_views.analytics_data, name='analytics'),
    path('api/unit/<int:unit_id>/update/', api_views.update_unit_field, name='update_unit'),
    path('api/unit/<int:unit_id>/update-full/', api_views.update_unit_full, name='update_unit_full'),
    path('api/unit/<int:unit_id>/detail/', api_views.get_unit_detail, name='unit_detail'),
    path('api/unit/<int:unit_id>/duplicate/', api_views.duplicate_unit, name='duplicate_unit'),
    path('api/unit/<int:unit_id>/delete/', api_views.delete_unit, name='delete_unit'),
    path('api/booking/create/', api_views.create_booking, name='create_booking'),
    path('api/booking/storage/process/', api_views.create_booking, name='process_booking'),
    path('api/unit/<int:unit_id>/status/', api_views.update_unit_status, name='update_unit_status'),
    path('booking/<int:booking_id>/detail/', views.storage_booking_detail, name='storage_booking_detail'),
    path('api/booking/<int:booking_id>/cancel/', api_views.cancel_storage_booking, name='cancel_storage_booking'),
]

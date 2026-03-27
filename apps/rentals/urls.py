from django.urls import path
from . import views, api_views

urlpatterns = [
    path('', views.customer_rentals_shop, name='rentals_list'),  # Customer shopping page as default
    path('admin/', views.rentals_list, name='rentals_admin_list'),  # Admin page moved to /admin/
    path('<int:item_id>/', views.rental_detail, name='rental_detail_short'),
    path('item/<int:item_id>/', views.rental_detail, name='rental_detail'),
    path('item/<int:item_id>/edit/', views.rental_edit, name='rental_edit'),
    path('book/<int:item_id>/', views.rental_book, name='rental_book'),
    path('booking/<int:booking_id>/summary/', views.booking_summary, name='booking_summary'),
    path('booking/<int:booking_id>/agreement/', views.rental_agreement, name='rental_agreement'),
    path('history/', views.rental_history, name='rental_history'),
    path('maintenance/', views.maintenance_schedule, name='maintenance_schedule'),
    path('api/analytics/', views.analytics_api, name='rental_analytics'),
    path('api/item/<int:item_id>/status/', views.update_item_status, name='update_item_status'),
    path('api/item/<int:item_id>/price/', views.update_item_price, name='update_item_price'),
    path('api/item/<int:item_id>/duplicate/', views.duplicate_item, name='duplicate_item'),
    path('api/item/<int:item_id>/delete/', views.delete_item, name='delete_item'),
    path('api/item/<int:item_id>/update/', views.update_item, name='update_item'),
    path('api/item/create/', views.create_item, name='create_item'),
    path('api/booking/create/', views.create_booking_api, name='create_booking'),
    path('api/item/<int:item_id>/detail/', views.item_detail_api, name='item_detail_api'),
    path('booking/<int:booking_id>/detail/', views.rental_booking_detail, name='rental_booking_detail'),
    path('api/booking/<int:booking_id>/cancel/', api_views.cancel_rental_booking, name='cancel_rental_booking'),
]

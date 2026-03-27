from django.urls import path
from . import views, api_views

app_name = 'lockers'

urlpatterns = [
    path('', views.customer_lockers_shop, name='list'),
    path('admin/', views.lockers_list, name='lockers_admin_list'),
    path('<int:locker_id>/', views.locker_detail, name='detail'),
    path('<int:locker_id>/book/', views.book_locker, name='book'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('analytics/', views.locker_analytics, name='analytics'),
    path('api/booking/create/', api_views.create_booking, name='create_booking'),
    path('api/booking/locker/process/', api_views.create_booking, name='process_booking'),
    path('api/booking/<int:booking_id>/cancel/', api_views.cancel_booking, name='cancel_booking'),
    path('api/booking/<int:booking_id>/extend/', api_views.extend_booking, name='extend_booking'),
    path('api/booking/<int:booking_id>/details/', api_views.get_booking_details, name='booking_details'),
    path('api/<int:locker_id>/validate/', api_views.validate_access_code, name='validate_access'),
    path('api/<int:locker_id>/duplicate/', api_views.duplicate_locker, name='duplicate_locker'),
    path('api/<int:locker_id>/update/', api_views.update_locker, name='update_locker'),
    path('api/locker/<int:locker_id>/update/', api_views.update_locker, name='update_locker_alt'),
    path('api/<int:locker_id>/delete/', api_views.delete_locker, name='delete_locker'),
    path('api/<int:locker_id>/open/', api_views.open_locker, name='open_locker'),
    path('booking/<int:booking_id>/detail/', views.locker_booking_detail, name='locker_booking_detail'),
]

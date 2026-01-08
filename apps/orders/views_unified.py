from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from permissions.decorators import get_user_role
from orders.models import Order
from rentals.models import RentalBooking
from storage.models import StorageBooking
from lockers.models import LockerBooking

@login_required
def unified_orders(request):
    """Unified orders page showing all bookings and purchases"""
    role = get_user_role(request.user)
    
    # Get all order types based on role
    if role == 'customer':
        # Customers see only their bookings
        marketplace_orders = Order.objects.filter(customer_user=request.user).order_by('-created_at')
        rental_bookings = RentalBooking.objects.filter(customer=request.user).select_related('item').order_by('-created_at')
        storage_bookings = StorageBooking.objects.filter(user=request.user).select_related('unit').order_by('-created_at')
        locker_bookings = LockerBooking.objects.filter(created_by=request.user).select_related('locker').order_by('-created_at')
    else:
        # Team members see all bookings
        marketplace_orders = Order.objects.filter(order_type='sale').order_by('-created_at')
        rental_bookings = RentalBooking.objects.all().select_related('item', 'customer').order_by('-created_at')
        storage_bookings = StorageBooking.objects.all().select_related('unit', 'user').order_by('-created_at')
        locker_bookings = LockerBooking.objects.all().select_related('locker', 'created_by').order_by('-created_at')
    
    context = {
        'marketplace_orders': marketplace_orders[:50],
        'rental_bookings': rental_bookings[:50],
        'storage_bookings': storage_bookings[:50],
        'locker_bookings': locker_bookings[:50],
        'user_role': role,
    }
    return render(request, 'orders/unified_orders.html', context)

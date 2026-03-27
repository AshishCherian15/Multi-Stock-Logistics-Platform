from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from permissions.decorators import require_role

# Removed unused dashboard functions - all team roles now use superadmin dashboard

@login_required
@require_role('customer')
def customer_dashboard(request):
    from orders.models import Order
    from cart.models import Cart
    from goods.models import ListModel as Product
    
    # Customer Metrics
    my_orders = Order.objects.filter(customer_user=request.user).count()
    pending_orders = Order.objects.filter(customer_user=request.user, status__in=['pending', 'confirmed']).count()
    
    # Cart items
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.count()
    except Cart.DoesNotExist:
        cart_items = 0
    
    # Wishlist items
    try:
        from wishlist.models import Wishlist
        wishlist = Wishlist.objects.get(user=request.user)
        wishlist_items = wishlist.items.count()
    except:
        wishlist_items = 0
    
    # Rentals count
    try:
        from rentals.models import RentalBooking
        active_rentals = RentalBooking.objects.filter(
            customer=request.user, 
            status__in=['active', 'pending', 'confirmed']
        ).count()
    except:
        active_rentals = 0
    
    # Storage units count
    try:
        from storage.models import StorageBooking
        storage_units = StorageBooking.objects.filter(
            user=request.user, 
            status='active'
        ).count()
    except:
        storage_units = 0
    
    # Locker bookings count
    try:
        from lockers.models import LockerBooking
        locker_bookings = LockerBooking.objects.filter(
            created_by=request.user, 
            status__in=['active', 'pending']
        ).count()
    except:
        locker_bookings = 0
    
    # Recent Orders
    recent_orders = Order.objects.filter(customer_user=request.user).only(
        'order_number', 'status', 'total_amount', 'created_at'
    ).order_by('-created_at')[:5]
    
    context = {
        'my_orders': my_orders,
        'pending_orders': pending_orders,
        'cart_items': cart_items,
        'wishlist_items': wishlist_items,
        'active_rentals': active_rentals,
        'storage_units': storage_units,
        'locker_bookings': locker_bookings,
        'recent_orders': recent_orders,
    }
    
    return render(request, 'dashboards/customer.html', context)

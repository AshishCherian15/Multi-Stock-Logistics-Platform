from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.http import require_http_methods
from permissions.decorators import require_role
import json

@login_required
@require_role('admin')
def admin_dashboard(request):
    """Admin dashboard with comprehensive metrics"""
    from goods.models import ListModel as Product
    from stock.models import StockListModel
    from orders.models import Order
    from customer.models import ListModel as Customer
    from django.contrib.auth.models import User
    
    # Time periods
    today = timezone.now().date()
    month_start = timezone.now().replace(day=1)
    week_ago = timezone.now() - timedelta(days=7)
    
    # User metrics
    total_users = User.objects.count()
    total_customers = Customer.objects.count()
    new_users_week = User.objects.filter(date_joined__gte=week_ago).count()
    active_users = User.objects.filter(last_login__gte=week_ago).count()
    
    # Order metrics
    orders = Order.objects.all()
    total_orders = orders.count()
    orders_today = orders.filter(created_at__date=today).count()
    orders_month = orders.filter(created_at__gte=month_start).count()
    pending_orders = orders.filter(status__in=['pending', 'confirmed']).count()
    
    # Revenue metrics
    total_revenue = orders.filter(status='completed').aggregate(
        total=Sum('grand_total'))['total'] or 0
    revenue_month = orders.filter(
        status='completed', 
        created_at__gte=month_start
    ).aggregate(total=Sum('grand_total'))['total'] or 0
    
    # Inventory metrics
    stocks = StockListModel.objects.all()
    total_products = Product.objects.count()
    low_stock = stocks.filter(can_order_stock__lte=10, can_order_stock__gt=0).count()
    out_of_stock = stocks.filter(can_order_stock=0).count()
    total_stock_value = 0
    
    # Calculate stock value
    for stock in stocks:
        try:
            product = Product.objects.filter(goods_code=stock.goods_code).first()
            if product:
                total_stock_value += float(product.goods_price) * stock.goods_qty
        except:
            pass
    
    # Booking metrics (if available)
    try:
        from rentals.models import RentalBooking
        active_rentals = RentalBooking.objects.filter(status='active').count()
    except:
        active_rentals = 0
    
    try:
        from storage.models import StorageBooking
        active_storage = StorageBooking.objects.filter(status='active').count()
    except:
        active_storage = 0
    
    try:
        from lockers.models import LockerBooking
        active_lockers = LockerBooking.objects.filter(status='active').count()
    except:
        active_lockers = 0
    
    # Recent activity
    recent_orders = orders.order_by('-created_at')[:10]
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    # Pending approvals
    pending_approvals = pending_orders
    
    context = {
        'total_users': total_users,
        'total_customers': total_customers,
        'new_users_week': new_users_week,
        'active_users': active_users,
        'total_orders': total_orders,
        'orders_today': orders_today,
        'orders_month': orders_month,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue,
        'revenue_month': revenue_month,
        'total_products': total_products,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'total_stock_value': total_stock_value,
        'active_rentals': active_rentals,
        'active_storage': active_storage,
        'active_lockers': active_lockers,
        'recent_orders': recent_orders,
        'recent_users': recent_users,
        'pending_approvals': pending_approvals,
    }
    
    return render(request, 'admin/dashboard.html', context)


@login_required
@require_role('admin')
def user_management(request):
    """User management page"""
    users = User.objects.all().order_by('-date_joined')
    
    # Filter by role if specified
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role__role=role_filter)
    
    # Search
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    context = {
        'users': users,
        'total_users': users.count(),
    }
    
    return render(request, 'admin/users/list.html', context)


@login_required
@require_role('admin')
def user_detail(request, user_id):
    """View user details"""
    user = get_object_or_404(User, id=user_id)
    
    # Get user's orders
    try:
        from orders.models import Order
        user_orders = Order.objects.filter(customer_user=user).order_by('-created_at')[:10]
    except:
        user_orders = []
    
    # Get user's bookings
    try:
        from rentals.models import RentalBooking
        user_rentals = RentalBooking.objects.filter(customer=user).order_by('-created_at')[:10]
    except:
        user_rentals = []
    
    context = {
        'user': user,
        'user_orders': user_orders,
        'user_rentals': user_rentals,
    }
    
    return render(request, 'admin/users/detail.html', context)


@login_required
@require_role('admin')
@require_http_methods(["POST"])
def user_toggle_active(request, user_id):
    """Activate/Deactivate user"""
    user = get_object_or_404(User, id=user_id)
    
    # Don't allow admin to deactivate superusers
    if user.is_superuser:
        return JsonResponse({
            'success': False,
            'message': 'Cannot modify superuser accounts'
        }, status=403)
    
    user.is_active = not user.is_active
    user.save()
    
    return JsonResponse({
        'success': True,
        'is_active': user.is_active,
        'message': f'User {"activated" if user.is_active else "deactivated"} successfully'
    })


@login_required
@require_role('admin')
def order_management(request):
    """Order management page"""
    from orders.models import Order
    
    orders = Order.objects.select_related('customer_user', 'customer').prefetch_related('items').order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Search
    search = request.GET.get('search')
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(customer_user__username__icontains=search) |
            Q(customer_user__email__icontains=search)
        )
    
    context = {
        'orders': orders,
        'total_orders': orders.count(),
    }
    
    return render(request, 'admin/orders/list.html', context)


@login_required
@require_role('superadmin', 'admin')
def order_detail(request, order_id):
    """View order details"""
    from orders.models import Order
    
    order = get_object_or_404(Order, id=order_id)
    
    context = {
        'order': order,
    }
    
    return render(request, 'admin/orders/detail.html', context)


@login_required
@require_role('admin')
@require_http_methods(["POST"])
def order_update_status(request, order_id):
    """Update order status"""
    from orders.models import Order
    
    order = get_object_or_404(Order, id=order_id)
    
    data = json.loads(request.body)
    new_status = data.get('status')
    
    if new_status in dict(Order.STATUS_CHOICES).keys():
        order.status = new_status
        order.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Order status updated to {new_status}'
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid status'
    }, status=400)


@login_required
@require_role('admin')
def inventory_management(request):
    """Inventory management page"""
    from goods.models import ListModel as Product
    from stock.models import StockListModel
    
    products = Product.objects.all().order_by('-create_time')
    
    # Search
    search = request.GET.get('search')
    if search:
        products = products.filter(
            Q(goods_name__icontains=search) |
            Q(goods_code__icontains=search) |
            Q(goods_desc__icontains=search)
        )
    
    # Add stock info to products
    products_with_stock = []
    for product in products:
        stock = StockListModel.objects.filter(goods_code=product.goods_code).first()
        product.stock_qty = stock.goods_qty if stock else 0
        product.stock_available = stock.can_order_stock if stock else 0
        products_with_stock.append(product)
    
    context = {
        'products': products_with_stock,
        'total_products': len(products_with_stock),
    }
    
    return render(request, 'admin/inventory/list.html', context)


@login_required
@require_role('admin')
def customer_management(request):
    """Customer management page"""
    from customer.models import ListModel as Customer
    
    customers = Customer.objects.all().order_by('-create_time')
    
    # Search
    search = request.GET.get('search')
    if search:
        customers = customers.filter(
            Q(customer_name__icontains=search) |
            Q(customer_city__icontains=search) |
            Q(customer_contact__icontains=search)
        )
    
    context = {
        'customers': customers,
        'total_customers': customers.count(),
    }
    
    return render(request, 'admin/customers/list.html', context)


@login_required
@require_role('admin')
def booking_management(request):
    """Booking management page"""
    bookings = []
    
    # Get all bookings
    try:
        from rentals.models import RentalBooking
        rentals = RentalBooking.objects.all().order_by('-created_at')
        for rental in rentals:
            bookings.append({
                'type': 'Rental',
                'id': rental.id,
                'customer': rental.customer.username if rental.customer else 'N/A',
                'item': rental.equipment.name if hasattr(rental, 'equipment') else 'N/A',
                'status': rental.status,
                'total': rental.total_amount,
                'created_at': rental.created_at,
            })
    except:
        pass
    
    try:
        from storage.models import StorageBooking
        storage = StorageBooking.objects.all().order_by('-created_at')
        for booking in storage:
            bookings.append({
                'type': 'Storage',
                'id': booking.id,
                'customer': booking.user.username if booking.user else 'N/A',
                'item': f"Unit {booking.unit.unit_number}" if hasattr(booking, 'unit') else 'N/A',
                'status': booking.status,
                'total': booking.total_amount,
                'created_at': booking.created_at,
            })
    except:
        pass
    
    try:
        from lockers.models import LockerBooking
        lockers = LockerBooking.objects.all().order_by('-created_at')
        for booking in lockers:
            bookings.append({
                'type': 'Locker',
                'id': booking.id,
                'customer': booking.created_by.username if booking.created_by else 'N/A',
                'item': f"Locker {booking.locker.locker_number}" if hasattr(booking, 'locker') else 'N/A',
                'status': booking.status,
                'total': booking.total_amount,
                'created_at': booking.created_at,
            })
    except:
        pass
    
    # Sort by created_at
    bookings.sort(key=lambda x: x['created_at'], reverse=True)
    
    context = {
        'bookings': bookings,
        'total_bookings': len(bookings),
    }
    
    return render(request, 'admin/bookings/list.html', context)


@login_required
@require_role('admin')
def reports(request):
    """Reports page"""
    from orders.models import Order
    from goods.models import ListModel as Product
    from customer.models import ListModel as Customer
    
    # Date range
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Sales report
    orders = Order.objects.filter(created_at__gte=start_date)
    total_sales = orders.aggregate(total=Sum('grand_total'))['total'] or 0
    total_orders = orders.count()
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0
    
    # Top products
    top_products = Product.objects.all()[:10]
    
    # Customer stats
    total_customers = Customer.objects.count()
    new_customers = Customer.objects.filter(create_time__gte=start_date).count()
    
    context = {
        'days': days,
        'total_sales': total_sales,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'top_products': top_products,
        'total_customers': total_customers,
        'new_customers': new_customers,
    }
    
    return render(request, 'admin/reports/index.html', context)

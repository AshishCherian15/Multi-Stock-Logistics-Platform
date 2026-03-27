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
@require_role('subadmin', 'staff')
def supervisor_dashboard(request):
    """Supervisor dashboard with operational metrics"""
    from goods.models import ListModel as Product
    from stock.models import StockListModel
    from orders.models import Order
    from customer.models import ListModel as Customer
    
    # Time periods
    today = timezone.now().date()
    week_ago = timezone.now() - timedelta(days=7)
    month_start = timezone.now().replace(day=1)
    
    # Team metrics (staff under supervision)
    team_members = User.objects.filter(role__role='staff').count()
    active_team = User.objects.filter(role__role='staff', last_login__gte=week_ago).count()
    
    # Order metrics (operational focus)
    orders = Order.objects.all()
    orders_today = orders.filter(created_at__date=today).count()
    orders_week = orders.filter(created_at__gte=week_ago).count()
    pending_orders = orders.filter(status__in=['pending', 'confirmed']).count()
    processing_orders = orders.filter(status='processing').count()
    
    # Inventory alerts
    stocks = StockListModel.objects.all()
    low_stock = stocks.filter(can_order_stock__lte=10, can_order_stock__gt=0).count()
    out_of_stock = stocks.filter(can_order_stock=0).count()
    
    # Booking metrics
    try:
        from rentals.models import RentalBooking
        pending_rentals = RentalBooking.objects.filter(status='pending').count()
        active_rentals = RentalBooking.objects.filter(status='active').count()
    except:
        pending_rentals = 0
        active_rentals = 0
    
    try:
        from storage.models import StorageBooking
        pending_storage = StorageBooking.objects.filter(status='pending').count()
        active_storage = StorageBooking.objects.filter(status='active').count()
    except:
        pending_storage = 0
        active_storage = 0
    
    # Tasks/Alerts
    total_alerts = low_stock + out_of_stock + pending_orders
    
    # Recent activity
    recent_orders = orders.order_by('-created_at')[:10]
    recent_team = User.objects.filter(role__role='staff').order_by('-last_login')[:10]
    
    context = {
        'team_members': team_members,
        'active_team': active_team,
        'orders_today': orders_today,
        'orders_week': orders_week,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'pending_rentals': pending_rentals,
        'active_rentals': active_rentals,
        'pending_storage': pending_storage,
        'active_storage': active_storage,
        'total_alerts': total_alerts,
        'recent_orders': recent_orders,
        'recent_team': recent_team,
    }
    
    return render(request, 'supervisor/dashboard.html', context)


@login_required
@require_role('subadmin', 'staff')
def team_management(request):
    """Manage team members (staff)"""
    team_members = User.objects.filter(role__role='staff').order_by('-date_joined')
    
    # Search
    search = request.GET.get('search')
    if search:
        team_members = team_members.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    # Status filter
    status = request.GET.get('status')
    if status == 'active':
        team_members = team_members.filter(is_active=True)
    elif status == 'inactive':
        team_members = team_members.filter(is_active=False)
    
    context = {
        'team_members': team_members,
        'total_team': team_members.count(),
    }
    
    return render(request, 'supervisor/team/list.html', context)


@login_required
@require_role('subadmin', 'staff')
def team_member_detail(request, user_id):
    """View team member details"""
    member = get_object_or_404(User, id=user_id, role__role='staff')
    
    # Get member's recent activity
    try:
        from orders.models import Order
        recent_orders = Order.objects.filter(
            created_by=member
        ).order_by('-created_at')[:10]
    except:
        recent_orders = []
    
    context = {
        'member': member,
        'recent_orders': recent_orders,
    }
    
    return render(request, 'supervisor/team/detail.html', context)


@login_required
@require_role('subadmin', 'staff')
def order_monitoring(request):
    """Monitor and manage orders"""
    from orders.models import Order
    
    orders = Order.objects.all().order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Search
    search = request.GET.get('search')
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(customer_user__username__icontains=search)
        )
    
    context = {
        'orders': orders,
        'total_orders': orders.count(),
    }
    
    return render(request, 'supervisor/orders/list.html', context)


@login_required
@require_role('subadmin', 'staff')
def order_detail_supervisor(request, order_id):
    """View order details"""
    from orders.models import Order
    
    order = get_object_or_404(Order, id=order_id)
    
    context = {
        'order': order,
    }
    
    return render(request, 'supervisor/orders/detail.html', context)


@login_required
@require_role('subadmin', 'staff')
@require_http_methods(["POST"])
def update_order_status_supervisor(request, order_id):
    """Update order status"""
    from orders.models import Order
    
    order = get_object_or_404(Order, id=order_id)
    
    data = json.loads(request.body)
    new_status = data.get('status')
    
    # Supervisors can only update to certain statuses
    allowed_statuses = ['confirmed', 'processing', 'shipped']
    
    if new_status in allowed_statuses:
        order.status = new_status
        order.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Order status updated to {new_status}'
        })
    
    return JsonResponse({
        'success': False,
        'message': 'You can only update to: confirmed, processing, or shipped'
    }, status=403)


@login_required
@require_role('subadmin', 'staff')
def inventory_monitoring(request):
    """Monitor inventory levels"""
    from goods.models import ListModel as Product
    from stock.models import StockListModel
    
    products = Product.objects.all().order_by('-create_time')
    
    # Filter by stock level
    stock_filter = request.GET.get('stock')
    if stock_filter == 'low':
        # Get products with low stock
        low_stock_codes = StockListModel.objects.filter(
            can_order_stock__lte=10,
            can_order_stock__gt=0
        ).values_list('goods_code', flat=True)
        products = products.filter(goods_code__in=low_stock_codes)
    elif stock_filter == 'out':
        # Get products out of stock
        out_stock_codes = StockListModel.objects.filter(
            can_order_stock=0
        ).values_list('goods_code', flat=True)
        products = products.filter(goods_code__in=out_stock_codes)
    
    # Search
    search = request.GET.get('search')
    if search:
        products = products.filter(
            Q(goods_name__icontains=search) |
            Q(goods_code__icontains=search)
        )
    
    # Add stock info
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
    
    return render(request, 'supervisor/inventory/list.html', context)


@login_required
@require_role('subadmin')
def booking_monitoring(request):
    """Monitor all bookings"""
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
    
    # Sort by date
    bookings.sort(key=lambda x: x['created_at'], reverse=True)
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = [b for b in bookings if b['status'] == status_filter]
    
    context = {
        'bookings': bookings,
        'total_bookings': len(bookings),
    }
    
    return render(request, 'supervisor/bookings/list.html', context)


@login_required
@require_role('subadmin')
def performance_reports(request):
    """View performance reports"""
    from orders.models import Order
    from goods.models import ListModel as Product
    
    # Date range
    days = int(request.GET.get('days', 7))
    start_date = timezone.now() - timedelta(days=days)
    
    # Order metrics
    orders = Order.objects.filter(created_at__gte=start_date)
    total_orders = orders.count()
    completed_orders = orders.filter(status='completed').count()
    pending_orders = orders.filter(status='pending').count()
    
    # Team performance
    team_members = User.objects.filter(role__role='staff')
    active_team = team_members.filter(last_login__gte=start_date).count()
    
    # Inventory
    from stock.models import StockListModel
    stocks = StockListModel.objects.all()
    low_stock = stocks.filter(can_order_stock__lte=10, can_order_stock__gt=0).count()
    out_of_stock = stocks.filter(can_order_stock=0).count()
    
    context = {
        'days': days,
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
        'team_members': team_members.count(),
        'active_team': active_team,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
    }
    
    return render(request, 'supervisor/reports/index.html', context)


@login_required
@require_role('superadmin', 'admin', 'subadmin')
def staff_management(request):
    """Supervisor-only staff management page - staff role CANNOT access this"""
    from django.contrib import messages
    
    # Get all staff members for management
    staff_users = User.objects.filter(role__role='staff')
    
    # Staff performance metrics
    from orders.models import Order
    staff_performance = []
    for staff in staff_users:
        orders_handled = Order.objects.filter(created_by=staff).count()
        total_sales = Order.objects.filter(created_by=staff, payment_status='paid').aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        staff_performance.append({
            'user': staff,
            'orders_handled': orders_handled,
            'total_sales': float(total_sales),
            'active': staff.is_active,
            'last_login': staff.last_login
        })
    
    # Team statistics
    total_staff = staff_users.count()
    active_staff = staff_users.filter(is_active=True).count()
    
    # Recent team activities
    recent_orders = Order.objects.filter(
        created_by__role__role='staff'
    ).select_related('created_by').order_by('-created_at')[:20]
    
    context = {
        'staff_performance': staff_performance,
        'total_staff': total_staff,
        'active_staff': active_staff,
        'inactive_staff': total_staff - active_staff,
        'recent_orders': recent_orders,
    }
    
    return render(request, 'supervisor/staff_management.html', context)

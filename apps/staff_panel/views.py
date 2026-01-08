from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.http import require_http_methods
from permissions.decorators import require_role
import json

@login_required
@require_role('staff', 'subadmin')
def staff_dashboard(request):
    """Staff dashboard with task-focused metrics"""
    from orders.models import Order
    from stock.models import StockListModel
    
    # Time periods
    today = timezone.now().date()
    week_ago = timezone.now() - timedelta(days=7)
    
    # My tasks (orders assigned or recent)
    my_orders_today = Order.objects.filter(created_at__date=today).count()
    pending_tasks = Order.objects.filter(status__in=['pending', 'confirmed']).count()
    processing_tasks = Order.objects.filter(status='processing').count()
    
    # Inventory alerts
    stocks = StockListModel.objects.all()
    low_stock = stocks.filter(can_order_stock__lte=10, can_order_stock__gt=0).count()
    out_of_stock = stocks.filter(can_order_stock=0).count()
    
    # Bookings to handle
    try:
        from rentals.models import RentalBooking
        pending_rentals = RentalBooking.objects.filter(status='pending').count()
    except:
        pending_rentals = 0
    
    try:
        from storage.models import StorageBooking
        pending_storage = StorageBooking.objects.filter(status='pending').count()
    except:
        pending_storage = 0
    
    # My activity
    my_activity_count = 0
    
    # Total tasks
    total_tasks = pending_tasks + processing_tasks + pending_rentals + pending_storage
    
    # Recent orders
    recent_orders = Order.objects.all().order_by('-created_at')[:10]
    
    context = {
        'my_orders_today': my_orders_today,
        'pending_tasks': pending_tasks,
        'processing_tasks': processing_tasks,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'pending_rentals': pending_rentals,
        'pending_storage': pending_storage,
        'total_tasks': total_tasks,
        'recent_orders': recent_orders,
    }
    
    return render(request, 'staff/dashboard.html', context)


@login_required
@require_role('staff', 'subadmin')
def my_tasks(request):
    """View my assigned tasks"""
    from orders.models import Order
    
    # Get orders that need processing
    tasks = Order.objects.filter(
        status__in=['pending', 'confirmed', 'processing']
    ).order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    context = {
        'tasks': tasks,
        'total_tasks': tasks.count(),
    }
    
    return render(request, 'staff/tasks/list.html', context)


@login_required
@require_role('staff', 'subadmin')
def task_detail(request, order_id):
    """View task details"""
    from orders.models import Order
    
    task = get_object_or_404(Order, id=order_id)
    
    context = {
        'task': task,
    }
    
    return render(request, 'staff/tasks/detail.html', context)


@login_required
@require_role('staff', 'subadmin')
@require_http_methods(["POST"])
def update_task_status(request, order_id):
    """Update task status"""
    from orders.models import Order
    
    task = get_object_or_404(Order, id=order_id)
    
    data = json.loads(request.body)
    new_status = data.get('status')
    
    # Staff can only update to processing
    allowed_statuses = ['processing']
    
    if new_status in allowed_statuses:
        task.status = new_status
        task.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Task status updated to {new_status}'
        })
    
    return JsonResponse({
        'success': False,
        'message': 'You can only mark tasks as processing'
    }, status=403)


@login_required
@require_role('staff', 'subadmin')
def inventory_check(request):
    """Check inventory levels"""
    from goods.models import ListModel as Product
    from stock.models import StockListModel
    
    products = Product.objects.all().order_by('goods_name')
    
    # Filter
    stock_filter = request.GET.get('stock')
    if stock_filter == 'low':
        low_stock_codes = StockListModel.objects.filter(
            can_order_stock__lte=10,
            can_order_stock__gt=0
        ).values_list('goods_code', flat=True)
        products = products.filter(goods_code__in=low_stock_codes)
    elif stock_filter == 'out':
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
    for product in products[:50]:  # Limit to 50
        stock = StockListModel.objects.filter(goods_code=product.goods_code).first()
        product.stock_qty = stock.goods_qty if stock else 0
        product.stock_available = stock.can_order_stock if stock else 0
        products_with_stock.append(product)
    
    context = {
        'products': products_with_stock,
        'total_products': len(products_with_stock),
    }
    
    return render(request, 'staff/inventory/list.html', context)


@login_required
@require_role('staff', 'subadmin')
def customer_orders(request):
    """View customer orders"""
    from orders.models import Order
    
    orders = Order.objects.all().order_by('-created_at')
    
    # Search
    search = request.GET.get('search')
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(customer_user__username__icontains=search)
        )
    
    context = {
        'orders': orders[:50],  # Limit to 50
        'total_orders': orders.count(),
    }
    
    return render(request, 'staff/orders/list.html', context)


@login_required
@require_role('staff')
def my_activity(request):
    """View my activity log"""
    # Get user's recent activity
    activity_log = []
    
    # This would typically track user actions
    # For now, show placeholder
    
    context = {
        'activity_log': activity_log,
    }
    
    return render(request, 'staff/activity/index.html', context)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db.models import Sum, Count, Q, Avg, F
from django.utils import timezone
from datetime import timedelta
import os

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

def is_team_member(user):
    # Allow all team roles to access dashboard (superadmin, admin, subadmin, supervisor, staff)
    from permissions.decorators import get_user_role
    user_role = get_user_role(user)
    return user_role in ['superadmin', 'admin', 'subadmin', 'supervisor', 'staff']

@login_required
@user_passes_test(is_team_member)
def superadmin_dashboard(request):
    from goods.models import ListModel as Product
    from stock.models import StockListModel, StockMovement, StockAlert
    from orders.models import Order
    from warehouse.models import ListModel as Warehouse
    from customer.models import ListModel as Customer
    from supplier.models import ListModel as Supplier
    from billing.models import Invoice
    from django.contrib.auth.models import User
    
    # System Health
    if PSUTIL_AVAILABLE:
        uptime = timezone.now() - timezone.datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc)
        uptime_str = f"{uptime.days}d {uptime.seconds//3600}h"
        storage_used = f"{psutil.disk_usage('/').percent}%"
    else:
        uptime_str = "N/A"
        storage_used = "N/A"
    
    # Inventory Metrics
    stocks = StockListModel.objects.all()
    total_skus = stocks.count()
    total_stock = stocks.aggregate(total=Sum('goods_qty'))['total'] or 0
    stock_on_hand = stocks.aggregate(total=Sum('onhand_stock'))['total'] or 0
    low_stock = stocks.filter(can_order_stock__lte=10, can_order_stock__gt=0).count()
    out_of_stock = stocks.filter(can_order_stock=0).count()
    
    # Stock Value Calculation
    products = Product.objects.all()
    stock_value = 0
    for stock in stocks:
        try:
            product = products.filter(goods_code=stock.goods_code).first()
            if product:
                stock_value += float(product.goods_price) * stock.goods_qty
        except:
            pass
    
    # Stock Movement (7 days)
    week_ago = timezone.now() - timedelta(days=7)
    movements_week = StockMovement.objects.filter(created_at__gte=week_ago)
    stock_in_week = movements_week.filter(movement_type='in').aggregate(total=Sum('quantity'))['total'] or 0
    stock_out_week = movements_week.filter(movement_type='out').aggregate(total=Sum('quantity'))['total'] or 0
    
    # Orders
    orders = Order.objects.all()
    total_orders = orders.count()
    pending_orders = orders.filter(status__in=['pending', 'confirmed']).count()
    completed_orders = orders.filter(status='completed').count()
    from stock.models import StockListModel, StockMovement
    from orders.models import Order
    from goods.models import ListModel as Product
    from customer.models import ListModel as Customer
    from datetime import datetime
    
    # Time-based greeting
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        greeting = "Good Morning"
    elif 12 <= current_hour < 17:
        greeting = "Good Afternoon"
    elif 17 <= current_hour < 21:
        greeting = "Good Evening"
    else:
        greeting = "Good Night"
    
    # Get user info
    user_name = request.user.get_full_name() or request.user.username
    
    month_start = timezone.now().replace(day=1)
    last_month_start = (month_start - timedelta(days=1)).replace(day=1)
    
    stocks = StockListModel.objects.all()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_customers = Customer.objects.count()
    
    # Monthly metrics
    monthly_orders = Order.objects.filter(created_at__gte=month_start).count()
    last_month_orders = Order.objects.filter(created_at__gte=last_month_start, created_at__lt=month_start).count()
    
    # Stock insights
    low_stock_count = stocks.filter(can_order_stock__lte=10, can_order_stock__gt=0).count()
    out_of_stock_count = stocks.filter(can_order_stock=0).count()
    in_stock_count = stocks.filter(can_order_stock__gt=10).count()
    
    # Calculate growth
    order_growth = 0
    if last_month_orders > 0:
        order_growth = ((monthly_orders - last_month_orders) / last_month_orders * 100)
    
    # Stock health percentage
    stock_health = 0
    if stocks.count() > 0:
        stock_health = round((in_stock_count / stocks.count() * 100), 1)
    
    # Warehouses
    total_warehouses = Warehouse.objects.filter(is_delete=False).count()
    
    # Recent activity
    recent_orders = orders.order_by('-created_at')[:5]
    
    # Additional metrics for template
    categories_count = Product.objects.values('goods_class').distinct().count()
    inbound_shipments = 0
    outbound_orders = pending_orders
    pending_sales_orders = pending_orders
    pending_purchase_orders = 0
    warehouse_utilization = "75%"
    top_warehouse = "Main Warehouse"
    inventory_turnover = "2.5x"
    days_inventory_remaining = "45 days"
    fast_movers = 12
    dead_stock = 3
    monthly_revenue = 0
    active_alerts = low_stock + out_of_stock
    recent_users = User.objects.filter(date_joined__gte=week_ago).count()
    
    context = {
        'greeting': greeting,
        'user_name': user_name,
        'current_time': timezone.now(),
        'total_products': total_products,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'monthly_orders': monthly_orders,
        'order_growth': round(order_growth, 1),
        'low_stock': low_stock_count,
        'out_of_stock': out_of_stock_count,
        'in_stock': in_stock_count,
        'stock_health_percent': stock_health,
        'total_skus': total_skus,
        'total_warehouses': total_warehouses,
        'stock_on_hand': stock_on_hand,
        'low_stock_items': low_stock,
        'out_of_stock_items': out_of_stock,
        'stock_value': stock_value,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'recent_orders': recent_orders,
        'system_health': 'Operational',
        'server_uptime': uptime_str,
        'storage_used': storage_used,
        'api_requests_today': 0,
        'now': timezone.now(),
        'categories_count': categories_count,
        'inbound_shipments': inbound_shipments,
        'outbound_orders': outbound_orders,
        'pending_sales_orders': pending_sales_orders,
        'pending_purchase_orders': pending_purchase_orders,
        'warehouse_utilization': warehouse_utilization,
        'top_warehouse': top_warehouse,
        'inventory_turnover': inventory_turnover,
        'days_inventory_remaining': days_inventory_remaining,
        'fast_movers': fast_movers,
        'dead_stock': dead_stock,
        'monthly_revenue': monthly_revenue,
        'active_alerts': active_alerts,
        'recent_users': recent_users,
        'total_stock_value': stock_value,
    }
    
    return render(request, 'dashboards/superadmin.html', context)

@login_required
@user_passes_test(is_team_member)
def dashboard_charts_api(request):
    from stock.models import StockMovement
    from orders.models import Order
    from goods.models import ListModel as Product
    
    # Try to import optional models
    try:
        from billing.models import Invoice
        billing_available = True
    except (ImportError, RuntimeError):
        billing_available = False
    
    days = int(request.GET.get('days', 7))
    
    # Revenue Chart Data - Use Invoice data for accurate revenue tracking
    revenue_labels = []
    revenue_data = []
    for i in range(days-1, -1, -1):
        day = timezone.now() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0)
        day_end = day_start + timedelta(days=1)
        
        # Get revenue from Invoices (most accurate)
        if billing_available:
            revenue = Invoice.objects.filter(
                created_at__gte=day_start,
                created_at__lt=day_end
            ).aggregate(total=Sum('grand_total'))['total'] or 0
            revenue = float(revenue)
        else:
            # Fallback to orders
            revenue = Order.objects.filter(
                created_at__gte=day_start,
                created_at__lt=day_end
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            revenue = float(revenue)
        
        revenue_labels.append(day.strftime('%d %b') if days>7 else day.strftime('%a'))
        revenue_data.append(round(revenue, 2))
    
    # Stock Movement Chart Data
    stock_labels = []
    stock_in_data = []
    stock_out_data = []
    for i in range(days-1, -1, -1):
        day = timezone.now() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0)
        day_end = day_start + timedelta(days=1)
        movements = StockMovement.objects.filter(created_at__gte=day_start, created_at__lt=day_end)
        stock_in = movements.filter(movement_type='in').aggregate(total=Sum('quantity'))['total'] or 0
        stock_out = movements.filter(movement_type='out').aggregate(total=Sum('quantity'))['total'] or 0
        stock_labels.append(day.strftime('%d %b') if days>7 else day.strftime('%a'))
        stock_in_data.append(abs(stock_in))
        stock_out_data.append(abs(stock_out))
    
    # Top Selling Categories
    categories = Product.objects.values('goods_class').annotate(count=Count('id')).order_by('-count')[:5]
    category_labels = [c['goods_class'] or 'Uncategorized' for c in categories]
    category_data = [c['count'] for c in categories]
    
    # Order Status Distribution
    order_statuses = Order.objects.values('status').annotate(count=Count('id'))
    status_labels = [s['status'].title() for s in order_statuses]
    status_data = [s['count'] for s in order_statuses]
    
    return JsonResponse({
        'revenue': {'labels': revenue_labels, 'data': revenue_data},
        'stock': {'labels': stock_labels, 'in': stock_in_data, 'out': stock_out_data},
        'categories': {'labels': category_labels, 'data': category_data},
        'order_status': {'labels': status_labels, 'data': status_data}
    })

@login_required
@user_passes_test(is_team_member)
def dashboard_metrics_api(request):
    from stock.models import StockListModel, StockMovement
    from orders.models import Order
    from goods.models import ListModel as Product
    from customer.models import ListModel as Customer
   
    # Try importing optional apps - they may not be in INSTALLED_APPS
    try:
        from apps.rentals.models import RentalBooking
        rentals_available = True
    except (ImportError, RuntimeError):
        rentals_available = False
    
    try:
        from apps.lockers.models import Locker
        lockers_available = True
    except (ImportError, RuntimeError):
        lockers_available = False
    
    try:
        from coupons.models import Coupon, CouponUsage
        coupons_available = True
    except (ImportError, RuntimeError):
        coupons_available = False
    
    try:
        from billing.models import Invoice
        billing_available = True
    except (ImportError, RuntimeError):
        billing_available = False
    
    month_start = timezone.now().replace(day=1)
    last_month_start = (month_start - timedelta(days=1)).replace(day=1)
    stocks = StockListModel.objects.all()
    
    # Revenue metrics
    if billing_available:
        total_revenue = Invoice.objects.filter(status='paid').aggregate(total=Sum('grand_total'))['total'] or 0
        monthly_revenue = Invoice.objects.filter(status='paid', created_at__gte=month_start).aggregate(total=Sum('grand_total'))['total'] or 0
        last_month_revenue = Invoice.objects.filter(status='paid', created_at__gte=last_month_start, created_at__lt=month_start).aggregate(total=Sum('grand_total'))['total'] or 0
    else:
        total_revenue = 0
        monthly_revenue = 0
        last_month_revenue = 0
    
    total_orders = Order.objects.count()
    monthly_orders = Order.objects.filter(created_at__gte=month_start).count()
    last_month_orders = Order.objects.filter(created_at__gte=last_month_start, created_at__lt=month_start).count()
    
    total_products = Product.objects.count()
    monthly_products = Product.objects.filter(create_time__gte=month_start).count()
    
    total_customers = Customer.objects.count()
    monthly_customers = Customer.objects.filter(create_time__gte=month_start).count()
    
    revenue_change = ((monthly_revenue - last_month_revenue) / last_month_revenue * 100) if last_month_revenue > 0 else 0
    orders_change = ((monthly_orders - last_month_orders) / last_month_orders * 100) if last_month_orders > 0 else 0
    
    data = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_revenue': float(total_revenue),
        'monthly_revenue': float(monthly_revenue),
        'revenue_change': round(revenue_change, 1),
        'orders_change': round(orders_change, 1),
        'new_products_month': monthly_products,
        'new_customers_month': monthly_customers,
        'total_skus': stocks.count(),
        'low_stock': stocks.filter(can_order_stock__lte=10, can_order_stock__gt=0).count(),
        'out_of_stock': stocks.filter(can_order_stock=0).count(),
        'pending_orders': Order.objects.filter(status__in=['pending', 'confirmed']).count(),
        'active_rentals': RentalBooking.objects.filter(status='active').count() if rentals_available else 0,
        'available_lockers': Locker.objects.filter(status='available').count() if lockers_available else 0,
        'occupied_lockers': Locker.objects.filter(status='occupied').count() if lockers_available else 0,
        'active_coupons': Coupon.objects.filter(is_active=True).count() if coupons_available else 0,
        'coupon_redemptions': CouponUsage.objects.count() if coupons_available else 0,
        'timestamp': timezone.now().isoformat()
    }
    
    return JsonResponse(data)

@login_required
@user_passes_test(is_team_member)
def dashboard_heatmap_api(request):
    from warehouse.models import ListModel as Warehouse
    from orders.models import Order
    
    warehouses = Warehouse.objects.all()[:12]
    heatmap_data = []
    
    for warehouse in warehouses:
        order_count = Order.objects.filter(warehouse_id=warehouse.id).count() if hasattr(Order, 'warehouse_id') else 0
        heatmap_data.append({
            'name': warehouse.warehouse_name[:15],
            'orders': order_count
        })
    
    return JsonResponse({'warehouses': heatmap_data})

@login_required
@user_passes_test(is_team_member)
def dashboard_bubble_api(request):
    from goods.models import ListModel as Product
    from orders.models import Order, OrderItem
    from django.db.models import Sum, Count
    
    products = Product.objects.all()[:20]
    bubble_data = []
    
    for product in products:
        try:
            sales_count = OrderItem.objects.filter(product_id=product.id).count() if hasattr(OrderItem, 'product_id') else 0
            revenue = float(product.goods_price) * sales_count if sales_count > 0 else 0
            stock = product.goods_stock if hasattr(product, 'goods_stock') else 0
            
            if sales_count > 0 or revenue > 0:
                bubble_data.append({
                    'x': sales_count,
                    'y': revenue,
                    'r': min(stock / 10, 30) if stock > 0 else 5
                })
        except:
            pass
    
    return JsonResponse({'products': bubble_data})

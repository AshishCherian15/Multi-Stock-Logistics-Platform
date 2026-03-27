from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from goods.models import ListModel
from stock.models import StockListModel, StockAlert
# from orders.models import SalesOrder, PurchaseOrder
from customer.models import ListModel as CustomerModel
from billing.models import Invoice

from permissions.decorators import require_permission

@require_permission('analytics', 'view')
def dashboard(request):
    return render(request, 'analytics/dashboard.html')

@require_permission('analytics', 'view')
def advanced_analytics(request):
    return render(request, 'analytics/advanced_analytics.html')

@require_permission('analytics', 'view')
def analytics_data_api(request):
    from orders.models import Order
    from datetime import datetime, timedelta
    
    total_products = ListModel.objects.filter(is_delete=False).count()
    total_orders = Order.objects.count()
    total_customers = CustomerModel.objects.filter(is_delete=False).count()
    total_revenue = Order.objects.filter(status='delivered').aggregate(total=Sum('total_amount'))['total'] or 0
    
    revenue_labels = []
    revenue_data = []
    for i in range(7):
        day = timezone.now().date() - timedelta(days=6-i)
        day_revenue = Order.objects.filter(created_at__date=day, status='delivered').aggregate(total=Sum('total_amount'))['total'] or 0
        revenue_labels.append(day.strftime('%a'))
        revenue_data.append(float(day_revenue))
    
    # Get actual category distribution from products
    category_data_raw = ListModel.objects.filter(is_delete=False).values('goods_class').annotate(
        count=Count('id')
    ).order_by('-count')[:4]
    
    category_labels = [item['goods_class'] or 'Uncategorized' for item in category_data_raw]
    category_data = [item['count'] for item in category_data_raw]
    
    # Fill with zeros if less than 4 categories
    while len(category_labels) < 4:
        category_labels.append('Other')
        category_data.append(0)
    
    return JsonResponse({
        'total_products': total_products,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_revenue': float(total_revenue),
        'revenue_labels': revenue_labels,
        'revenue_data': revenue_data,
        'category_labels': category_labels,
        'category_data': category_data
    })

@require_permission('analytics', 'view')
def overview_api(request):
    from orders.models import Order
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Products
    total_products = ListModel.objects.filter(is_delete=False).count()
    low_stock = StockListModel.objects.filter(onhand_stock__lte=10).count()
    
    # Orders
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status__in=['pending', 'confirmed']).count()
    
    # Revenue
    total_revenue = Invoice.objects.filter(status='paid').aggregate(total=Sum('grand_total'))['total'] or 0
    monthly_revenue = Invoice.objects.filter(status='paid', created_at__gte=month_ago).aggregate(total=Sum('grand_total'))['total'] or 0
    
    # Customers
    total_customers = CustomerModel.objects.filter(is_delete=False).count()
    new_customers = CustomerModel.objects.filter(is_delete=False, create_time__gte=month_ago).count()
    
    # Alerts
    critical_alerts = StockAlert.objects.filter(alert_level='critical', is_resolved=False).count()
    
    return JsonResponse({
        'products': {'total': total_products, 'low_stock': low_stock},
        'orders': {'total': total_orders, 'pending': pending_orders},
        'revenue': {'total': float(total_revenue), 'monthly': float(monthly_revenue)},
        'customers': {'total': total_customers, 'new': new_customers},
        'alerts': {'critical': critical_alerts}
    })

@require_permission('analytics', 'view')
def sales_chart_api(request):
    days = int(request.GET.get('days', 30))
    start_date = timezone.now().date() - timedelta(days=days)
    
    invoices = Invoice.objects.filter(created_at__gte=start_date, status='paid').values('created_at__date').annotate(total=Sum('grand_total')).order_by('created_at__date')
    
    labels = []
    data = []
    for inv in invoices:
        labels.append(inv['created_at__date'].strftime('%Y-%m-%d'))
        data.append(float(inv['total']))
    
    return JsonResponse({'labels': labels, 'data': data})

@require_permission('analytics', 'view')
def inventory_chart_api(request):
    products = ListModel.objects.values('goods_class').annotate(count=Count('id'))
    
    labels = [p['goods_class'] for p in products]
    data = [p['count'] for p in products]
    
    return JsonResponse({'labels': labels, 'data': data})

@require_permission('analytics', 'view')
def top_products_api(request):
    limit = int(request.GET.get('limit', 10))
    
    products = StockListModel.objects.order_by('-onhand_stock')[:limit]
    
    data = [{
        'name': p.goods_desc,
        'code': p.goods_code,
        'qty': p.onhand_stock,
        'class': 'Stock'
    } for p in products]
    
    return JsonResponse({'products': data})

@require_permission('analytics', 'view')
def alerts_summary_api(request):
    critical = StockAlert.objects.filter(alert_level='critical', is_resolved=False).count()
    warning = StockAlert.objects.filter(alert_level='warning', is_resolved=False).count()
    info = StockAlert.objects.filter(alert_level='info', is_resolved=False).count()
    
    return JsonResponse({
        'critical': critical,
        'warning': warning,
        'info': info,
        'total': critical + warning + info
    })

@require_permission('analytics', 'view')
def user_activity_api(request):
    days = int(request.GET.get('days', 7))
    start_date = timezone.now() - timedelta(days=days)
    
    from users.models import UserActivity
    activities = UserActivity.objects.filter(timestamp__gte=start_date).values('timestamp__date').annotate(count=Count('id')).order_by('timestamp__date')
    
    labels = []
    data = []
    for act in activities:
        labels.append(act['timestamp__date'].strftime('%Y-%m-%d'))
        data.append(act['count'])
    
    return JsonResponse({'labels': labels, 'data': data})

@require_permission('analytics', 'view')
def revenue_breakdown_api(request):
    month_ago = timezone.now().date() - timedelta(days=30)
    
    by_type = Invoice.objects.filter(status='paid', created_at__gte=month_ago).values('invoice_type').annotate(total=Sum('grand_total'))
    
    labels = []
    data = []
    for item in by_type:
        labels.append(item['invoice_type'])
        data.append(float(item['total']))
    
    return JsonResponse({'labels': labels, 'data': data})

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db import connection, models
from goods.models import ListModel
from stock.models import StockListModel
from orders.models import Order
from customer.models import ListModel as CustomerModel
from permissions.decorators import require_role
import json

@login_required
@require_role('superadmin', 'admin', 'supervisor', 'staff')
def dashboard_metrics(request):
    return JsonResponse({
        'revenue': Order.objects.filter(status='delivered').aggregate(total=models.Sum('total_amount'))['total'] or 0,
        'orders': Order.objects.count(),
        'products': ListModel.objects.filter(is_delete=False).count(),
        'customers': CustomerModel.objects.filter(is_delete=False).count(),
        'low_stock': StockListModel.objects.filter(goods_qty__lt=10).count()
    })

@login_required
@require_role('superadmin', 'admin')
@require_http_methods(["POST"])
def bulk_product_action(request):
    data = json.loads(request.body)
    action = data.get('action')
    ids = data.get('ids', [])
    
    if action == 'delete':
        ListModel.objects.filter(id__in=ids).update(is_delete=True)
        return JsonResponse({'status': 'success', 'message': f'{len(ids)} products deleted'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid action'})

@login_required
@require_role('superadmin', 'admin', 'supervisor', 'staff')
def order_statistics(request):
    from django.db.models import Count, Sum
    stats = Order.objects.aggregate(
        total=Count('id'),
        pending=Count('id', filter=models.Q(status='pending')),
        delivered=Count('id', filter=models.Q(status='delivered')),
        revenue=Sum('total_amount')
    )
    return JsonResponse(stats)

@login_required
@require_role('superadmin', 'admin', 'supervisor', 'staff')
def inventory_alerts(request):
    low_stock = StockListModel.objects.filter(goods_qty__lt=10).values('goods_code', 'goods_qty')[:20]
    out_stock = StockListModel.objects.filter(goods_qty=0).values('goods_code')[:20]
    
    return JsonResponse({
        'low_stock': list(low_stock),
        'out_of_stock': list(out_stock),
        'low_count': low_stock.count(),
        'out_count': out_stock.count()
    })

@login_required
@require_role('superadmin', 'admin')
def audit_logs(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM audit_auditlog ORDER BY created_at DESC LIMIT 50')
        columns = [col[0] for col in cursor.description]
        logs = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return JsonResponse({'logs': logs})

@login_required
@require_role('superadmin', 'admin')
def get_settings(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT key, value, category FROM settings_systemsetting')
        settings = {row[0]: {'value': row[1], 'category': row[2]} for row in cursor.fetchall()}
    
    return JsonResponse({'settings': settings})

@login_required
@require_role('superadmin', 'admin')
@require_http_methods(["POST"])
def save_settings(request):
    data = json.loads(request.body)
    
    with connection.cursor() as cursor:
        for key, value in data.items():
            cursor.execute('''
                INSERT OR REPLACE INTO settings_systemsetting (key, value, category, updated_at)
                VALUES (?, ?, ?, datetime('now'))
            ''', [key, value, 'general'])
    
    return JsonResponse({'status': 'success', 'message': 'Settings saved'})

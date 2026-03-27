from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import StockAlert, StockListModel
from goods.models import ListModel

@login_required
def stock_alerts(request):
    alerts = StockAlert.objects.filter(is_resolved=False)
    
    # Get current low stock items
    low_stock_items = []
    products = ListModel.objects.filter(is_delete=False)
    
    for product in products:
        stock = StockListModel.objects.filter(goods_code=product.goods_code).first()
        if stock and stock.goods_qty <= product.min_stock_level:
            low_stock_items.append({
                'product': product,
                'stock': stock,
                'level': 'critical' if stock.goods_qty <= product.reorder_point else 'warning'
            })
    
    context = {
        'alerts': alerts,
        'low_stock_items': low_stock_items,
        'critical_count': len([i for i in low_stock_items if i['level'] == 'critical']),
        'warning_count': len([i for i in low_stock_items if i['level'] == 'warning']),
    }
    return render(request, 'stock/alerts.html', context)

@login_required
def check_alerts_api(request):
    """API endpoint to check for low stock alerts"""
    alerts = []
    products = ListModel.objects.filter(is_delete=False)
    
    for product in products:
        stock = StockListModel.objects.filter(goods_code=product.goods_code).first()
        if stock and stock.goods_qty < 10:
            level = 'critical' if stock.goods_qty == 0 else 'warning'
            alerts.append({
                'message': f'{product.goods_desc} is low on stock ({stock.goods_qty} remaining)',
                'level': level
            })
    
    return JsonResponse({
        'status': 'success',
        'alert_count': len(alerts),
        'critical': len([a for a in alerts if a['level'] == 'critical']),
        'warning': len([a for a in alerts if a['level'] == 'warning']),
        'alerts': alerts
    })

@login_required
def resolve_alert(request, alert_id):
    """Mark alert as resolved"""
    if request.method == 'POST':
        alert = StockAlert.objects.get(id=alert_id)
        alert.is_resolved = True
        from django.utils import timezone
        alert.resolved_at = timezone.now()
        alert.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

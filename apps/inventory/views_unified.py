from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from permissions.decorators import require_permission, require_role

try:
    from stock.models import StockListModel, StockMovement, StockAlert
    STOCK_AVAILABLE = True
except ImportError:
    STOCK_AVAILABLE = False

from goods.models import ListModel as Product

@login_required
@require_role('superadmin', 'admin', 'supervisor', 'staff')
def unified_inventory(request):
    if not STOCK_AVAILABLE:
        from inventory.models import InventoryTransaction
        transactions = InventoryTransaction.objects.order_by('-created_at')[:10]
        context = {
            'stocks': [],
            'total_products': Product.objects.count(),
            'low_stock_count': 0,
            'out_of_stock_count': 0,
            'total_value': 0,
            'recent_movements': transactions,
            'alerts': [],
            'active_alerts': 0,
            'categories': Product.objects.values('goods_class').annotate(count=Count('id')),
        }
        return render(request, 'inventory/unified_dashboard.html', context)
    
    # Stock Levels
    stocks = StockListModel.objects.all()
    total_products = stocks.count()
    low_stock = stocks.filter(can_order_stock__lte=10, can_order_stock__gt=0).count()
    out_of_stock = stocks.filter(can_order_stock=0).count()
    total_value = stocks.aggregate(total=Sum('goods_qty'))['total'] or 0
    
    # Recent Movements
    recent_movements = StockMovement.objects.order_by('-created_at')[:10]
    
    # Active Alerts
    alerts = StockAlert.objects.filter(is_resolved=False).order_by('-created_at')
    
    # Categories
    categories = Product.objects.values('goods_class').annotate(count=Count('id'))
    
    context = {
        'stocks': stocks[:50],
        'total_products': total_products,
        'low_stock_count': low_stock,
        'out_of_stock_count': out_of_stock,
        'total_value': total_value,
        'recent_movements': recent_movements,
        'alerts': alerts,
        'active_alerts': alerts.count(),
        'categories': categories,
    }
    
    return render(request, 'inventory/unified_dashboard.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from .models import InventoryTransaction, StockAlert, InventoryReport
from goods.models import ListModel as Product
from warehouse.models import ListModel as Warehouse
from stock.models import StockListModel as Stock
from permissions.decorators import require_role, require_permission
import uuid
from datetime import datetime, timedelta

@login_required
@require_permission('inventory', 'view')
def inventory_dashboard(request):
    from stock.models import StockMovement
    
    # Get summary data
    total_products = Product.objects.filter(is_delete=False).count()
    total_warehouses = Warehouse.objects.filter(is_delete=False).count()
    low_stock_alerts = Stock.objects.filter(goods_qty__lt=20).count()
    
    # Get recent stock movements with product details
    recent_movements = StockMovement.objects.select_related('user').order_by('-created_at')[:10]
    
    # Enrich movements with product data
    movements_data = []
    for movement in recent_movements:
        try:
            product = Product.objects.get(goods_code=movement.goods_code)
            stock = Stock.objects.filter(goods_code=movement.goods_code).first()
            movements_data.append({
                'goods_code': movement.goods_code,
                'product_name': product.goods_desc,
                'product_image': stock.goods_image.url if stock and hasattr(stock, 'goods_image') and stock.goods_image else None,
                'movement_type': movement.movement_type,
                'quantity': movement.quantity,
                'reason': movement.reason,
                'created_at': movement.created_at,
                'user': movement.user
            })
        except:
            pass
    
    context = {
        'total_products': total_products,
        'total_warehouses': total_warehouses,
        'low_stock_alerts': low_stock_alerts,
        'recent_transactions': movements_data,
    }
    return render(request, 'inventory/dashboard.html', context)

@login_required
@require_role('superadmin', 'admin', 'supervisor', 'staff')
def stock_movements(request):
    transactions = InventoryTransaction.objects.all().order_by('-created_at')
    
    # Filter by type if specified
    transaction_type = request.GET.get('type')
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    context = {
        'transactions': transactions,
        'transaction_types': InventoryTransaction.TRANSACTION_TYPES,
    }
    return render(request, 'inventory/movements.html', context)

@login_required
@require_role('superadmin', 'admin', 'supervisor', 'staff')
def stock_alerts(request):
    alerts = StockAlert.objects.filter(is_resolved=False).order_by('-created_at')
    
    context = {
        'alerts': alerts,
        'total_alerts': alerts.count(),
        'low_stock_count': alerts.filter(alert_type='low_stock').count(),
        'out_of_stock_count': alerts.filter(alert_type='out_of_stock').count(),
    }
    return render(request, 'inventory/alerts.html', context)

@require_permission('inventory', 'create')
def create_transaction(request):
    if request.method == 'POST':
        product_id = request.POST.get('product')
        warehouse_id = request.POST.get('warehouse')
        transaction_type = request.POST.get('transaction_type')
        quantity = int(request.POST.get('quantity'))
        notes = request.POST.get('notes', '')
        
        transaction = InventoryTransaction.objects.create(
            product_id=product_id,
            warehouse_id=warehouse_id,
            transaction_type=transaction_type,
            quantity=quantity,
            reference_number=f"TXN-{uuid.uuid4().hex[:8].upper()}",
            notes=notes,
            created_by=request.user
        )
        
        messages.success(request, f'Transaction {transaction.reference_number} created successfully!')
        return redirect('inventory:movements')
    
    context = {
        'products': Product.objects.filter(is_delete=False),
        'warehouses': Warehouse.objects.filter(is_delete=False),
        'transaction_types': InventoryTransaction.TRANSACTION_TYPES,
    }
    return render(request, 'inventory/create_transaction.html', context)

@login_required
def resolve_alert(request, alert_id):
    alert = get_object_or_404(StockAlert, id=alert_id)
    alert.is_resolved = True
    alert.resolved_at = datetime.now()
    alert.save()
    
    messages.success(request, 'Alert resolved successfully!')
    return redirect('inventory:alerts')

@login_required
@require_permission('inventory', 'edit')
def get_stock_api(request, stock_id):
    try:
        stock = get_object_or_404(Stock, id=stock_id)
        return JsonResponse({
            'success': True,
            'goods_code': stock.goods_code,
            'goods_desc': stock.goods_desc,
            'onhand_stock': stock.onhand_stock if hasattr(stock, 'onhand_stock') else stock.goods_qty,
            'can_order_stock': stock.can_order_stock,
            'ordered_stock': stock.ordered_stock,
            'damage_stock': getattr(stock, 'damage_stock', 0),
            'supplier': getattr(stock, 'supplier', ''),
            'goods_image': stock.goods_image.url if hasattr(stock, 'goods_image') and stock.goods_image else None
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=404)

@login_required
@require_permission('inventory', 'create')
def create_stock_api(request):
    if request.method == 'POST':
        try:
            stock = Stock.objects.create(
                goods_code=request.POST['goods_code'],
                goods_desc=request.POST['goods_desc'],
                goods_qty=int(request.POST.get('onhand_stock', 0)),
                onhand_stock=int(request.POST.get('onhand_stock', 0)),
                can_order_stock=int(request.POST.get('can_order_stock', 0)),
                ordered_stock=int(request.POST.get('ordered_stock', 0)),
                damage_stock=int(request.POST.get('damage_stock', 0)),
                supplier=request.POST.get('supplier', ''),
                openid=request.user.username
            )
            if 'goods_image' in request.FILES:
                stock.goods_image = request.FILES['goods_image']
                stock.save()
            return JsonResponse({'success': True, 'id': stock.id})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    return JsonResponse({'success': False, 'message': 'POST required'}, status=405)

@login_required
@require_permission('inventory', 'edit')
def update_stock_api(request, stock_id):
    if request.method == 'POST':
        try:
            stock = get_object_or_404(Stock, id=stock_id)
            stock.goods_code = request.POST.get('goods_code', stock.goods_code)
            stock.goods_desc = request.POST.get('goods_desc', stock.goods_desc)
            onhand = int(request.POST.get('onhand_stock', stock.goods_qty))
            stock.goods_qty = onhand
            stock.onhand_stock = onhand
            stock.can_order_stock = int(request.POST.get('can_order_stock', stock.can_order_stock))
            stock.ordered_stock = int(request.POST.get('ordered_stock', stock.ordered_stock))
            stock.damage_stock = int(request.POST.get('damage_stock', getattr(stock, 'damage_stock', 0)))
            stock.supplier = request.POST.get('supplier', getattr(stock, 'supplier', ''))
            if 'goods_image' in request.FILES:
                stock.goods_image = request.FILES['goods_image']
            stock.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    return JsonResponse({'success': False, 'message': 'POST required'}, status=405)

@login_required
@require_permission('inventory', 'delete')
def delete_stock_api(request, stock_id):
    if request.method == 'POST':
        try:
            stock = get_object_or_404(Stock, id=stock_id)
            stock.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    return JsonResponse({'success': False, 'message': 'POST required'}, status=405)

@login_required
@require_permission('inventory', 'edit')
def update_qty_api(request, stock_id):
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            stock = get_object_or_404(Stock, id=stock_id)
            field = data.get('field')
            value = int(data.get('value', 0))
            
            if field == 'onhand':
                stock.goods_qty = value
                stock.onhand_stock = value
            elif field == 'available':
                stock.can_order_stock = value
            
            stock.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    return JsonResponse({'success': False, 'message': 'POST required'}, status=405)
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from stock.models import StockListModel, StockMovement
from permissions.decorators import require_permission
import json
import csv
import io

@login_required
@require_permission('inventory', 'view')
@require_http_methods(["GET"])
def get_stock(request, stock_id):
    stock = get_object_or_404(StockListModel, id=stock_id)
    return JsonResponse({
        'goods_code': stock.goods_code,
        'goods_desc': stock.goods_desc,
        'onhand_stock': stock.onhand_stock,
        'can_order_stock': stock.can_order_stock,
        'ordered_stock': stock.ordered_stock,
        'goods_image': stock.goods_image.url if stock.goods_image else None,
    })

@login_required
@require_permission('inventory', 'create')
@require_http_methods(["POST"])
def create_stock(request):
    try:
        goods_code = request.POST.get('goods_code')
        goods_desc = request.POST.get('goods_desc')
        onhand_stock = int(request.POST.get('onhand_stock', 0))
        can_order_stock = int(request.POST.get('can_order_stock', 0))
        ordered_stock = int(request.POST.get('ordered_stock', 0))
        goods_image = request.FILES.get('goods_image')
        
        stock = StockListModel.objects.create(
            goods_code=goods_code,
            goods_desc=goods_desc,
            onhand_stock=onhand_stock,
            goods_qty=onhand_stock,
            can_order_stock=can_order_stock,
            ordered_stock=ordered_stock,
            goods_image=goods_image,
            openid=request.user.openid if hasattr(request.user, 'openid') else 'admin'
        )
        
        StockMovement.objects.create(
            goods_code=goods_code,
            movement_type='in',
            quantity=onhand_stock,
            reason='Initial stock',
            user=request.user
        )
        
        return JsonResponse({'success': True, 'message': 'Stock created successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@require_permission('inventory', 'edit')
@require_http_methods(["POST"])
def update_stock(request, stock_id):
    try:
        stock = get_object_or_404(StockListModel, id=stock_id)
        
        stock.goods_code = request.POST.get('goods_code', stock.goods_code)
        stock.goods_desc = request.POST.get('goods_desc', stock.goods_desc)
        stock.onhand_stock = int(request.POST.get('onhand_stock', stock.onhand_stock))
        stock.goods_qty = stock.onhand_stock
        stock.can_order_stock = int(request.POST.get('can_order_stock', stock.can_order_stock))
        stock.ordered_stock = int(request.POST.get('ordered_stock', stock.ordered_stock))
        
        if request.FILES.get('goods_image'):
            stock.goods_image = request.FILES.get('goods_image')
        
        stock.save()
        
        return JsonResponse({'success': True, 'message': 'Stock updated successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@require_permission('inventory', 'delete')
@require_http_methods(["POST"])
def delete_stock(request, stock_id):
    try:
        stock = get_object_or_404(StockListModel, id=stock_id)
        stock.delete()
        return JsonResponse({'success': True, 'message': 'Stock deleted successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@require_permission('inventory', 'edit')
@require_http_methods(["POST"])
def update_qty(request, stock_id):
    try:
        data = json.loads(request.body)
        stock = get_object_or_404(StockListModel, id=stock_id)
        field = data.get('field')
        value = int(data.get('value', 0))
        
        if field == 'onhand':
            stock.onhand_stock = value
            stock.goods_qty = value
        elif field == 'available':
            stock.can_order_stock = value
        
        stock.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@require_permission('inventory', 'create')
@require_http_methods(["POST"])
def bulk_upload(request):
    try:
        file = request.FILES.get('bulk_file')
        if not file:
            return JsonResponse({'success': False, 'message': 'No file uploaded'})
        
        decoded_file = file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        
        count = 0
        for row in reader:
            StockListModel.objects.create(
                goods_code=row['goods_code'],
                goods_desc=row['goods_desc'],
                onhand_stock=int(row['onhand_stock']),
                goods_qty=int(row['onhand_stock']),
                can_order_stock=int(row['can_order_stock']),
                openid=request.user.openid if hasattr(request.user, 'openid') else 'admin'
            )
            count += 1
        
        return JsonResponse({'success': True, 'count': count})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

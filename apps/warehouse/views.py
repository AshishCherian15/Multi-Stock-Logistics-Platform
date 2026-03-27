from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Sum, Count
from .models import ListModel
from .serializers import WarehouseSerializer
from permissions.decorators import require_permission, require_role
from stock.models import StockListModel
from goods.models import ListModel as GoodsModel

class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = ListModel.objects.filter(is_delete=False)
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]

@require_permission('warehouses', 'view')
def warehouse_management_view(request):
    warehouses = ListModel.objects.filter(is_delete=False)
    total_stock = StockListModel.objects.aggregate(total=Sum('goods_qty'))['total'] or 0
    context = {
        'warehouses': warehouses,
        'total_warehouses': warehouses.count(),
        'total_items': total_stock,
    }
    return render(request, 'warehouse/enhanced_warehouse.html', context)

@require_permission('warehouses', 'create')
@require_http_methods(["POST"])
def create_warehouse(request):
    import json
    data = json.loads(request.body)
    warehouse = ListModel.objects.create(
        warehouse_name=data.get('warehouse_name', data.get('name', '')),
        warehouse_city=data.get('warehouse_city', data.get('location', '')),
        warehouse_address=data.get('warehouse_address', ''),
        warehouse_contact=data.get('warehouse_contact', ''),
        warehouse_manager=data.get('warehouse_manager', ''),
        warehouse_image=data.get('warehouse_image', ''),
        creater=data.get('creater', request.user.username)
    )
    return JsonResponse({'success': True, 'id': warehouse.id})

@api_view(['GET'])
def warehouse_stats(request):
    warehouses = ListModel.objects.filter(is_delete=False)
    total_stock = StockListModel.objects.aggregate(total=Sum('goods_qty'))['total'] or 0
    
    # Calculate pending transfers from stock movements
    from stock.models import StockMovement
    from django.utils import timezone
    from datetime import timedelta
    pending_transfers = StockMovement.objects.filter(
        movement_type='adjust',
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    # Calculate capacity used (percentage of stock vs theoretical max)
    # Assuming each warehouse can hold 10000 units
    max_capacity = warehouses.count() * 10000
    capacity_used = int((total_stock / max_capacity * 100)) if max_capacity > 0 else 0
    
    return Response({
        'total_warehouses': warehouses.count(),
        'total_items': total_stock,
        'pending_transfers': pending_transfers,
        'capacity_used': capacity_used
    })

@api_view(['GET'])
def zone_details(request, zone_id):
    stocks = StockListModel.objects.filter(goods_code__icontains=zone_id)[:10]
    items = [{'code': s.goods_code, 'desc': s.goods_desc, 'qty': s.goods_qty} for s in stocks]
    current_stock = sum(s.goods_qty for s in stocks)
    
    # Calculate capacity based on actual stock
    # Assuming zone capacity is 5x current stock or minimum 1000
    capacity = max(current_stock * 5, 1000)
    
    return Response({
        'zone': zone_id,
        'items': items,
        'capacity': capacity,
        'current': current_stock
    })

@api_view(['GET', 'DELETE'])
@require_permission('warehouses', 'view')
def warehouse_detail(request, pk):
    try:
        warehouse = ListModel.objects.get(id=pk, is_delete=False)
        if request.method == 'DELETE':
            # Only SuperAdmin can delete warehouses
            from permissions.decorators import get_user_role
            if get_user_role(request.user) != 'superadmin':
                return Response({'success': False, 'error': 'Only SuperAdmin can delete warehouses'}, status=403)
            warehouse.is_delete = True
            warehouse.save()
            return Response({'success': True, 'message': 'Warehouse deleted'})
        return Response({'success': True, 'data': WarehouseSerializer(warehouse).data})
    except ListModel.DoesNotExist:
        return Response({'success': False, 'error': 'Warehouse not found'}, status=404)

@api_view(['GET'])
def products_list(request):
    products = GoodsModel.objects.filter(is_delete=False)[:100]
    data = [{'id': p.id, 'code': p.goods_code, 'name': p.goods_desc} for p in products]
    return Response(data)
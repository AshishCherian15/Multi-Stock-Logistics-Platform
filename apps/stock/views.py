from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from .models import StockListModel, StockAlert, StockMovement
from .serializers import StockSerializer
from permissions.decorators import require_permission
import csv
import io
import json
from datetime import datetime

class StockViewSet(viewsets.ModelViewSet):
    queryset = StockListModel.objects.all()
    serializer_class = StockSerializer
    # Custom permission class defined below
    permission_classes = [] 

    def get_queryset(self):
        """
        SuperAdmin sees all stock.
        Others see only their store's stock (filtered by openid).
        """
        user = self.request.user
        if user.is_superuser:
            return StockListModel.objects.all()
        
        try:
            from permissions.decorators import get_user_role
            role = get_user_role(user)
            if role == 'superadmin':
                return StockListModel.objects.all()
        except:
            pass
        
        openid = getattr(user, 'openid', user.username)
        return StockListModel.objects.filter(openid=openid)

    def get_permissions(self):
        from permissions.decorators import check_permission
        from rest_framework.permissions import BasePermission

        class StockPermission(BasePermission):
            def has_permission(self, request, view):
                if not request.user.is_authenticated:
                    return False
                if request.method == 'GET':
                    return check_permission(request.user, 'stock', 'view')
                elif request.method == 'POST':
                    return check_permission(request.user, 'stock', 'create')
                elif request.method in ['PUT', 'PATCH']:
                    return check_permission(request.user, 'stock', 'adjust')
                elif request.method == 'DELETE':
                    return check_permission(request.user, 'stock', 'delete')
                return False
        
        return [StockPermission()]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['supplier']
    search_fields = ['goods_code', 'goods_desc']

@require_permission('stock', 'view')  # Stock view permission
def stock_dashboard(request):
    # Get filtered stock based on user role
    from permissions.decorators import get_user_role
    if request.user.is_superuser or get_user_role(request.user) == 'superadmin':
        stocks = StockListModel.objects.all().order_by('can_order_stock')
        alerts = StockAlert.objects.filter(is_resolved=False).order_by('-created_at')
    else:
        openid = getattr(request.user, 'openid', request.user.username)
        stocks = StockListModel.objects.filter(openid=openid).order_by('can_order_stock')
        alerts = StockAlert.objects.filter(is_resolved=False).order_by('-created_at')  # Alerts are global
    
    context = {
        'stocks': stocks,
        'alerts': alerts,
        'total_products': stocks.count(),
        'low_stock_count': stocks.filter(can_order_stock__lte=10, can_order_stock__gt=0).count(),
        'out_of_stock_count': stocks.filter(can_order_stock=0).count(),
        'active_alerts': alerts.count(),
    }
    return render(request, 'stock/dashboard.html', context)

@require_permission('stock', 'adjust')  # Stock adjust permission
@require_http_methods(["POST"])
def add_stock_api(request):
    try:
        goods_code = request.POST.get('goods_code')
        goods_desc = request.POST.get('goods_desc')
        goods_qty = int(request.POST.get('goods_qty', 0))
        warehouse = request.POST.get('warehouse', 'Main')
        
        stock = StockListModel.objects.create(
            goods_code=goods_code,
            goods_desc=goods_desc,
            goods_qty=goods_qty,
            can_order_stock=goods_qty,
            ordered_stock=0,
            openid=request.user.username
        )
        
        return JsonResponse({'success': True, 'id': stock.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@require_permission('stock', 'adjust')  # Bulk stock upload
@require_http_methods(["POST"])
def bulk_upload_stock_api(request):
    try:
        csv_file = request.FILES.get('file')
        if not csv_file:
            return JsonResponse({'success': False, 'error': 'No file uploaded'}, status=400)
        
        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        
        created = 0
        for row in reader:
            StockListModel.objects.create(
                goods_code=row['goods_code'],
                goods_desc=row['goods_desc'],
                goods_qty=int(row['goods_qty']),
                can_order_stock=int(row['goods_qty']),
                ordered_stock=0,
                openid=request.user.username
            )
            created += 1
        
        return JsonResponse({'success': True, 'created': created})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_permission('stock', 'adjust')
@require_http_methods(["POST"])
def adjust_stock_api(request):
    """Adjust stock levels (increase/decrease)"""
    try:
        data = json.loads(request.body)
        goods_code = data.get('goods_code')
        adjustment_type = data.get('type')  # 'increase' or 'decrease'
        quantity = int(data.get('quantity', 0))
        reason = data.get('reason', '')
        
        if not goods_code or not adjustment_type or quantity <= 0:
            return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)
        
        stock = StockListModel.objects.filter(goods_code=goods_code).first()
        if not stock:
            return JsonResponse({'success': False, 'error': 'Stock not found'}, status=404)
        
        old_qty = stock.goods_qty
        
        if adjustment_type == 'increase':
            stock.goods_qty += quantity
            stock.can_order_stock += quantity
            stock.onhand_stock += quantity
            movement_type = 'in'
        elif adjustment_type == 'decrease':
            if stock.goods_qty < quantity:
                return JsonResponse({'success': False, 'error': 'Insufficient stock'}, status=400)
            stock.goods_qty -= quantity
            stock.can_order_stock = max(0, stock.can_order_stock - quantity)
            stock.onhand_stock = max(0, stock.onhand_stock - quantity)
            movement_type = 'out'
        else:
            return JsonResponse({'success': False, 'error': 'Invalid adjustment type'}, status=400)
        
        stock.save()
        
        # Record stock movement
        StockMovement.objects.create(
            goods_code=goods_code,
            movement_type='adjust',
            quantity=quantity if adjustment_type == 'increase' else -quantity,
            reason=reason or f'Stock {adjustment_type}',
            user=request.user
        )
        
        return JsonResponse({
            'success': True,
            'old_qty': old_qty,
            'new_qty': stock.goods_qty,
            'message': f'Stock adjusted from {old_qty} to {stock.goods_qty}'
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@require_permission('stock', 'transfer')  # Stock transfer permission (Admin+)
@require_http_methods(["POST"])
def transfer_stock_api(request):
    """Transfer stock between warehouses/locations"""
    try:
        data = json.loads(request.body)
        goods_code = data.get('goods_code')
        from_warehouse = data.get('from_warehouse', 'Main')
        to_warehouse = data.get('to_warehouse')
        quantity = int(data.get('quantity', 0))
        reason = data.get('reason', '')
        
        if not all([goods_code, to_warehouse, quantity > 0]):
            return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)
        
        # Get source stock
        source_stock = StockListModel.objects.filter(goods_code=goods_code).first()
        if not source_stock:
            return JsonResponse({'success': False, 'error': 'Source stock not found'}, status=404)
        
        if source_stock.goods_qty < quantity:
            return JsonResponse({'success': False, 'error': 'Insufficient stock for transfer'}, status=400)
        
        # Reduce from source
        source_stock.goods_qty -= quantity
        source_stock.can_order_stock -= quantity
        source_stock.save()
        
        # Record outbound movement
        StockMovement.objects.create(
            goods_code=goods_code,
            movement_type='out',
            quantity=-quantity,
            reason=f'Transfer to {to_warehouse}: {reason}',
            user=request.user
        )
        
        # Record inbound movement
        StockMovement.objects.create(
            goods_code=goods_code,
            movement_type='in',
            quantity=quantity,
            reason=f'Transfer from {from_warehouse}: {reason}',
            user=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Transferred {quantity} units to {to_warehouse}',
            'remaining_stock': source_stock.goods_qty
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@require_permission('stock', 'view')
def stock_movements_page(request):
    """Stock movements page with filters"""
    movements = StockMovement.objects.select_related('user').order_by('-created_at')[:100]
    return render(request, 'stock/movements.html', {'movements': movements})

@require_permission('stock', 'delete')
def delete_movement(request, movement_id):
    from django.contrib import messages
    movement = get_object_or_404(StockMovement, id=movement_id)
    movement.delete()
    messages.success(request, 'Movement deleted')
    return redirect('stock_movements_page')

@require_permission('stock', 'view')  # View stock movements
def stock_movements_api(request):
    """Get stock movement history"""
    try:
        goods_code = request.GET.get('goods_code')
        movement_type = request.GET.get('type')
        days = int(request.GET.get('days', 30))
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 50))
        
        movements = StockMovement.objects.all()
        
        if goods_code:
            movements = movements.filter(goods_code=goods_code)
        if movement_type:
            movements = movements.filter(movement_type=movement_type)
        
        # Pagination
        from django.core.paginator import Paginator
        paginator = Paginator(movements, per_page)
        page_obj = paginator.get_page(page)
        
        results = []
        for movement in page_obj:
            results.append({
                'id': movement.id,
                'goods_code': movement.goods_code,
                'movement_type': movement.get_movement_type_display(),
                'quantity': movement.quantity,
                'reason': movement.reason,
                'user': movement.user.username if movement.user else 'System',
                'created_at': movement.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return JsonResponse({
            'success': True,
            'movements': results,
            'total': paginator.count,
            'page': page,
            'total_pages': paginator.num_pages
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
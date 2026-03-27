"""
Production Inventory Views with Advanced Filtering and Modals
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator

from permissions.decorators import require_permission
from goods.models import ListModel as Product
from stock.models import StockListModel


@require_permission('products', 'view')
def production_inventory(request):
    """Production inventory page with real data, filters, and modals"""
    
    # Base queryset
    products = Product.objects.filter(is_delete=False)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(goods_name__icontains=search_query) |
            Q(goods_code__icontains=search_query) |
            Q(goods_desc__icontains=search_query)
        )
    
    # Category filter
    category = request.GET.get('category', '')
    if category:
        products = products.filter(goods_class=category)
    
    # Stock level filter
    stock_level = request.GET.get('stock_level', '')
    if stock_level == 'low':
        # Low stock items
        products = products.filter(
            stocklistmodel__qty__lt=models.F('stocklistmodel__qty_minimum')
        ).distinct()
    elif stock_level == 'out':
        # Out of stock
        products = products.filter(stocklistmodel__qty=0).distinct()
    elif stock_level == 'good':
        # Good stock
        products = products.filter(
            stocklistmodel__qty__gte=models.F('stocklistmodel__qty_minimum')
        ).distinct()
    
    # Supplier filter
    supplier = request.GET.get('supplier', '')
    if supplier:
        products = products.filter(supplier__id=supplier)
    
    # Sorting
    sort_order = request.GET.get('sort', 'name')
    if sort_order == 'name':
        products = products.order_by('goods_name')
    elif sort_order == 'name_desc':
        products = products.order_by('-goods_name')
    elif sort_order == 'price':
        products = products.order_by('goods_cost')
    elif sort_order == 'price_desc':
        products = products.order_by('-goods_cost')
    elif sort_order == 'stock':
        products = products.order_by('stocklistmodel__qty')
    elif sort_order == 'stock_desc':
        products = products.order_by('-stocklistmodel__qty')
    
    # Pagination
    paginator = Paginator(products, 20)  # 20 items per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get all categories for filter dropdown
    categories = Product.objects.filter(
        is_delete=False
    ).values_list('goods_class', flat=True).distinct()
    
    # Get all suppliers for filter dropdown
    from supplier.models import ListModel as Supplier
    suppliers = Supplier.objects.filter(is_delete=False)
    
    context = {
        'products': page_obj,
        'categories': categories,
        'suppliers': suppliers,
        'search_query': search_query,
        'selected_category': category,
        'selected_stock_level': stock_level,
        'selected_supplier': supplier,
        'sort_order': sort_order,
    }
    
    return render (request, 'inventory/production_inventory.html', context)


@require_permission('products', 'view')
def product_detail_modal(request, product_id):
    """Get product details for modal (AJAX)"""
    product = get_object_or_404(Product, id=product_id, is_delete=False)
    
    # Get stock information
    stock_info = StockListModel.objects.filter(
        goods_code=product.goods_code,
        is_delete=False
    ).first()
    
    data = {
        'id': product.id,
        'code': product.goods_code,
        'name': product.goods_name,
        'description': product.goods_desc,
        'category': product.goods_class,
        'cost': str(product.goods_cost),
        'price': str(product.goods_price),
        'stock_qty': stock_info.qty if stock_info else 0,
        'min_qty': stock_info.qty_minimum if stock_info else 0,
        'supplier': product.goods_supplier,
        'unit': product.goods_unit,
    }
    
    return JsonResponse(data)


@require_permission('products', 'edit')
def product_edit_modal(request, product_id):
    """Edit product via modal (AJAX)"""
    product = get_object_or_404(Product, id=product_id, is_delete=False)
    
    if request.method == 'POST':
        product.goods_name = request.POST.get('name')
        product.goods_desc = request.POST.get('description')
        product.goods_cost = request.POST.get('cost')
        product.goods_price = request.POST.get('price')
        product.save()
        
        return JsonResponse({'success': True, 'message': 'Product updated successfully'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from permissions.decorators import require_role
from .models import StockTransfer
from goods.models import ListModel as Product
from warehouse.models import ListModel as Warehouse

@login_required
@require_role('superadmin','admin','supervisor','staff')
def transfer_list(request):
    transfers = StockTransfer.objects.select_related('product','from_warehouse','to_warehouse','created_by')
    return render(request, 'transfers/list.html', {'transfers': transfers})

@login_required
@require_role('superadmin','admin','supervisor')
def create_transfer(request):
    if request.method == 'POST':
        from_wh = get_object_or_404(Warehouse, id=request.POST.get('from_warehouse'))
        to_wh = get_object_or_404(Warehouse, id=request.POST.get('to_warehouse'))
        qty = int(request.POST.get('quantity', 0))
        if qty <= 0:
            messages.error(request, 'Quantity must be positive.')
        elif from_wh == to_wh:
            messages.error(request, 'Source and destination must differ.')
        else:
            StockTransfer.objects.create(
                product=get_object_or_404(Product, id=request.POST.get('product_id')),
                from_warehouse=from_wh, to_warehouse=to_wh,
                quantity=qty, notes=request.POST.get('notes',''), created_by=request.user
            )
            messages.success(request, 'Transfer created.')
            return redirect('transfers:list')
    return render(request, 'transfers/create.html', {
        'products': Product.objects.filter(is_delete=False),
        'warehouses': Warehouse.objects.all()
    })

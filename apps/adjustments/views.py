from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from permissions.decorators import require_role
from .models import StockAdjustment
from goods.models import ListModel as Product

@login_required
@require_role('superadmin','admin','supervisor','staff')
def adjustment_list(request):
    adjustments = StockAdjustment.objects.select_related('product','created_by','approved_by')
    return render(request, 'adjustments/list.html', {'adjustments': adjustments})

@login_required
@require_role('superadmin','admin','supervisor')
def create_adjustment(request):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=request.POST.get('product_id'))
        StockAdjustment.objects.create(
            product=product,
            adjustment_type=request.POST.get('adjustment_type'),
            quantity=request.POST.get('quantity'),
            reason=request.POST.get('reason',''),
            created_by=request.user,
        )
        messages.success(request, 'Adjustment submitted for approval.')
        return redirect('adjustments:list')
    return render(request, 'adjustments/create.html', {'products': Product.objects.filter(is_delete=False)})

@login_required
@require_role('superadmin','admin')
def approve_adjustment(request, adjustment_id):
    adj = get_object_or_404(StockAdjustment, id=adjustment_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        adj.status = 'approved' if action == 'approve' else 'rejected'
        adj.approved_by = request.user
        adj.save()
        messages.success(request, f'Adjustment {adj.status}.')
    return redirect('adjustments:list')

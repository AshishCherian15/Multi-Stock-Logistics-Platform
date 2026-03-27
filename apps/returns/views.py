from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from permissions.decorators import require_role
from .models import ReturnRequest
from orders.models import Order

@login_required
@require_role('superadmin','admin','supervisor','staff')
def return_list(request):
    returns = ReturnRequest.objects.select_related('order','customer','handled_by')
    return render(request, 'returns/list.html', {'returns': returns})

@login_required
def create_return(request):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=request.POST.get('order_id'), customer_user=request.user)
        ReturnRequest.objects.create(order=order, customer=request.user, reason=request.POST.get('reason'), description=request.POST.get('description',''))
        messages.success(request, 'Return request submitted.')
        return redirect('orders:my_orders')
    orders = Order.objects.filter(customer_user=request.user, status='delivered')
    return render(request, 'returns/create.html', {'orders': orders})

@login_required
@require_role('superadmin','admin','supervisor')
def process_return(request, return_id):
    ret = get_object_or_404(ReturnRequest, id=return_id)
    if request.method == 'POST':
        ret.status = 'approved' if request.POST.get('action') == 'approve' else 'rejected'
        ret.handled_by = request.user
        ret.save()
        messages.success(request, f'Return {ret.status}.')
    return redirect('returns:list')

@login_required
@require_role('superadmin','admin')
def process_refund(request, return_id):
    ret = get_object_or_404(ReturnRequest, id=return_id, status='approved')
    if request.method == 'POST':
        ret.refund_amount = request.POST.get('refund_amount', 0)
        ret.status = 'completed'
        ret.save()
        messages.success(request, f'Refund of ₹{ret.refund_amount} processed.')
    return redirect('returns:list')

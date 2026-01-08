from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from permissions.decorators import require_role

@login_required
@require_role('superadmin', 'admin', 'supervisor', 'staff')
def return_list(request):
    returns = [
        {'id': 1, 'order': 'ORD-001', 'customer': 'John Doe', 'reason': 'Defective', 'status': 'Pending', 'amount': '$299'},
        {'id': 2, 'order': 'ORD-002', 'customer': 'Jane Smith', 'reason': 'Wrong Item', 'status': 'Approved', 'amount': '$199'}
    ]
    return render(request, 'returns/list.html', {'returns': returns})

@login_required
@require_role('superadmin', 'admin', 'supervisor', 'staff')
def create_return(request):
    return render(request, 'returns/create.html')

@login_required
@require_role('superadmin', 'admin', 'supervisor')
def process_return(request, return_id):
    return render(request, 'returns/process.html', {'return_id': return_id})

@login_required
@require_role('superadmin', 'admin')
def process_refund(request, return_id):
    return render(request, 'returns/refund.html', {'return_id': return_id})
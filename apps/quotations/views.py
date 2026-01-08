from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from permissions.decorators import require_role

@login_required
@require_role('superadmin', 'admin', 'supervisor', 'staff')
def quotation_list(request):
    quotations = [
        {'id': 1, 'customer': 'John Doe', 'amount': '$2,500', 'status': 'Pending', 'date': '2024-11-10'},
        {'id': 2, 'customer': 'Jane Smith', 'amount': '$1,800', 'status': 'Approved', 'date': '2024-11-09'}
    ]
    return render(request, 'quotations/list.html', {'quotations': quotations})

@login_required
@require_role('superadmin', 'admin', 'supervisor', 'staff')
def create_quotation(request):
    return render(request, 'quotations/create.html')

@login_required
@require_role('superadmin', 'admin', 'supervisor', 'staff')
def quotation_detail(request, quotation_id):
    return render(request, 'quotations/detail.html', {'quotation_id': quotation_id})

@login_required
@require_role('superadmin', 'admin', 'supervisor')
def convert_to_order(request, quotation_id):
    return render(request, 'quotations/convert.html', {'quotation_id': quotation_id})
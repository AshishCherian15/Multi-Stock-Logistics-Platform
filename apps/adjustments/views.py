from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from permissions.decorators import require_role

@login_required
@require_role('superadmin', 'admin', 'supervisor', 'staff')
def adjustment_list(request):
    adjustments = [
        {'id': 1, 'product': 'iPhone 14', 'type': 'Stock Count', 'quantity': -5, 'reason': 'Damaged items', 'date': '2024-11-10'},
        {'id': 2, 'product': 'Samsung Galaxy', 'type': 'Correction', 'quantity': 3, 'reason': 'System error', 'date': '2024-11-09'}
    ]
    return render(request, 'adjustments/list.html', {'adjustments': adjustments})

@login_required
@require_role('superadmin', 'admin', 'supervisor')
def create_adjustment(request):
    return render(request, 'adjustments/create.html')

@login_required
@require_role('superadmin', 'admin')
def approve_adjustment(request, adjustment_id):
    return render(request, 'adjustments/approve.html', {'adjustment_id': adjustment_id})
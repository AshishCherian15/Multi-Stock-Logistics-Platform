from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from permissions.decorators import require_role

@login_required
@require_role('superadmin', 'admin', 'supervisor', 'staff')
def transfer_list(request):
    transfers = [
        {'id': 1, 'from_warehouse': 'Main Warehouse', 'to_warehouse': 'Branch A', 'product': 'iPhone 14', 'quantity': 10, 'status': 'In Transit'},
        {'id': 2, 'from_warehouse': 'Branch A', 'to_warehouse': 'Branch B', 'product': 'Samsung Galaxy', 'quantity': 5, 'status': 'Completed'}
    ]
    return render(request, 'transfers/list.html', {'transfers': transfers})

@login_required
@require_role('superadmin', 'admin', 'supervisor', 'staff')
def create_transfer(request):
    return render(request, 'transfers/create.html')

@login_required
@require_role('superadmin', 'admin', 'supervisor')
def approve_transfer(request, transfer_id):
    return render(request, 'transfers/approve.html', {'transfer_id': transfer_id})

@login_required
@require_role('superadmin', 'admin', 'supervisor', 'staff')
def track_transfer(request, transfer_id):
    return render(request, 'transfers/track.html', {'transfer_id': transfer_id})
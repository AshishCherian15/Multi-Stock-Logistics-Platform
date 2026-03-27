from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from permissions.decorators import require_role

@login_required
@require_role('superadmin', 'admin', 'supervisor', 'staff')
def expense_list(request):
    return render(request, 'expenses/list.html')

@login_required
@require_role('superadmin', 'admin', 'supervisor')
def create_expense(request):
    return render(request, 'expenses/create.html')
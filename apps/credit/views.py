from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CreditProfile, CreditTransaction
from customer.models import ListModel as Customer
from permissions.decorators import require_role

@login_required
@require_role('superadmin', 'admin', 'supervisor', 'staff')
def credit_dashboard(request):
    profiles = CreditProfile.objects.select_related('customer').all()
    total_credit = sum(p.credit_limit for p in profiles)
    total_used = sum(p.used_credit for p in profiles)
    total_overdue = sum(p.overdue_amount for p in profiles)
    
    return render(request, 'credit/dashboard.html', {
        'profiles': profiles,
        'total_credit': total_credit,
        'total_used': total_used,
        'total_overdue': total_overdue,
    })

@login_required
@require_role('superadmin', 'admin', 'supervisor', 'staff')
def credit_detail(request, profile_id):
    profile = get_object_or_404(CreditProfile, id=profile_id)
    transactions = profile.transactions.all()[:20]
    return render(request, 'credit/detail.html', {
        'profile': profile,
        'transactions': transactions
    })

@login_required
@require_role('superadmin', 'admin')
def add_credit_profile(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        customer = get_object_or_404(Customer, id=customer_id)
        
        if hasattr(customer, 'credit_profile'):
            messages.error(request, 'This customer already has a credit profile')
        else:
            CreditProfile.objects.create(
                customer=customer,
                credit_limit=0,
                available_credit=0,
                used_credit=0,
                risk_level='low',
                payment_terms_days=30,
                overdue_amount=0,
                is_active=True
            )
            messages.success(request, f'Credit profile created for {customer.customer_name}')
        return redirect('credit:dashboard')
    
    customers_without_profile = Customer.objects.filter(credit_profile__isnull=True)
    return render(request, 'credit/add_profile.html', {
        'customers': customers_without_profile
    })

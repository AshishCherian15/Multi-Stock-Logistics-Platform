from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import models as db_models
from permissions.decorators import require_role
from .models import Quotation, QuotationItem


@login_required
@require_role('superadmin', 'admin', 'supervisor', 'staff')
def quotation_list(request):
    status_filter = request.GET.get('status', '')
    qs = Quotation.objects.select_related('created_by')
    if status_filter:
        qs = qs.filter(status=status_filter)
    return render(request, 'quotations/list.html', {
        'quotations': qs,
        'status_filter': status_filter,
        'status_choices': Quotation.STATUS_CHOICES,
    })


@login_required
@require_role('superadmin', 'admin', 'supervisor', 'staff')
def create_quotation(request):
    if request.method == 'POST':
        quotation = Quotation.objects.create(
            customer_name=request.POST['customer_name'],
            customer_email=request.POST['customer_email'],
            customer_phone=request.POST.get('customer_phone', ''),
            customer_company=request.POST.get('customer_company', ''),
            notes=request.POST.get('notes', ''),
            terms=request.POST.get('terms', ''),
            tax_rate=request.POST.get('tax_rate', 0),
            discount_amount=request.POST.get('discount_amount', 0),
            created_by=request.user,
        )
        # Bulk-create line items from POST arrays
        descriptions = request.POST.getlist('description[]')
        quantities = request.POST.getlist('quantity[]')
        unit_prices = request.POST.getlist('unit_price[]')
        discount_pcts = request.POST.getlist('discount_pct[]') or ['0'] * len(descriptions)
        items = [
            QuotationItem(
                quotation=quotation,
                description=desc,
                quantity=qty,
                unit_price=price,
                discount_pct=disc,
            )
            for desc, qty, price, disc in zip(descriptions, quantities, unit_prices, discount_pcts)
            if desc.strip()
        ]
        if items:
            QuotationItem.objects.bulk_create(items)
        quotation.recalculate_totals()
        messages.success(request, f'Quotation {quotation.quotation_number} created.')
        return redirect('quotation_detail', quotation_id=quotation.pk)
    return render(request, 'quotations/create.html')


@login_required
@require_role('superadmin', 'admin', 'supervisor', 'staff')
def quotation_detail(request, quotation_id):
    quotation = get_object_or_404(Quotation.objects.prefetch_related('items'), pk=quotation_id)
    return render(request, 'quotations/detail.html', {'quotation': quotation})


@login_required
@require_role('superadmin', 'admin', 'supervisor')
def update_status(request, quotation_id):
    quotation = get_object_or_404(Quotation, pk=quotation_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        allowed = [s for s, _ in Quotation.STATUS_CHOICES if s != 'converted']
        if new_status in allowed:
            quotation.status = new_status
            quotation.save(update_fields=['status', 'updated_at'])
            messages.success(request, f'Status updated to {quotation.get_status_display()}.')
        else:
            messages.error(request, 'Invalid status.')
    return redirect('quotation_detail', quotation_id=quotation.pk)


@login_required
@require_role('superadmin', 'admin', 'supervisor')
def convert_to_order(request, quotation_id):
    quotation = get_object_or_404(Quotation, pk=quotation_id)
    if quotation.status not in ('draft', 'sent', 'approved'):
        messages.error(request, 'Only draft, sent, or approved quotations can be converted.')
        return redirect('quotation_detail', quotation_id=quotation.pk)
    if quotation.is_expired:
        messages.error(request, 'This quotation has expired and cannot be converted.')
        return redirect('quotation_detail', quotation_id=quotation.pk)
    return render(request, 'quotations/convert.html', {'quotation': quotation})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from .models import Invoice, InvoiceItem, Receipt, InvoiceComment
from datetime import datetime, timedelta
import io
from django.conf import settings

# Import RBAC decorators
from permissions.decorators import require_permission, require_role

@login_required
def invoice_list(request):
    from permissions.decorators import get_user_role
    
    user_role = get_user_role(request.user)
    
    if user_role == 'customer':
        # Customers see only their own invoices
        invoices = Invoice.objects.filter(
            customer_email=request.user.email
        ).order_by('-created_at')
        receipts = Receipt.objects.filter(
            invoice__customer_email=request.user.email
        ).order_by('-payment_date')
        context = {'invoices': invoices, 'receipts': receipts}
        return render(request, 'billing/customer_list.html', context)
    
    from permissions.decorators import check_permission
    if not check_permission(request.user, 'billing', 'view'):
        return render(request, 'billing/customer_list.html', {'invoices': [], 'receipts': []})
    
    # Admin/Staff see all invoices for management
    invoices = Invoice.objects.all().order_by('-created_at')
    receipts = Receipt.objects.all().order_by('-payment_date')
    
    context = {'invoices': invoices, 'receipts': receipts}
    return render(request, 'billing/unified_billing.html', context)

@require_permission('billing', 'create')  # Create invoices (Admin+)
def invoice_create(request):
    if request.method == 'POST':
        invoice = Invoice(
            invoice_type=request.POST['invoice_type'],
            customer_name=request.POST['customer_name'],
            customer_email=request.POST['customer_email'],
            customer_phone=request.POST['customer_phone'],
            customer_address=request.POST['customer_address'],
            due_date=request.POST['due_date'],
            project_name=request.POST.get('project_name', ''),
            tax_rate=request.POST.get('tax_rate', 0),
            discount_amount=request.POST.get('discount_amount', 0),
            payment_method=request.POST.get('payment_method', ''),
            terms_conditions=request.POST.get('terms_conditions', ''),
            created_by=request.user
        )
        invoice.save()
        
        # Add items
        items = request.POST.getlist('item_description[]')
        quantities = request.POST.getlist('item_quantity[]')
        prices = request.POST.getlist('item_price[]')
        
        subtotal = 0
        for desc, qty, price in zip(items, quantities, prices):
            if desc and qty and price:
                item = InvoiceItem(invoice=invoice, description=desc, quantity=int(qty), price=float(price))
                item.save()
                subtotal += item.amount
        
        invoice.subtotal = subtotal
        invoice.tax_amount = (subtotal * float(invoice.tax_rate)) / 100
        invoice.grand_total = subtotal + invoice.tax_amount - float(invoice.discount_amount)
        invoice.save()
        
        messages.success(request, f'Invoice {invoice.invoice_number} created successfully!')
        return redirect('billing:invoice_detail', pk=invoice.id)
    
    return render(request, 'billing/invoice_form.html', {'invoice_types': Invoice.INVOICE_TYPES})

@login_required
def invoice_detail(request, pk):
    from permissions.decorators import get_user_role
    
    invoice = get_object_or_404(Invoice, pk=pk)
    
    # Check permissions
    user_role = get_user_role(request.user)
    if user_role == 'customer':
        # Customers can only view their own invoices
        if invoice.customer_email != request.user.email:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden('You do not have permission to view this invoice')
    else:
        # Staff need billing view permission
        from permissions.decorators import check_permission
        if not check_permission(request.user, 'billing', 'view'):
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden('You do not have permission to view invoices')
    
    comments = invoice.comments.all()
    receipts = invoice.receipts.all()
    context = {'invoice': invoice, 'comments': comments, 'receipts': receipts}
    return render(request, 'billing/invoice_detail.html', context)

@login_required
def invoice_pdf(request, pk):
    from permissions.decorators import get_user_role
    
    invoice = get_object_or_404(Invoice, pk=pk)
    
    # Check permissions
    user_role = get_user_role(request.user)
    if user_role == 'customer':
        # Customers can only download their own invoices
        if invoice.customer_email != request.user.email:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden('You do not have permission to download this invoice')
    else:
        # Staff need billing pdf permission
        from permissions.decorators import check_permission
        if not check_permission(request.user, 'billing', 'pdf'):
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden('You do not have permission to generate PDFs')
    
    template = request.GET.get('template', 'light')
    
    html = render_to_string('billing/invoice_pdf.html', {'invoice': invoice, 'template': template})
    
    try:
        from weasyprint import HTML
        pdf_file = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
        return response
    except:
        return HttpResponse(html)

@require_permission('billing', 'create')  # Create receipts (record payments)
def receipt_create(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    
    if request.method == 'POST':
        receipt = Receipt(
            invoice=invoice,
            payment_mode=request.POST['payment_mode'],
            amount_paid=request.POST['amount_paid']
        )
        receipt.save()
        
        invoice.status = 'paid'
        invoice.save()
        
        messages.success(request, f'Receipt {receipt.receipt_number} generated!')
        return redirect('billing:receipt_detail', pk=receipt.id)
    
    return render(request, 'billing/receipt_form.html', {'invoice': invoice})

@login_required
def receipt_detail(request, pk):
    from permissions.decorators import get_user_role
    
    receipt = get_object_or_404(Receipt, pk=pk)
    
    # Check permissions
    user_role = get_user_role(request.user)
    if user_role == 'customer':
        # Customers can only view their own receipts
        if receipt.invoice.customer_email != request.user.email:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden('You do not have permission to view this receipt')
    else:
        # Staff need billing view permission
        from permissions.decorators import check_permission
        if not check_permission(request.user, 'billing', 'view'):
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden('You do not have permission to view receipts')
    
    return render(request, 'billing/receipt_detail.html', {'receipt': receipt})

@login_required
def receipt_pdf(request, pk):
    from permissions.decorators import get_user_role
    
    receipt = get_object_or_404(Receipt, pk=pk)
    
    # Check permissions
    user_role = get_user_role(request.user)
    if user_role == 'customer':
        # Customers can only download their own receipts
        if receipt.invoice.customer_email != request.user.email:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden('You do not have permission to download this receipt')
    else:
        # Staff need billing pdf permission
        from permissions.decorators import check_permission
        if not check_permission(request.user, 'billing', 'pdf'):
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden('You do not have permission to generate PDFs')
    
    html = render_to_string('billing/receipt_pdf.html', {'receipt': receipt})
    
    try:
        from weasyprint import HTML
        pdf_file = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="receipt_{receipt.receipt_number}.pdf"'
        return response
    except:
        return HttpResponse(html)

@require_permission('billing', 'delete')  # Delete invoices (SuperAdmin/Admin only)
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.delete()
    messages.success(request, 'Invoice deleted successfully!')
    return redirect('billing:invoice_list')

from django.views.decorators.http import require_http_methods
import json

@require_http_methods(["POST"])
@login_required
def create_from_payment(request):
    try:
        data = json.loads(request.body)
        
        # Create invoice
        invoice = Invoice.objects.create(
            invoice_type=data.get('invoice_type', 'marketplace'),
            customer_name=request.user.get_full_name() or request.user.username,
            customer_email=request.user.email or 'customer@example.com',
            customer_phone='N/A',
            customer_address='N/A',
            due_date=datetime.now().date(),
            subtotal=data.get('subtotal', 0),
            tax_rate=18,
            tax_amount=data.get('tax', 0),
            discount_amount=data.get('discount', 0),
            grand_total=data.get('total', 0),
            payment_method=data.get('payment_method', 'online'),
            status='paid' if data.get('payment_method') != 'cod' else 'sent',
            notes=f"Coupon: {data.get('coupon_code', 'None')}",
            created_by=request.user
        )
        
        # Add invoice items
        for item in data.get('items', []):
            InvoiceItem.objects.create(
                invoice=invoice,
                description=item.get('name', 'Item'),
                quantity=item.get('quantity', 1),
                price=item.get('price', 0)
            )
        
        # Create receipt if payment is not COD
        receipt = None
        if data.get('payment_method') != 'cod':
            receipt = Receipt.objects.create(
                invoice=invoice,
                payment_mode=data.get('payment_method', 'online'),
                amount_paid=data.get('total', 0)
            )
        
        return JsonResponse({
            'success': True,
            'invoice_number': invoice.invoice_number,
            'receipt_number': receipt.receipt_number if receipt else None
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


"""
Customers, Suppliers, and Warehouse pages with real data
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
import csv
from io import StringIO, BytesIO
from datetime import datetime

from permissions.decorators import require_permission, get_user_role
from customer.models import ListModel as Customer
from supplier.models import ListModel as Supplier
from warehouse.models import ListModel as Warehouse
from stock.models import StockListModel


@require_permission('customers', 'view')
def customers_page(request):
    """Customers management page for team roles"""
    role = get_user_role(request.user)
    if role not in ['superadmin', 'admin', 'subadmin', 'staff']:
        from django.contrib import messages
        messages.error(request, 'Access denied. Team roles only.')
        return redirect('customers:dashboard')
    
    customers = Customer.objects.filter(is_delete=False)
    
    # Get unique cities for filter dropdown
    all_cities = Customer.objects.filter(is_delete=False).values_list('customer_city', flat=True).distinct().order_by('customer_city')
    cities = [c for c in all_cities if c]
    
    # Optionally attach profile avatars (if mapping exists by contact/email)
    try:
        from profile.models import Profile
        profiles = Profile.objects.select_related('user').all()
        profile_map = {p.user.email: p for p in profiles if getattr(p, 'avatar', None)}
        for c in customers:
            # naive mapping: contact field may contain email
            email = getattr(c, 'customer_contact', '')
            c.profile = profile_map.get(email)
    except Exception:
        pass
    
    # Search
    search = request.GET.get('search', '')
    if search:
        customers = customers.filter(
            Q(customer_name__icontains=search) |
            Q(customer_city__icontains=search) |
            Q(customer_contact__icontains=search)
        )
    
    # Filter by city
    city_filter = request.GET.get('city', '')
    if city_filter:
        customers = customers.filter(customer_city=city_filter)
    
    # Filter by status (placeholder - all customers are active by default)
    status_filter = request.GET.get('status', '')
    # Note: Customer model doesn't have status field, so this is a placeholder
    # If inactive status needed, can filter by is_delete or add a status field
    
    # Sort
    sort = request.GET.get('sort', 'name')
    if sort == 'name':
        customers = customers.order_by('customer_name')
    elif sort == 'city':
        customers = customers.order_by('customer_city')
    
    # Pagination
    paginator = Paginator(customers, 25)
    page = request.GET.get('page', 1)
    customers_page = paginator.get_page(page)
    
    # Summary statistics
    total_customers = customers.count()
    active_customers = total_customers  # placeholder: no explicit status field
    pending_tickets = 0
    avg_order_value = 0
    try:
        from orders.models import Order
        # Compute avg order value across customers (simple average)
        values = Order.objects.values_list('order_amount', flat=True)
        if values:
            avg_order_value = sum(v or 0 for v in values) / len(values)
    except Exception:
        pass

    context = {
        'customers': customers_page,
        'total_customers': total_customers,
        'active_customers': active_customers,
        'pending_tickets': pending_tickets,
        'avg_order_value': avg_order_value,
        'search': search,
        'cities': cities,
    }
    
    return render(request, 'pages/customers.html', context)


@require_permission('customers', 'delete')
def customer_delete(request, customer_id):
    """Soft-delete a customer and redirect back to list."""
    from django.contrib import messages
    from django.shortcuts import redirect, get_object_or_404
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('pages:customers')
    customer = get_object_or_404(Customer, id=customer_id)
    customer.is_delete = True
    customer.save()
    messages.success(request, 'Customer deleted successfully.')
    return redirect('pages:customers')


@require_permission('messaging', 'view')
def customer_message(request, customer_id):
    """Redirect to messaging for an individual customer thread."""
    from django.shortcuts import redirect
    # Use the correct messaging route for customer chat
    return redirect('messaging:customer_chat', customer_id=customer_id)


@require_permission('customers', 'view')
def customer_detail(request, customer_id):
    """Customer detail page for viewing individual customer information."""
    from django.shortcuts import get_object_or_404
    role = get_user_role(request.user)
    if role not in ['superadmin', 'admin', 'subadmin', 'staff']:
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, 'Access denied. Team roles only.')
        return redirect('customers:dashboard')
    
    customer = get_object_or_404(Customer, id=customer_id, is_delete=False)
    
    # Get related orders if available
    orders = []
    try:
        from orders.models import Order
        orders = Order.objects.filter(customer_name=customer.customer_name, is_delete=False).order_by('-create_time')[:10]
    except Exception:
        pass
    
    context = {
        'customer': customer,
        'orders': orders,
    }
    
    return render(request, 'pages/customer_detail.html', context)


@require_permission('customers', 'edit')
def customer_edit(request, customer_id):
    """Customer edit page for updating customer information."""
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    
    role = get_user_role(request.user)
    if role not in ['superadmin', 'admin', 'subadmin', 'staff']:
        messages.error(request, 'Access denied. Team roles only.')
        return redirect('customers:dashboard')
    
    customer = get_object_or_404(Customer, id=customer_id, is_delete=False)
    
    if request.method == 'POST':
        # Update customer fields
        customer.customer_name = request.POST.get('customer_name', customer.customer_name)
        customer.customer_city = request.POST.get('customer_city', customer.customer_city)
        customer.customer_address = request.POST.get('customer_address', customer.customer_address)
        customer.customer_contact = request.POST.get('customer_contact', customer.customer_contact)
        customer.customer_manager = request.POST.get('customer_manager', customer.customer_manager)
        customer.customer_level = request.POST.get('customer_level', customer.customer_level)
        customer.save()
        
        messages.success(request, 'Customer updated successfully.')
        return redirect('pages:customer_detail', customer_id=customer.id)
    
    context = {
        'customer': customer,
    }
    
    return render(request, 'pages/customer_edit.html', context)


@require_permission('customers', 'create')
def customer_create(request):
    """Create a new customer via AJAX POST and return JSON."""
    from django.contrib import messages
    from django.shortcuts import redirect

    role = get_user_role(request.user)
    if role not in ['superadmin', 'admin', 'subadmin', 'staff']:
        return JsonResponse({'success': False, 'message': 'Access denied. Team roles only.'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)

    name = request.POST.get('customer_name', '').strip()
    city = request.POST.get('customer_city', '').strip()
    contact = request.POST.get('customer_contact', '').strip()
    manager = request.POST.get('customer_manager', '').strip()
    level = request.POST.get('customer_level', '1')
    address = request.POST.get('customer_address', '').strip()

    if not name or not city or not contact:
        return JsonResponse({'success': False, 'message': 'Name, city, and contact are required.'}, status=400)

    try:
        level_int = int(level)
    except Exception:
        level_int = 1

    customer = Customer.objects.create(
        customer_name=name,
        customer_city=city,
        customer_contact=contact,
        customer_manager=manager,
        customer_level=level_int,
        customer_address=address,
    )

    return JsonResponse({'success': True, 'id': customer.id})


@require_permission('customers', 'export')
def customers_export(request):
    """Export customers list in CSV or XLSX format."""
    role = get_user_role(request.user)
    if role not in ['superadmin', 'admin', 'subadmin', 'staff']:
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, 'Access denied. Team roles only.')
        return redirect('customers:dashboard')

    # Base queryset with simple search to mirror list page
    qs = Customer.objects.filter(is_delete=False)
    search = request.GET.get('search', '').strip()
    if search:
        qs = qs.filter(
            Q(customer_name__icontains=search) |
            Q(customer_city__icontains=search) |
            Q(customer_contact__icontains=search)
        )
    
    # Apply city filter
    city_filter = request.GET.get('city', '').strip()
    if city_filter:
        qs = qs.filter(customer_city=city_filter)
    
    # Apply status filter (placeholder - model has no status field)
    status_filter = request.GET.get('status', '').strip()
    # Note: Status filter is UI-only until Customer model has a status field

    fmt = request.GET.get('format', request.GET.get('export', 'xlsx')).lower()
    filename_ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_name = f"customers_{filename_ts}"

    headers = ['Customer Name', 'City', 'Contact', 'Manager', 'Level', 'Address', 'Created']
    rows = [
        [
            c.customer_name,
            c.customer_city,
            c.customer_contact,
            c.customer_manager,
            c.customer_level,
            c.customer_address,
            c.create_time.strftime('%Y-%m-%d %H:%M') if getattr(c, 'create_time', None) else ''
        ]
        for c in qs.order_by('customer_name')
    ]

    if fmt == 'csv':
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerows(rows)
        resp = HttpResponse(output.getvalue(), content_type='text/csv')
        resp['Content-Disposition'] = f'attachment; filename="{base_name}.csv"'
        return resp
    elif fmt in ('xlsx', 'excel'):
        try:
            from openpyxl import Workbook
        except Exception:
            return JsonResponse({'success': False, 'message': 'Excel export not available.'}, status=500)
        wb = Workbook()
        ws = wb.active
        ws.title = 'Customers'
        ws.append(headers)
        for r in rows:
            ws.append(r)
        out = BytesIO()
        wb.save(out)
        resp = HttpResponse(out.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = f'attachment; filename="{base_name}.xlsx"'
        return resp
    else:
        return JsonResponse({'success': False, 'message': 'Unsupported format. Use csv or xlsx.'}, status=400)


@require_permission('suppliers', 'view')
def suppliers_page(request):
    """Suppliers page with real data and filters"""
    
    suppliers = Supplier.objects.filter(is_delete=False)
    
    # Search
    search = request.GET.get('search', '')
    if search:
        suppliers = suppliers.filter(
            Q(supplier_name__icontains=search) |
            Q(supplier_city__icontains=search) |
            Q(supplier_contact__icontains=search)
        )
    
    # Sort
    sort = request.GET.get('sort', 'name')
    if sort == 'name':
        suppliers = suppliers.order_by('supplier_name')
    elif sort == 'level':
        suppliers = suppliers.order_by('-supplier_level')
    
    # Pagination
    paginator = Paginator(suppliers, 25)
    page = request.GET.get('page', 1)
    suppliers_page = paginator.get_page(page)
    
    context = {
        'suppliers': suppliers_page,
        'total_suppliers': suppliers.count(),
        'search': search,
    }
    
    return render(request, 'pages/suppliers.html', context)


@require_permission('warehouses', 'view')
def warehouses_page(request):
    """Warehouses page with real data"""
    
    warehouses = Warehouse.objects.filter(is_delete=False).annotate(
        stock_count=Count('stocklistmodel'),
        total_stock=Sum('stocklistmodel__qty')
    )
    
    context = {
        'warehouses': warehouses,
        'total_warehouses': warehouses.count(),
    }
    
    return render(request, 'pages/warehouses.html', context)

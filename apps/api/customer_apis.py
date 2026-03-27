"""
Customer-facing API endpoints with pagination and per-item permissions
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from permissions.decorators import require_role

@login_required
@require_role('customer')
def rentals_list_api(request):
    from rentals.models import Rental
    
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 20))
    sort = request.GET.get('sort', '-created_at')
    
    rentals = Rental.objects.filter(customer=request.user)
    
    if q:
        rentals = rentals.filter(Q(equipment_name__icontains=q) | Q(rental_id__icontains=q))
    if status:
        rentals = rentals.filter(status=status)
    
    rentals = rentals.order_by(sort)
    paginator = Paginator(rentals, limit)
    page_obj = paginator.get_page(page)
    
    items = [{
        'id': r.id,
        'title': r.equipment_name,
        'summary': f"{r.duration} days rental",
        'status': r.status,
        'updated_at': r.updated_at.isoformat(),
        'permissions': {
            'view': True,
            'edit': r.status == 'pending',
            'extend': r.status == 'active',
            'cancel': r.status in ['pending', 'active']
        }
    } for r in page_obj]
    
    return JsonResponse({
        'items': items,
        'page': page,
        'limit': limit,
        'total': paginator.count
    })

@login_required
@require_role('customer')
def storage_units_list_api(request):
    from storage.models import StorageUnit
    
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 20))
    sort = request.GET.get('sort', '-created_at')
    
    units = StorageUnit.objects.filter(customer=request.user)
    
    if q:
        units = units.filter(Q(unit_number__icontains=q) | Q(location__icontains=q))
    if status:
        units = units.filter(status=status)
    
    units = units.order_by(sort)
    paginator = Paginator(units, limit)
    page_obj = paginator.get_page(page)
    
    items = [{
        'id': u.id,
        'title': u.unit_number,
        'summary': f"{u.size}, {u.location}",
        'status': u.status,
        'updated_at': u.updated_at.isoformat(),
        'permissions': {
            'view': True,
            'edit': False,
            'extend': u.status == 'active',
            'cancel': u.status == 'active'
        }
    } for u in page_obj]
    
    return JsonResponse({
        'items': items,
        'page': page,
        'limit': limit,
        'total': paginator.count
    })

@login_required
@require_role('customer')
def lockers_list_api(request):
    from lockers.models import LockerBooking
    
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 20))
    sort = request.GET.get('sort', '-created_at')
    
    bookings = LockerBooking.objects.filter(customer=request.user)
    
    if q:
        bookings = bookings.filter(Q(locker_number__icontains=q) | Q(location__icontains=q))
    if status:
        bookings = bookings.filter(status=status)
    
    bookings = bookings.order_by(sort)
    paginator = Paginator(bookings, limit)
    page_obj = paginator.get_page(page)
    
    items = [{
        'id': b.id,
        'title': f"Locker {b.locker_number}",
        'summary': f"{b.location}",
        'status': b.status,
        'updated_at': b.updated_at.isoformat(),
        'permissions': {
            'view': True,
            'edit': False,
            'extend': False,
            'cancel': b.status == 'active'
        }
    } for b in page_obj]
    
    return JsonResponse({
        'items': items,
        'page': page,
        'limit': limit,
        'total': paginator.count
    })

@login_required
@require_role('customer')
def invoices_list_api(request):
    from billing.models import Invoice
    
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 20))
    sort = request.GET.get('sort', '-created_at')
    
    invoices = Invoice.objects.filter(customer=request.user)
    
    if q:
        invoices = invoices.filter(Q(invoice_number__icontains=q))
    if status:
        invoices = invoices.filter(status=status)
    
    invoices = invoices.order_by(sort)
    paginator = Paginator(invoices, limit)
    page_obj = paginator.get_page(page)
    
    items = [{
        'id': i.id,
        'title': i.invoice_number,
        'summary': f"₹{i.total_amount}",
        'status': i.status,
        'updated_at': i.updated_at.isoformat(),
        'permissions': {
            'view': True,
            'edit': False,
            'extend': False,
            'cancel': False
        }
    } for i in page_obj]
    
    return JsonResponse({
        'items': items,
        'page': page,
        'limit': limit,
        'total': paginator.count
    })

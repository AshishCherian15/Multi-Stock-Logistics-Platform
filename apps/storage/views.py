from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import StorageUnit, StorageBooking
import random
import string

from permissions.decorators import require_permission

@login_required
def storage_list(request):
    # All authenticated users can view storage units
    units = StorageUnit.objects.all().order_by('-created_at')
    unit_type = request.GET.get('type')
    location = request.GET.get('location')
    
    if unit_type:
        units = units.filter(type=unit_type)
    if location:
        units = units.filter(location__icontains=location)
    
    # Get user role for template conditionals
    try:
        user_role = request.user.role.role
    except:
        user_role = 'guest'
    
    context = {
        'units': units,
        'total_units': units.count(),
        'available_units': units.filter(status='available').count(),
        'occupied_units': units.filter(status='occupied').count(),
        'user_role': user_role,
    }
    # Use main list template for everyone (admin buttons hidden by template conditionals)
    return render(request, 'storage/enhanced_list.html', context)

@require_permission('storage', 'view')
def storage_detail(request, unit_id):
    unit = get_object_or_404(StorageUnit, id=unit_id)
    return render(request, 'storage/detail.html', {'unit': unit})

@require_permission('storage', 'create')
def book_storage(request, unit_id):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Lock the storage unit to prevent concurrent bookings
                unit = StorageUnit.objects.select_for_update().get(id=unit_id)
                
                # Check availability with lock held
                if unit.status != 'available':
                    messages.error(request, 'Storage unit is not available')
                    return redirect('storage:storage_list')
                
                start_date = request.POST.get('start_date')
                end_date = request.POST.get('end_date')
                access_code = ''.join(random.choices(string.digits, k=6))
                
                booking = StorageBooking.objects.create(
                    unit=unit,
                    user=request.user,
                    start_date=start_date,
                    end_date=end_date,
                    total_amount=unit.price_per_month,
                    access_code=access_code
                )
                
                # Update unit status atomically
                unit.status = 'occupied'
                unit.access_code = access_code
                unit.save()
                
                messages.success(request, f'Storage booked! Your access code is: {access_code}')
                return redirect('storage:my_bookings')
        except StorageUnit.DoesNotExist:
            messages.error(request, 'Storage unit not found')
            return redirect('storage:storage_list')
        except Exception as e:
            messages.error(request, f'Error booking storage: {str(e)}')
            return redirect('storage:storage_list')
    
    unit = get_object_or_404(StorageUnit, id=unit_id)
    return render(request, 'storage/book.html', {'unit': unit})

@login_required
def my_bookings(request):
    bookings = StorageBooking.objects.filter(user=request.user)
    return render(request, 'storage/my_bookings.html', {'bookings': bookings})

@login_required
def storage_booking_detail(request, booking_id):
    booking = get_object_or_404(StorageBooking, id=booking_id)
    
    # Check if user owns this booking or is staff
    if booking.user != request.user and not request.user.is_staff:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden('You do not have permission to view this booking')
    
    context = {
        'booking': booking,
        'unit': booking.unit,
    }
    return render(request, 'storage/storage_booking_detail.html', context)

@login_required
def customer_storage_shop(request):
    """Customer-facing storage shopping page"""
    units = StorageUnit.objects.all().order_by('-created_at')
    unit_type = request.GET.get('type')
    location = request.GET.get('location')
    
    if unit_type:
        units = units.filter(type=unit_type)
    if location:
        units = units.filter(location__icontains=location)
    
    context = {
        'units': units,
        'total_units': units.count(),
        'available_units': units.filter(status='available').count(),
        'occupied_units': units.filter(status='occupied').count(),
        'maintenance_units': units.filter(status='maintenance').count(),
    }
    return render(request, 'storage/enhanced_list.html', context)

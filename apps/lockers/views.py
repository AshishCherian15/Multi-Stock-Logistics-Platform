from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from .models import LockerType, Locker, LockerBooking, LockerAccessLog


@login_required
def lockers_list(request):
    """Display all available lockers"""
    # All authenticated users can view lockers
    lockers = Locker.objects.select_related('locker_type').filter(is_active=True)
    locker_types = LockerType.objects.filter(is_active=True)
    
    # Statistics
    total_lockers = lockers.count()
    available = lockers.filter(status='available').count()
    occupied = lockers.filter(status='occupied').count()
    maintenance = lockers.filter(status='maintenance').count()
    
    # Get user role for template conditionals
    try:
        user_role = request.user.role.role
    except:
        user_role = 'guest'
    
    context = {
        'lockers': lockers,
        'locker_types': locker_types,
        'total_lockers': total_lockers,
        'available': available,
        'occupied': occupied,
        'maintenance': maintenance,
        'user_role': user_role,
    }
    return render(request, 'lockers/enhanced_list.html', context)


def locker_detail(request, locker_id):
    """Display detailed information about a locker"""
    locker = get_object_or_404(Locker, id=locker_id)
    bookings = locker.bookings.all()[:10]
    access_logs = locker.access_logs.all()[:20]
    
    context = {
        'locker': locker,
        'bookings': bookings,
        'access_logs': access_logs,
    }
    return render(request, 'lockers/detail.html', context)


@login_required
def book_locker(request, locker_id):
    """Book a locker with transaction locking to prevent double-booking"""
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Lock the locker row to prevent concurrent bookings
                locker = Locker.objects.select_for_update().get(id=locker_id)
                
                # Check availability with lock held
                if not locker.is_available():
                    return JsonResponse({'error': 'Locker not available'}, status=400)
                
                duration_type = request.POST.get('duration_type')
                duration_count = int(request.POST.get('duration_count', 1))
                
                # Calculate dates
                start_date = timezone.now()
                if duration_type == 'hourly':
                    end_date = start_date + timedelta(hours=duration_count)
                    rate = locker.locker_type.hourly_rate
                elif duration_type == 'daily':
                    end_date = start_date + timedelta(days=duration_count)
                    rate = locker.locker_type.daily_rate
                elif duration_type == 'weekly':
                    end_date = start_date + timedelta(weeks=duration_count)
                    rate = locker.locker_type.weekly_rate
                else:  # monthly
                    end_date = start_date + timedelta(days=30 * duration_count)
                    rate = locker.locker_type.monthly_rate
                
                total_amount = rate * duration_count
                
                # Generate access code
                access_code = locker.generate_access_code()
                
                # Create booking
                booking = LockerBooking.objects.create(
                    locker=locker,
                    customer_name=request.POST.get('customer_name'),
                    customer_email=request.POST.get('customer_email'),
                    customer_phone=request.POST.get('customer_phone'),
                    duration_type=duration_type,
                    duration_count=duration_count,
                    start_date=start_date,
                    end_date=end_date,
                    access_code=access_code,
                    total_amount=total_amount,
                    items_description=request.POST.get('items_description', ''),
                    created_by=request.user
                )
                
                # Update locker status atomically
                locker.status = 'occupied'
                locker.save()
                
                # Log access
                LockerAccessLog.objects.create(
                    locker=locker,
                    booking=booking,
                    action='open',
                    access_code_used=access_code,
                    user=request.user,
                    notes='Locker assigned'
                )
                
                return JsonResponse({
                    'success': True,
                    'booking_number': booking.booking_number,
                    'access_code': access_code
                })
        except Locker.DoesNotExist:
            return JsonResponse({'error': 'Locker not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    locker = get_object_or_404(Locker, id=locker_id)
    return render(request, 'lockers/book.html', {'locker': locker})


@login_required
def my_bookings(request):
    """Display user's locker bookings"""
    bookings = LockerBooking.objects.filter(
        created_by=request.user
    ).select_related('locker', 'locker__locker_type')
    
    context = {
        'bookings': bookings,
        'active_count': bookings.filter(status='active').count(),
        'pending_count': bookings.filter(status='pending').count(),
        'completed_count': bookings.filter(status='completed').count(),
    }
    return render(request, 'lockers/my_bookings.html', context)


@login_required
def locker_analytics(request):
    """Display locker analytics - Admin only"""
    from permissions.decorators import get_user_role
    
    # Block customers from accessing analytics
    user_role = get_user_role(request.user)
    if user_role == 'customer':
        from django.contrib import messages
        messages.error(request, 'You do not have permission to access analytics.')
        return redirect('lockers:lockers_list')
    
    lockers = Locker.objects.select_related('locker_type')
    bookings = LockerBooking.objects.all()
    
    # Calculate metrics
    total_revenue = sum(b.total_amount for b in bookings if b.paid)
    avg_duration = bookings.count() / max(lockers.filter(status='occupied').count(), 1)
    
    context = {
        'total_lockers': lockers.count(),
        'available_lockers': lockers.filter(status='available').count(),
        'occupied_lockers': lockers.filter(status='occupied').count(),
        'total_bookings': bookings.count(),
        'active_bookings': bookings.filter(status='active').count(),
        'total_revenue': total_revenue,
        'avg_duration': avg_duration,
    }
    return render(request, 'lockers/analytics.html', context)

@login_required
def locker_booking_detail(request, booking_id):
    """Display detailed information about a locker booking"""
    booking = get_object_or_404(LockerBooking, id=booking_id)
    
    # Check if user owns this booking or is staff
    if booking.created_by != request.user and not request.user.is_staff:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden('You do not have permission to view this booking')
    
    context = {
        'booking': booking,
        'locker': booking.locker,
    }
    return render(request, 'lockers/locker_booking_detail.html', context)

@login_required
def customer_lockers_shop(request):
    """Customer-facing lockers shopping page"""
    lockers = Locker.objects.select_related('locker_type').filter(is_active=True)
    locker_types = LockerType.objects.filter(is_active=True)
    
    # Statistics
    total_lockers = lockers.count()
    available = lockers.filter(status='available').count()
    occupied = lockers.filter(status='occupied').count()
    maintenance = lockers.filter(status='maintenance').count()
    
    context = {
        'lockers': lockers,
        'locker_types': locker_types,
        'total_lockers': total_lockers,
        'available': available,
        'occupied': occupied,
        'maintenance': maintenance,
    }
    return render(request, 'lockers/enhanced_list.html', context)

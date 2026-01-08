from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import models
from datetime import timedelta
import json
from .models import RentalItem, RentalBooking, RentalCategory, MaintenanceSchedule
from permissions.decorators import require_permission

@login_required
def rentals_list(request):
    # All authenticated users can view rentals
    category = request.GET.get('category', 'all')
    if category == 'all' or not category:
        items = RentalItem.objects.all().select_related('category')
    else:
        items = RentalItem.objects.filter(category__category_type=category).select_related('category')
    
    categories = RentalCategory.objects.all()
    
    # Get user role for template conditionals
    try:
        user_role = request.user.role.role
    except:
        user_role = 'guest'
    
    context = {
        'items': items,
        'categories': categories,
        'selected_category': category if category else 'all',
        'user_role': user_role,
    }
    
    # Use the main list template for everyone (admin buttons will be hidden by template conditionals)
    return render(request, 'rentals/enhanced_list.html', context)

@require_permission('rentals', 'view')
def rental_detail(request, item_id):
    item = get_object_or_404(RentalItem, id=item_id)
    return render(request, 'rentals/detail.html', {'item': item})

@require_permission('rentals', 'edit')
def rental_edit(request, item_id):
    item = get_object_or_404(RentalItem, id=item_id)
    if request.method == 'POST':
        item.name = request.POST.get('name', item.name)
        item.description = request.POST.get('description', item.description)
        item.hourly_rate = request.POST.get('hourly_rate', item.hourly_rate)
        item.daily_rate = request.POST.get('daily_rate', item.daily_rate)
        item.weekly_rate = request.POST.get('weekly_rate', item.weekly_rate)
        item.monthly_rate = request.POST.get('monthly_rate', item.monthly_rate)
        item.status = request.POST.get('status', item.status)
        if request.FILES.get('image'):
            item.image = request.FILES['image']
        item.save()
        messages.success(request, 'Item updated successfully!')
        return redirect('rentals_list')
    categories = RentalCategory.objects.all()
    return render(request, 'rentals/edit.html', {'item': item, 'categories': categories})

@require_permission('rentals', 'create')
def rental_book(request, item_id):
    item = get_object_or_404(RentalItem, id=item_id)
    
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        delivery_option = request.POST.get('delivery_option')
        delivery_address = request.POST.get('delivery_address', '')
        duration_type = request.POST.get('duration_type')
        
        # Calculate total amount
        if duration_type == 'hourly':
            total_amount = item.hourly_rate
        elif duration_type == 'daily':
            total_amount = item.daily_rate
        elif duration_type == 'weekly':
            total_amount = item.weekly_rate
        else:
            total_amount = item.monthly_rate
        
        booking = RentalBooking.objects.create(
            item=item,
            customer=request.user,
            start_date=start_date,
            end_date=end_date,
            delivery_option=delivery_option,
            delivery_address=delivery_address,
            total_amount=total_amount,
            status='confirmed'
        )
        
        item.status = 'booked'
        item.save()
        
        messages.success(request, 'Booking confirmed successfully!')
        return redirect('booking_summary', booking_id=booking.id)
    
    return render(request, 'rentals/book.html', {'item': item})


from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

@require_http_methods(["POST"])
@login_required
def update_item_status(request, item_id):
    item = get_object_or_404(RentalItem, id=item_id)
    data = json.loads(request.body)
    item.status = data.get('status')
    item.save()
    return JsonResponse({'success': True})

@require_http_methods(["POST"])
@login_required
def update_item_price(request, item_id):
    from permissions.decorators import get_user_role
    
    # Check permission
    user_role = get_user_role(request.user)
    if user_role not in ['superadmin', 'admin', 'supervisor']:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    item = get_object_or_404(RentalItem, id=item_id)
    data = json.loads(request.body)
    field = data.get('field') + '_rate'
    setattr(item, field, data.get('value'))
    item.save()
    return JsonResponse({'success': True})

@require_http_methods(["POST"])
@require_permission('rentals', 'create')
def duplicate_item(request, item_id):
    item = get_object_or_404(RentalItem, id=item_id)
    item.pk = None
    item.name = item.name + ' (Copy)'
    item.save()
    return JsonResponse({'success': True})

@require_http_methods(["POST"])
@require_permission('rentals', 'create')
def create_booking_api(request):
    data = json.loads(request.body)
    item = get_object_or_404(RentalItem, id=data['item_id'])
    duration_type = data['duration_type']
    duration_count = int(data['duration_count'])
    
    rates = {'hourly': item.hourly_rate, 'daily': item.daily_rate, 'weekly': item.weekly_rate, 'monthly': item.monthly_rate}
    total = rates[duration_type] * duration_count
    
    booking = RentalBooking.objects.create(
        item=item,
        customer=request.user,
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=duration_count),
        delivery_option='pickup',
        total_amount=total,
        status='confirmed'
    )
    
    item.status = 'booked'
    item.save()
    
    return JsonResponse({'success': True, 'booking_number': f'RB{booking.id:05d}'})

@require_permission('rentals', 'view')
@login_required
@require_permission('rentals', 'view')
def analytics_api(request):
    bookings = RentalBooking.objects.filter(status='active')
    total_items = RentalItem.objects.count()
    booked_items = RentalItem.objects.filter(status='booked').count()
    
    return JsonResponse({
        'total_revenue': float(bookings.aggregate(models.Sum('total_amount'))['total_amount__sum'] or 0),
        'active_rentals': bookings.count(),
        'utilization_rate': int((booked_items / total_items * 100) if total_items > 0 else 0),
        'avg_duration': 7,
        'revenue_trend': [1200, 1500, 1800, 2100, 1900, 2300, 2500],
        'category_split': [45, 35, 20]
    })

@require_http_methods(["POST", "DELETE"])
@require_permission('rentals', 'delete')
def delete_item(request, item_id):
    item = get_object_or_404(RentalItem, id=item_id)
    item.delete()
    return JsonResponse({'success': True})

@require_http_methods(["POST", "PUT"])
@login_required
def update_item(request, item_id):
    from permissions.decorators import get_user_role
    
    user_role = get_user_role(request.user)
    if user_role not in ['superadmin', 'admin', 'supervisor', 'staff']:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    item = get_object_or_404(RentalItem, id=item_id)
    
    if request.FILES or request.POST:
        if request.POST.get('name'):
            item.name = request.POST['name']
        if request.POST.get('description'):
            item.description = request.POST['description']
        if request.POST.get('hourly_rate'):
            item.hourly_rate = request.POST['hourly_rate']
        if request.POST.get('daily_rate'):
            item.daily_rate = request.POST['daily_rate']
        if request.POST.get('weekly_rate'):
            item.weekly_rate = request.POST['weekly_rate']
        if request.POST.get('monthly_rate'):
            item.monthly_rate = request.POST['monthly_rate']
        if request.POST.get('status'):
            item.status = request.POST['status']
        if request.FILES.get('image'):
            item.image = request.FILES['image']
        if hasattr(item, 'updated_by'):
            item.updated_by = request.user
    else:
        try:
            data = json.loads(request.body)
            for field in ['name', 'description', 'hourly_rate', 'daily_rate', 'weekly_rate', 'monthly_rate', 'status']:
                if field in data:
                    setattr(item, field, data[field])
            if hasattr(item, 'updated_by'):
                item.updated_by = request.user
        except:
            return JsonResponse({'success': False, 'error': 'Invalid data format'})
    
    item.save()
    return JsonResponse({'success': True})

@require_http_methods(["POST"])
@require_permission('rentals', 'create')
def create_item(request):
    data = json.loads(request.body)
    category = get_object_or_404(RentalCategory, id=data['category_id'])
    
    item = RentalItem.objects.create(
        category=category,
        name=data['name'],
        description=data.get('description', ''),
        hourly_rate=data.get('hourly_rate', 0),
        daily_rate=data.get('daily_rate', 0),
        weekly_rate=data.get('weekly_rate', 0),
        monthly_rate=data.get('monthly_rate', 0)
    )
    
    return JsonResponse({'success': True, 'item_id': item.id})

@require_permission('rentals', 'view')
def booking_summary(request, booking_id):
    booking = get_object_or_404(RentalBooking, id=booking_id)
    return render(request, 'rentals/summary.html', {'booking': booking})

@require_permission('rentals', 'view')
def rental_agreement(request, booking_id):
    booking = get_object_or_404(RentalBooking, id=booking_id)
    booking.agreement_generated = True
    booking.save()
    return render(request, 'rentals/agreement.html', {'booking': booking})

@login_required
def rental_history(request):
    bookings = RentalBooking.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'rentals/history.html', {'bookings': bookings})

@require_permission('rentals', 'view')  # Maintenance view
def maintenance_schedule(request):
    schedules = MaintenanceSchedule.objects.all().order_by('-scheduled_date')
    return render(request, 'rentals/maintenance.html', {'schedules': schedules})

@require_permission('rentals', 'view')
def item_detail_api(request, item_id):
    item = get_object_or_404(RentalItem, id=item_id)
    return JsonResponse({
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'hourly_rate': float(item.hourly_rate or 0),
        'daily_rate': float(item.daily_rate or 0),
        'weekly_rate': float(item.weekly_rate or 0),
        'monthly_rate': float(item.monthly_rate or 0),
        'status': item.status,
        'image_url': item.image.url if item.image else None
    })

@login_required
def rental_booking_detail(request, booking_id):
    booking = get_object_or_404(RentalBooking, id=booking_id)
    
    # Check if user owns this booking or is staff
    if booking.customer != request.user and not request.user.is_staff:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden('You do not have permission to view this booking')
    
    context = {
        'booking': booking,
        'equipment_name': booking.item.name,
        'equipment_type': booking.item.category.name if booking.item.category else 'N/A',
        'booking_id': f"RB{booking.id:05d}",
    }
    return render(request, 'rentals/rental_booking_detail.html', context)


@login_required
def customer_rentals_shop(request):
    """Customer-facing rental shopping page"""
    category = request.GET.get('category', 'all')
    if category == 'all' or not category:
        items = RentalItem.objects.filter(status='available').select_related('category')
    else:
        items = RentalItem.objects.filter(category__category_type=category, status='available').select_related('category')
    
    categories = RentalCategory.objects.all()
    context = {
        'items': items,
        'categories': categories,
        'selected_category': category if category else 'all',
    }
    return render(request, 'rentals/enhanced_list.html', context)

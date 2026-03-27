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
    category = request.GET.get('category', 'all')
    if category == 'all' or not category:
        items = RentalItem.objects.all().select_related('category')
    else:
        items = RentalItem.objects.filter(category__category_type=category).select_related('category')
    categories = RentalCategory.objects.all()
    try:
        user_role = request.user.role.role
    except:
        user_role = 'customer'
    return render(request, 'rentals/enhanced_list.html', {
        'items': items, 'categories': categories,
        'selected_category': category or 'all', 'user_role': user_role,
    })


@require_permission('rentals', 'view')
def rental_detail(request, item_id):
    item = get_object_or_404(RentalItem, id=item_id)
    return render(request, 'rentals/detail.html', {'item': item})


@require_permission('rentals', 'edit')
def rental_edit(request, item_id):
    item = get_object_or_404(RentalItem, id=item_id)
    if request.method == 'POST':
        for field in ['name', 'description', 'hourly_rate', 'daily_rate', 'weekly_rate', 'monthly_rate', 'status']:
            val = request.POST.get(field)
            if val is not None:
                setattr(item, field, val)
        if request.FILES.get('image'):
            item.image = request.FILES['image']
        item.save()
        messages.success(request, 'Item updated successfully!')
        return redirect('rentals_list')
    return render(request, 'rentals/edit.html', {
        'item': item, 'categories': RentalCategory.objects.all()
    })


@login_required
def rental_book(request, item_id):
    """Book a rental — total = rate × duration_count (FIXED)."""
    item = get_object_or_404(RentalItem, id=item_id)
    if item.status == 'booked':
        messages.error(request, 'This item is currently unavailable.')
        return redirect('rentals_list')

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        delivery_option = request.POST.get('delivery_option', 'pickup')
        delivery_address = request.POST.get('delivery_address', '')
        duration_type = request.POST.get('duration_type', 'daily')
        duration_count = max(int(request.POST.get('duration_count', 1)), 1)

        rate_map = {
            'hourly': float(item.hourly_rate or 0),
            'daily':  float(item.daily_rate  or 0),
            'weekly': float(item.weekly_rate  or 0),
            'monthly':float(item.monthly_rate or 0),
        }
        rate = rate_map.get(duration_type, rate_map['daily'])
        total_amount = rate * duration_count  # FIXED: multiply by count

        # Create booking as PENDING — item status set AFTER payment
        booking = RentalBooking.objects.create(
            item=item,
            customer=request.user,
            start_date=start_date,
            end_date=end_date,
            delivery_option=delivery_option,
            delivery_address=delivery_address,
            total_amount=total_amount,
            status='pending',
        )
        messages.success(request, f'Booking created! Total: ₹{total_amount:.2f}. Complete payment to confirm.')
        return redirect('payments:payment_page', booking_type='rental', booking_id=booking.id)

    return render(request, 'rentals/book.html', {'item': item})


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
    if get_user_role(request.user) not in ['superadmin', 'admin', 'supervisor']:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    item = get_object_or_404(RentalItem, id=item_id)
    data = json.loads(request.body)
    field = data.get('field') + '_rate'
    if hasattr(item, field):
        setattr(item, field, data.get('value'))
        item.save()
    return JsonResponse({'success': True})


@require_http_methods(["POST"])
@require_permission('rentals', 'create')
def duplicate_item(request, item_id):
    item = get_object_or_404(RentalItem, id=item_id)
    item.pk = None
    item.name += ' (Copy)'
    item.status = 'available'
    item.save()
    return JsonResponse({'success': True})


@require_http_methods(["POST"])
@login_required
def create_booking_api(request):
    data = json.loads(request.body)
    item = get_object_or_404(RentalItem, id=data['item_id'])
    duration_type = data.get('duration_type', 'daily')
    duration_count = max(int(data.get('duration_count', 1)), 1)
    rates = {
        'hourly': float(item.hourly_rate or 0),
        'daily':  float(item.daily_rate  or 0),
        'weekly': float(item.weekly_rate  or 0),
        'monthly':float(item.monthly_rate or 0),
    }
    total = rates.get(duration_type, rates['daily']) * duration_count
    booking = RentalBooking.objects.create(
        item=item, customer=request.user,
        start_date=timezone.now().date(),
        end_date=(timezone.now() + timedelta(days=duration_count)).date(),
        total_amount=total, status='pending',
    )
    return JsonResponse({
        'success': True, 'booking_id': booking.id, 'total': total,
        'redirect_url': f'/payments/pay/rental/{booking.id}/',
    })


@login_required
def rental_analytics(request):
    bookings = RentalBooking.objects.select_related('item', 'customer')
    return render(request, 'rentals/analytics.html', {
        'total_bookings': bookings.count(),
        'active_bookings': bookings.filter(status='active').count(),
        'total_revenue': float(bookings.aggregate(models.Sum('total_amount'))['total_amount__sum'] or 0),
        'bookings': bookings.order_by('-id')[:20],
    })


@login_required
def booking_summary(request, booking_id):
    booking = get_object_or_404(RentalBooking, id=booking_id)
    return render(request, 'rentals/summary.html', {'booking': booking})


@login_required
def rental_history(request):
    bookings = RentalBooking.objects.filter(customer=request.user).select_related('item').order_by('-id')
    return render(request, 'rentals/history.html', {'bookings': bookings})


@login_required
def maintenance_list(request):
    schedules = MaintenanceSchedule.objects.select_related('item').order_by('-scheduled_date')
    return render(request, 'rentals/maintenance.html', {'schedules': schedules})


@login_required
def maintenance_schedule(request):
    return maintenance_list(request)


@login_required
def customer_rentals_shop(request):
    category = request.GET.get('category', 'all')
    items = RentalItem.objects.all().select_related('category')
    if category and category != 'all':
        items = items.filter(category__category_type=category)
    categories = RentalCategory.objects.all()
    return render(request, 'rentals/customer_shop.html', {
        'items': items, 'categories': categories, 'selected_category': category,
    })


@login_required
def analytics_api(request):
    from django.db.models import Sum
    bookings = RentalBooking.objects.all()
    return JsonResponse({
        'total_bookings': bookings.count(),
        'active': bookings.filter(status='active').count(),
        'revenue': float(bookings.aggregate(Sum('total_amount'))['total_amount__sum'] or 0),
    })


@require_http_methods(["POST"])
@login_required
def update_item(request, item_id):
    item = get_object_or_404(RentalItem, id=item_id)
    data = json.loads(request.body)
    for field in ['name', 'description', 'status', 'hourly_rate', 'daily_rate', 'weekly_rate', 'monthly_rate']:
        if field in data:
            setattr(item, field, data[field])
    item.save()
    return JsonResponse({'success': True})


@require_http_methods(["POST"])
@login_required
def create_item(request):
    data = json.loads(request.body)
    item = RentalItem.objects.create(
        name=data.get('name', 'New Item'),
        description=data.get('description', ''),
        daily_rate=data.get('daily_rate', 0),
        status='available',
    )
    return JsonResponse({'success': True, 'id': item.id})


@login_required
def item_detail_api(request, item_id):
    item = get_object_or_404(RentalItem, id=item_id)
    return JsonResponse({
        'id': item.id, 'name': item.name, 'status': item.status,
        'hourly_rate': str(item.hourly_rate or 0),
        'daily_rate': str(item.daily_rate or 0),
        'weekly_rate': str(item.weekly_rate or 0),
        'monthly_rate': str(item.monthly_rate or 0),
    })


@require_http_methods(["POST"])
@login_required
def delete_item(request, item_id):
    item = get_object_or_404(RentalItem, id=item_id)
    item.delete()
    return JsonResponse({'success': True})


@login_required
def rental_booking_detail(request, booking_id):
    booking = get_object_or_404(RentalBooking, id=booking_id)
    if booking.customer != request.user and not request.user.is_staff:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden('Permission denied')
    return render(request, 'rentals/rental_booking_detail.html', {'booking': booking, 'item': booking.item})


@login_required
def rental_agreement(request, booking_id):
    booking = get_object_or_404(RentalBooking, id=booking_id)
    return render(request, 'rentals/agreement.html', {'booking': booking})

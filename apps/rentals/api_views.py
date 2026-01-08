from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import RentalItem, RentalBooking, RentalCategory
import json

@login_required
@require_http_methods(["GET"])
def analytics_data(request):
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    
    total_revenue = RentalBooking.objects.filter(status__in=['confirmed', 'active', 'completed']).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    active_rentals = RentalBooking.objects.filter(status='active').count()
    total_items = RentalItem.objects.count()
    booked_items = RentalItem.objects.filter(status='booked').count()
    utilization = (booked_items / total_items * 100) if total_items > 0 else 0
    avg_duration = 5
    
    revenue_trend = []
    for i in range(7):
        day = now - timedelta(days=6-i)
        day_revenue = RentalBooking.objects.filter(created_at__date=day.date(), status__in=['confirmed', 'active', 'completed']).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        revenue_trend.append(float(day_revenue))
    
    category_split = []
    for cat_type in ['equipment', 'vehicle', 'event']:
        count = RentalItem.objects.filter(category__category_type=cat_type).count()
        category_split.append(count)
    
    return JsonResponse({
        'total_revenue': float(total_revenue),
        'active_rentals': active_rentals,
        'utilization_rate': round(utilization, 1),
        'avg_duration': avg_duration,
        'revenue_trend': revenue_trend,
        'category_split': category_split
    })

@login_required
@require_http_methods(["POST"])
def update_item_status(request, item_id):
    """Update rental item status - admin only"""
    from permissions.decorators import get_user_role
    
    # Check if user has permission
    user_role = get_user_role(request.user)
    if user_role not in ['superadmin', 'admin', 'subadmin', 'staff']:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    try:
        item = RentalItem.objects.get(id=item_id)
        data = json.loads(request.body)
        item.status = data.get('status')
        item.save()
        return JsonResponse({'success': True})
    except:
        return JsonResponse({'success': False}, status=400)

@login_required
@require_http_methods(["POST"])
def update_item_price(request, item_id):
    try:
        item = RentalItem.objects.get(id=item_id)
        data = json.loads(request.body)
        field = data.get('field')
        value = data.get('value')
        setattr(item, f'{field}_rate', value)
        item.save()
        return JsonResponse({'success': True})
    except:
        return JsonResponse({'success': False}, status=400)

@login_required
@require_http_methods(["POST"])
def duplicate_item(request, item_id):
    """Duplicate rental item - admin only"""
    from permissions.decorators import get_user_role
    
    user_role = get_user_role(request.user)
    if user_role not in ['superadmin', 'admin', 'subadmin']:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    try:
        item = RentalItem.objects.get(id=item_id)
        new_item = RentalItem.objects.create(
            category=item.category,
            name=f"{item.name} (Copy)",
            description=item.description,
            image=item.image,
            specifications=item.specifications,
            status='available',
            hourly_rate=item.hourly_rate,
            daily_rate=item.daily_rate,
            weekly_rate=item.weekly_rate,
            monthly_rate=item.monthly_rate
        )
        return JsonResponse({'success': True, 'id': new_item.id})
    except:
        return JsonResponse({'success': False}, status=400)

@login_required
@require_http_methods(["POST"])
def create_booking(request):
    try:
        data = json.loads(request.body)
        item = RentalItem.objects.get(id=data['item_id'])
        
        duration_type = data['duration_type']
        duration_count = int(data['duration_count'])
        
        rates = {
            'hourly': item.hourly_rate,
            'daily': item.daily_rate,
            'weekly': item.weekly_rate,
            'monthly': item.monthly_rate
        }
        
        total = float(rates[duration_type]) * duration_count
        
        start_date = timezone.now()
        if duration_type == 'hourly':
            end_date = start_date + timedelta(hours=duration_count)
        elif duration_type == 'daily':
            end_date = start_date + timedelta(days=duration_count)
        elif duration_type == 'weekly':
            end_date = start_date + timedelta(weeks=duration_count)
        else:
            end_date = start_date + timedelta(days=duration_count*30)
        
        booking = RentalBooking.objects.create(
            item=item,
            customer=request.user,
            start_date=start_date,
            end_date=end_date,
            delivery_option='pickup',
            total_amount=total,
            status='confirmed'
        )
        
        item.status = 'booked'
        item.save()
        
        return JsonResponse({
            'success': True,
            'booking_id': booking.id,
            'booking_number': f'RNT-{booking.id:05d}'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def cancel_rental_booking(request, booking_id):
    """Cancel a rental booking"""
    from django.shortcuts import get_object_or_404
    
    booking = get_object_or_404(RentalBooking, id=booking_id)
    
    # Check if user owns this booking or is staff
    if booking.customer != request.user and not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Unauthorized'
        }, status=403)
    
    if booking.status not in ['pending', 'confirmed', 'active']:
        return JsonResponse({
            'success': False,
            'message': f'Cannot cancel this booking. Current status: {booking.status}'
        })
    
    # Cancel the booking
    booking.status = 'cancelled'
    booking.save()
    
    # Free up the item
    if booking.item:
        booking.item.status = 'available'
        booking.item.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Rental booking cancelled successfully'
    })

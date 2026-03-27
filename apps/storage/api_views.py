from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import StorageUnit, StorageBooking
import json
import random
import string
import logging

logger = logging.getLogger(__name__)

@login_required
@require_http_methods(["GET"])
def analytics_data(request):
    total_units = StorageUnit.objects.count()
    occupied = StorageUnit.objects.filter(status='occupied').count()
    occupancy_rate = (occupied / total_units * 100) if total_units > 0 else 0
    monthly_revenue = StorageUnit.objects.filter(status='occupied').aggregate(Sum('price_per_month'))['price_per_month__sum'] or 0
    avg_size = StorageUnit.objects.aggregate(Avg('size_sqft'))['size_sqft__avg'] or 0
    
    occupancy_trend = [72, 75, 78, 82, 85, round(occupancy_rate)]
    floor_data = []
    for floor in range(1, 5):
        count = StorageUnit.objects.filter(floor=floor).count()
        floor_data.append(count)
    
    return JsonResponse({
        'total_units': total_units,
        'occupancy_rate': round(occupancy_rate, 1),
        'monthly_revenue': float(monthly_revenue),
        'avg_size': round(avg_size, 1),
        'occupancy_trend': occupancy_trend,
        'floor_data': floor_data
    })

@login_required
@require_http_methods(["POST"])
def update_unit_field(request, unit_id):
    from permissions.decorators import get_user_role
    
    user_role = get_user_role(request.user)
    if user_role not in ['superadmin', 'admin', 'subadmin', 'staff']:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    try:
        unit = StorageUnit.objects.get(id=unit_id)
        
        if request.FILES or request.POST:
            if request.POST.get('unit_number'):
                unit.unit_number = request.POST['unit_number']
            if request.POST.get('type'):
                unit.type = request.POST['type']
            if request.POST.get('size_sqft'):
                unit.size_sqft = request.POST['size_sqft']
            if request.POST.get('location'):
                unit.location = request.POST['location']
            if request.POST.get('floor'):
                unit.floor = request.POST['floor']
            if request.POST.get('zone'):
                unit.zone = request.POST['zone']
            if request.POST.get('price_per_month'):
                unit.price_per_month = request.POST['price_per_month']
            if request.POST.get('status'):
                unit.status = request.POST['status']
            if request.POST.get('features'):
                unit.features = request.POST['features']
            if 'is_climate_controlled' in request.POST:
                unit.is_climate_controlled = request.POST.get('is_climate_controlled') == 'true'
            if request.FILES.get('image'):
                unit.image = request.FILES['image']
            if hasattr(unit, 'updated_by'):
                unit.updated_by = request.user
        else:
            data = json.loads(request.body)
            for field in ['unit_number', 'type', 'size_sqft', 'location', 'floor', 'zone', 'price_per_month', 'status', 'features']:
                if field in data:
                    setattr(unit, field, data[field])
            if 'is_climate_controlled' in data:
                unit.is_climate_controlled = data['is_climate_controlled']
            if hasattr(unit, 'updated_by'):
                unit.updated_by = request.user
        
        unit.save()
        return JsonResponse({'success': True})
    except StorageUnit.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Unit not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def duplicate_unit(request, unit_id):
    """Duplicate storage unit - admin only"""
    from permissions.decorators import get_user_role
    
    user_role = get_user_role(request.user)
    if user_role not in ['superadmin', 'admin', 'subadmin']:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    try:
        unit = StorageUnit.objects.get(id=unit_id)
        new_unit = StorageUnit.objects.create(
            unit_number=f"{unit.unit_number}-COPY",
            type=unit.type,
            size_sqft=unit.size_sqft,
            location=unit.location,
            floor=unit.floor,
            zone=unit.zone,
            status='available',
            price_per_month=unit.price_per_month,
            features=unit.features,
            is_climate_controlled=unit.is_climate_controlled
        )
        return JsonResponse({'success': True, 'id': new_unit.id})
    except:
        return JsonResponse({'success': False}, status=400)

@login_required
@require_http_methods(["DELETE"])
def delete_unit(request, unit_id):
    """Delete storage unit - admin only"""
    from permissions.decorators import get_user_role
    
    user_role = get_user_role(request.user)
    if user_role not in ['superadmin', 'admin']:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    try:
        unit = StorageUnit.objects.get(id=unit_id)
        # Check if unit has active bookings
        if unit.bookings.filter(status='active').exists():
            return JsonResponse({'success': False, 'error': 'Cannot delete unit with active bookings'}, status=400)
        unit.delete()
        return JsonResponse({'success': True})
    except:
        return JsonResponse({'success': False}, status=400)

@login_required
@require_http_methods(["POST"])
def create_booking(request):
    try:
        data = json.loads(request.body)
        unit_id = data.get('unit_id')
        
        if not unit_id:
            return JsonResponse({'success': False, 'error': 'Unit ID required'}, status=400)
        
        unit = StorageUnit.objects.get(id=unit_id)
        duration_months = int(data.get('duration_months', 1))
        start_date = timezone.now()
        end_date = start_date + timedelta(days=duration_months*30)
        total = float(unit.price_per_month) * duration_months
        access_code = ''.join(random.choices(string.digits, k=6))
        
        booking = StorageBooking.objects.create(
            unit=unit,
            user=request.user,
            start_date=start_date,
            end_date=end_date,
            total_amount=total,
            access_code=access_code,
            status='active'
        )
        
        unit.status = 'occupied'
        unit.access_code = access_code
        unit.save()
        
        return JsonResponse({
            'success': True,
            'booking_id': booking.id,
            'booking_number': f'STR-{booking.id:05d}',
            'access_code': access_code
        })
    except StorageUnit.DoesNotExist:
        logger.error(f"Storage unit not found: {data.get('unit_id')}")
        return JsonResponse({'success': False, 'error': 'Storage unit not found'}, status=404)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Booking creation error: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def update_unit_status(request, unit_id):
    """Update storage unit status - admin only"""
    from permissions.decorators import get_user_role
    
    # Check if user has permission
    user_role = get_user_role(request.user)
    if user_role not in ['superadmin', 'admin', 'subadmin', 'staff']:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    try:
        unit = StorageUnit.objects.get(id=unit_id)
        data = json.loads(request.body)
        unit.status = data.get('status')
        unit.save()
        return JsonResponse({'success': True})
    except:
        return JsonResponse({'success': False}, status=400)

@login_required
@require_http_methods(["GET"])
def get_unit_detail(request, unit_id):
    """Get storage unit details for edit modal"""
    try:
        unit = StorageUnit.objects.get(id=unit_id)
        return JsonResponse({
            'id': unit.id,
            'unit_number': unit.unit_number,
            'type': unit.type,
            'size_sqft': float(unit.size_sqft),
            'location': unit.location,
            'floor': unit.floor,
            'zone': unit.zone,
            'price_per_month': float(unit.price_per_month),
            'features': unit.features,
            'is_climate_controlled': unit.is_climate_controlled,
            'status': unit.status,
            'image_url': getattr(unit, 'image', None).url if hasattr(unit, 'image') and unit.image else None
        })
    except StorageUnit.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Unit not found'}, status=404)

@login_required
@require_http_methods(["POST"])
def update_unit_full(request, unit_id):
    """Update storage unit with support for FormData and image uploads - admin only"""
    from permissions.decorators import get_user_role
    
    user_role = get_user_role(request.user)
    if user_role not in ['superadmin', 'admin', 'subadmin', 'staff']:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    try:
        unit = StorageUnit.objects.get(id=unit_id)
        
        if request.POST.get('unit_number'):
            unit.unit_number = request.POST.get('unit_number')
        if request.POST.get('type'):
            unit.type = request.POST.get('type')
        if request.POST.get('size_sqft'):
            unit.size_sqft = request.POST.get('size_sqft')
        if request.POST.get('location'):
            unit.location = request.POST.get('location')
        if request.POST.get('floor'):
            unit.floor = request.POST.get('floor')
        if request.POST.get('zone'):
            unit.zone = request.POST.get('zone')
        if request.POST.get('price_per_month'):
            unit.price_per_month = request.POST.get('price_per_month')
        if request.POST.get('features'):
            unit.features = request.POST.get('features')
        if request.POST.get('status'):
            unit.status = request.POST.get('status')
        
        if 'is_climate_controlled' in request.POST:
            unit.is_climate_controlled = request.POST.get('is_climate_controlled') == 'true'
        
        if request.FILES.get('image'):
            unit.image = request.FILES['image']
        
        unit.save()
        return JsonResponse({'success': True})
    except StorageUnit.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Unit not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def cancel_storage_booking(request, booking_id):
    """Cancel a storage booking"""
    from django.shortcuts import get_object_or_404
    
    booking = get_object_or_404(StorageBooking, id=booking_id)
    
    # Check if user owns this booking or is staff
    if booking.user != request.user and not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Unauthorized'
        }, status=403)
    
    if booking.status not in ['active', 'pending']:
        return JsonResponse({
            'success': False,
            'message': f'Cannot cancel this booking. Current status: {booking.status}'
        })
    
    booking.status = 'cancelled'
    booking.save()
    
    if booking.unit:
        booking.unit.status = 'available'
        booking.unit.access_code = ''
        booking.unit.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Storage booking cancelled successfully'
    })

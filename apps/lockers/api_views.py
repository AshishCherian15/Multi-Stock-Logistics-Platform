from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
import json
from .models import Locker, LockerBooking, LockerAccessLog


@require_http_methods(["POST"])
@login_required
def create_booking(request):
	"""API endpoint to create a new locker booking"""
	try:
		data = json.loads(request.body)
		locker_id = data.get('locker_id')
		
		if not locker_id:
			return JsonResponse({'success': False, 'error': 'Locker ID required'}, status=400)
		
		locker = Locker.objects.get(id=locker_id)
		
		if not locker.is_available():
			return JsonResponse({'success': False, 'error': 'Locker not available'}, status=400)
		
		customer_name = data.get('customer_name') or request.user.get_full_name() or request.user.username
		customer_email = data.get('customer_email') or request.user.email or ''
		customer_phone = data.get('customer_phone') or ''
		duration_type = data.get('duration_type') or 'daily'
		duration_count = int(data.get('duration_count', 1))
		items_description = data.get('items_description') or ''
		
		start_date = timezone.now()
		if duration_type == 'hourly':
			end_date = start_date + timedelta(hours=duration_count)
			rate = float(locker.locker_type.hourly_rate)
		elif duration_type == 'daily':
			end_date = start_date + timedelta(days=duration_count)
			rate = float(locker.locker_type.daily_rate)
		elif duration_type == 'weekly':
			end_date = start_date + timedelta(weeks=duration_count)
			rate = float(locker.locker_type.weekly_rate)
		else:
			end_date = start_date + timedelta(days=30 * duration_count)
			rate = float(locker.locker_type.monthly_rate)
		
		total_amount = rate * duration_count
		access_code = locker.generate_access_code()
		
		booking = LockerBooking.objects.create(
			locker=locker,
			customer_name=customer_name,
			customer_email=customer_email,
			customer_phone=customer_phone,
			duration_type=duration_type,
			duration_count=duration_count,
			start_date=start_date,
			end_date=end_date,
			access_code=access_code,
			total_amount=total_amount,
			items_description=items_description,
			status='active',
			created_by=request.user
		)
		
		locker.status = 'occupied'
		locker.save()
		
		LockerAccessLog.objects.create(
			locker=locker,
			booking=booking,
			action='open',
			access_code_used=access_code,
			user=request.user,
			notes='Locker booked and access code assigned'
		)
		
		return JsonResponse({
			'success': True,
			'booking_id': booking.id,
			'booking_number': booking.booking_number,
			'access_code': access_code,
			'total_amount': float(total_amount),
			'end_date': end_date.isoformat()
		})
		
	except Locker.DoesNotExist:
		return JsonResponse({'success': False, 'error': 'Locker not found'}, status=404)
	except json.JSONDecodeError:
		return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
	except Exception as e:
		import traceback
		traceback.print_exc()
		return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@login_required
def cancel_booking(request, booking_id):
	"""API endpoint to cancel a booking"""
	try:
		booking = LockerBooking.objects.get(id=booking_id)
		
		# Check if user owns this booking or is staff
		if booking.created_by != request.user and not request.user.is_staff:
			return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
		
		# Allow cancellation of pending or active bookings
		if booking.status not in ['pending', 'active']:
			return JsonResponse({'success': False, 'error': 'Can only cancel pending or active bookings'}, status=400)
		
		# Cancel booking
		booking.status = 'cancelled'
		booking.save()
		
		# Update locker status
		booking.locker.status = 'available'
		booking.locker.access_code = ''
		booking.locker.save()
		
		return JsonResponse({'success': True, 'message': 'Booking cancelled successfully'})
		
	except LockerBooking.DoesNotExist:
		return JsonResponse({'success': False, 'error': 'Booking not found'}, status=404)
	except Exception as e:
		return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@login_required
def extend_booking(request, booking_id):
	"""API endpoint to extend a booking"""
	try:
		data = json.loads(request.body)
		booking = LockerBooking.objects.get(id=booking_id)
		
		# Check if user owns this booking
		if booking.created_by != request.user and not request.user.is_staff:
			return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
		
		# Only allow extension of active bookings
		if booking.status != 'active':
			return JsonResponse({'success': False, 'error': 'Can only extend active bookings'}, status=400)
		
		# Get extension duration
		extension_count = int(data.get('extension_count', 1))
		
		# Calculate new end date
		if booking.duration_type == 'hourly':
			new_end_date = booking.end_date + timedelta(hours=extension_count)
			rate = booking.locker.locker_type.hourly_rate
		elif booking.duration_type == 'daily':
			new_end_date = booking.end_date + timedelta(days=extension_count)
			rate = booking.locker.locker_type.daily_rate
		elif booking.duration_type == 'weekly':
			new_end_date = booking.end_date + timedelta(weeks=extension_count)
			rate = booking.locker.locker_type.weekly_rate
		else:  # monthly
			new_end_date = booking.end_date + timedelta(days=30 * extension_count)
			rate = booking.locker.locker_type.monthly_rate
		
		additional_amount = rate * extension_count
		
		# Update booking
		booking.end_date = new_end_date
		booking.duration_count += extension_count
		booking.total_amount += additional_amount
		booking.save()
		
		return JsonResponse({
			'success': True,
			'new_end_date': new_end_date.isoformat(),
			'additional_amount': float(additional_amount),
			'total_amount': float(booking.total_amount)
		})
		
	except LockerBooking.DoesNotExist:
		return JsonResponse({'success': False, 'error': 'Booking not found'}, status=404)
	except Exception as e:
		return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def validate_access_code(request, locker_id):
	"""API endpoint to validate an access code"""
	try:
		locker = Locker.objects.get(id=locker_id)
		code = request.GET.get('code', '')
		
		# Find active booking with this access code
		booking = LockerBooking.objects.filter(
			locker=locker,
			access_code=code,
			status='active'
		).first()
		
		if booking:
			# Check if booking is not expired
			if timezone.now() <= booking.end_date:
				# Log access
				LockerAccessLog.objects.create(
					locker=locker,
					booking=booking,
					action='open',
					access_code_used=code,
					notes='Access code validated successfully'
				)
				return JsonResponse({
					'valid': True,
					'booking_number': booking.booking_number,
					'expires': booking.end_date.isoformat()
				})
			else:
				return JsonResponse({'valid': False, 'error': 'Booking expired'})
		else:
			# Log failed attempt
			LockerAccessLog.objects.create(
				locker=locker,
				action='access_denied',
				access_code_used=code,
				notes='Invalid access code attempt'
			)
			return JsonResponse({'valid': False, 'error': 'Invalid access code'})
		
	except Locker.DoesNotExist:
		return JsonResponse({'valid': False, 'error': 'Locker not found'}, status=404)
	except Exception as e:
		return JsonResponse({'valid': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
@login_required
def get_booking_details(request, booking_id):
	"""API endpoint to get booking details"""
	try:
		booking = LockerBooking.objects.select_related('locker', 'locker__locker_type').get(id=booking_id)
		
		# Check if user owns this booking
		if booking.created_by != request.user and not request.user.is_staff:
			return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
		
		return JsonResponse({
			'success': True,
			'booking': {
				'booking_number': booking.booking_number,
				'locker_number': booking.locker.locker_number,
				'location': booking.locker.location,
				'status': booking.status,
				'access_code': booking.access_code if booking.status == 'active' else None,
				'start_date': booking.start_date.isoformat(),
				'end_date': booking.end_date.isoformat(),
				'total_amount': float(booking.total_amount),
				'paid': booking.paid,
				'duration_type': booking.duration_type,
				'duration_count': booking.duration_count
			}
		})
		
	except LockerBooking.DoesNotExist:
		return JsonResponse({'success': False, 'error': 'Booking not found'}, status=404)
	except Exception as e:
		return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@login_required
def duplicate_locker(request, locker_id):
	"""API endpoint to duplicate a locker - admin only"""
	from permissions.decorators import get_user_role
	
	user_role = get_user_role(request.user)
	if user_role not in ['superadmin', 'admin', 'subadmin']:
		return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
	
	try:
		locker = Locker.objects.get(id=locker_id)
		
		# Create a new locker with copied attributes
		new_locker = Locker.objects.create(
			locker_number=f"{locker.locker_number}-COPY",
			locker_type=locker.locker_type,
			location=locker.location,
			status='available',
			access_code=''
		)
		
		return JsonResponse({
			'success': True,
			'id': new_locker.id,
			'locker_number': new_locker.locker_number
		})
		
	except Locker.DoesNotExist:
		return JsonResponse({'success': False, 'error': 'Locker not found'}, status=404)
	except Exception as e:
		return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@login_required
def update_locker(request, locker_id):
    from permissions.decorators import get_user_role
    
    user_role = get_user_role(request.user)
    if user_role not in ['superadmin', 'admin', 'subadmin', 'staff']:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    try:
        locker = Locker.objects.get(id=locker_id)
        
        if request.FILES or request.POST:
            if request.POST.get('locker_number'):
                locker.locker_number = request.POST['locker_number']
            if request.POST.get('location'):
                locker.location = request.POST['location']
            if request.POST.get('status'):
                locker.status = request.POST['status']
            if request.POST.get('notes'):
                locker.notes = request.POST['notes']
            if request.FILES.get('image'):
                locker.image = request.FILES['image']
            if hasattr(locker, 'updated_by'):
                locker.updated_by = request.user
        else:
            data = json.loads(request.body)
            for field in ['locker_number', 'location', 'status', 'notes']:
                if field in data:
                    setattr(locker, field, data[field])
            if hasattr(locker, 'updated_by'):
                locker.updated_by = request.user
        
        locker.save()
        return JsonResponse({'success': True})
        
    except Locker.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Locker not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["DELETE"])
@login_required
def delete_locker(request, locker_id):
	"""API endpoint to delete a locker - admin only"""
	from permissions.decorators import get_user_role
	
	user_role = get_user_role(request.user)
	if user_role not in ['superadmin', 'admin']:
		return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
	
	try:
		locker = Locker.objects.get(id=locker_id)
		
		# Check if locker has active bookings
		if locker.bookings.filter(status='active').exists():
			return JsonResponse({'success': False, 'error': 'Cannot delete locker with active bookings'}, status=400)
		
		locker.delete()
		return JsonResponse({'success': True})
		
	except Locker.DoesNotExist:
		return JsonResponse({'success': False, 'error': 'Locker not found'}, status=404)
	except Exception as e:
		return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_http_methods(["POST"])
@login_required
def open_locker(request, locker_id):
	"""API endpoint to open a locker"""
	try:
		locker = Locker.objects.get(id=locker_id)
		
		# Find active booking for this user
		booking = LockerBooking.objects.filter(
			locker=locker,
			created_by=request.user,
			status='active'
		).first()
		
		if not booking:
			return JsonResponse({'success': False, 'error': 'No active booking found for this locker'}, status=403)
		
		# Check if booking is not expired
		if timezone.now() > booking.end_date:
			return JsonResponse({'success': False, 'error': 'Booking has expired'}, status=400)
		
		# Log the access
		LockerAccessLog.objects.create(
			locker=locker,
			booking=booking,
			action='open',
			access_code_used=booking.access_code,
			user=request.user,
			notes='Locker opened via customer portal'
		)
		
		return JsonResponse({
			'success': True,
			'message': 'Locker opened successfully',
			'access_code': booking.access_code,
			'locker_number': locker.locker_number
		})
		
	except Locker.DoesNotExist:
		return JsonResponse({'success': False, 'error': 'Locker not found'}, status=404)
	except Exception as e:
		return JsonResponse({'success': False, 'error': str(e)}, status=500)

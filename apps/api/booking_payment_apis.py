"""
Payment and Booking Management APIs
Handles payment processing, agreements, and booking creation for Rentals, Storage, and Lockers
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db import transaction
from datetime import datetime, timedelta
import json

from rentals.models import RentalItem, RentalBooking
from storage.models import StorageUnit, StorageBooking
from lockers.models import Locker, LockerBooking
from permissions.decorators import require_role
from payments.unified_payment import UnifiedPayment


@login_required
@require_http_methods(["POST"])
def process_rental_booking(request):
    """
    Process rental booking with payment and agreement acceptance
    Expects: item_id, duration_type, duration_count, agree_terms, agree_penalty
    """
    try:
        data = json.loads(request.body)
        
        item_id = data.get('item_id')
        duration_type = data.get('duration_type')
        duration_count = int(data.get('duration_count', 1))
        agree_terms = data.get('agree_terms')
        agree_penalty = data.get('agree_penalty')
        agree_liability = data.get('agree_liability')
        
        # Convert to boolean if string
        if isinstance(agree_terms, str):
            agree_terms = agree_terms.lower() == 'true'
        if isinstance(agree_penalty, str):
            agree_penalty = agree_penalty.lower() == 'true'
        if isinstance(agree_liability, str):
            agree_liability = agree_liability.lower() == 'true'
        
        # Validate agreements
        if not (agree_terms and agree_penalty and agree_liability):
            return JsonResponse({
                'success': False,
                'message': 'You must accept all terms and conditions to proceed'
            }, status=400)
        
        # Get rental item
        item = RentalItem.objects.get(id=item_id)
        
        # Calculate amount based on duration
        if duration_type == 'hourly':
            total_amount = item.hourly_rate * duration_count
            end_date = datetime.now() + timedelta(hours=duration_count)
        elif duration_type == 'daily':
            total_amount = item.daily_rate * duration_count
            end_date = datetime.now() + timedelta(days=duration_count)
        elif duration_type == 'weekly':
            total_amount = item.weekly_rate * duration_count
            end_date = datetime.now() + timedelta(weeks=duration_count)
        elif duration_type == 'monthly':
            total_amount = item.monthly_rate * duration_count
            end_date = datetime.now() + timedelta(days=30 * duration_count)
        else:
            return JsonResponse({'success': False, 'message': 'Invalid duration type'}, status=400)
        
        # Create booking
        with transaction.atomic():
            booking = RentalBooking.objects.create(
                customer=request.user,
                item=item,
                start_date=datetime.now(),
                end_date=end_date,
                duration_type=duration_type,
                duration_count=duration_count,
                total_amount=total_amount,
                status='pending',
                terms_agreed=agree_terms,
                penalty_agreed=agree_penalty,
                liability_agreed=agree_liability,
            )
            
            # Reduce stock if item has stock tracking
            if hasattr(item, 'stock_quantity') and item.stock_quantity:
                item.stock_quantity -= 1
                item.save()
            
            # Process payment using unified service
            payment_method = data.get('payment_method', 'online')
            result = UnifiedPayment.process_booking_payment(
                'rental', booking.id, total_amount, payment_method, request.user
            )
            
            if not result['success']:
                return JsonResponse(result, status=400)
            
            return JsonResponse({
                'success': True,
                'message': 'Booking confirmed successfully!',
                'booking_id': booking.id,
                'booking_reference': f'RB{booking.id:05d}',
            })
    
    except RentalItem.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Item not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def process_storage_booking(request):
    """
    Process storage unit booking with payment and agreement acceptance.

    Frontend sends: unit_id, duration_months, start_date, agreements + customer info.
    Backend previously expected an explicit end_date and threw 500 when missing.
    """
    try:
        data = json.loads(request.body)

        unit_id = data.get('unit_id')
        start_date_str = data.get('start_date')
        duration_months = data.get('duration_months')
        agree_terms = data.get('agree_terms')
        agree_penalty = data.get('agree_penalty')
        agree_liability = data.get('agree_liability')

        # Convert to boolean if string
        if isinstance(agree_terms, str):
            agree_terms = agree_terms.lower() == 'true'
        if isinstance(agree_penalty, str):
            agree_penalty = agree_penalty.lower() == 'true'
        if isinstance(agree_liability, str):
            agree_liability = agree_liability.lower() == 'true'

        # Validate agreements
        if not (agree_terms and agree_penalty and agree_liability):
            return JsonResponse({
                'success': False,
                'message': 'You must accept all terms and conditions to proceed'
            }, status=400)

        # Basic required fields
        if not (unit_id and start_date_str and duration_months):
            return JsonResponse({'success': False, 'message': 'Missing required booking fields'}, status=400)

        # Parse start date and duration months
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid start date format (expected YYYY-MM-DD)'}, status=400)

        try:
            duration_months = int(duration_months)
        except (TypeError, ValueError):
            return JsonResponse({'success': False, 'message': 'Invalid duration months'}, status=400)

        if duration_months <= 0:
            return JsonResponse({'success': False, 'message': 'Duration must be at least 1 month'}, status=400)

        # Compute end date based on duration
        end_date = start_date + timedelta(days=30 * duration_months)

        # Get storage unit
        unit = StorageUnit.objects.get(id=unit_id)

        total_amount = unit.price_per_month * duration_months
        
        # Generate access code
        import random, string
        access_code = ''.join(random.choices(string.digits, k=6))

        # Create booking
        with transaction.atomic():
            booking = StorageBooking.objects.create(
                user=request.user,
                unit=unit,
                start_date=start_date,
                end_date=end_date,
                total_amount=total_amount,
                access_code=access_code,
                status='pending',
                terms_agreed=agree_terms,
                penalty_agreed=agree_penalty,
                liability_agreed=agree_liability,
            )

            # Process payment using unified service
            payment_method = data.get('payment_method', 'online')
            result = UnifiedPayment.process_booking_payment(
                'storage', booking.id, total_amount, payment_method, request.user
            )
            
            if not result['success']:
                return JsonResponse(result, status=400)
            
            # Update unit access code
            unit.access_code = access_code
            unit.save()

            return JsonResponse({
                'success': True,
                'message': 'Booking confirmed successfully!',
                'booking_id': booking.id,
                'booking_reference': f'SB{booking.id:05d}',
                'access_code': access_code,
            })

    except StorageUnit.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Unit not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def process_locker_booking(request):
    """
    Process locker booking with payment and agreement acceptance.

    Frontend sends: locker_id, duration_type, duration_count, agreements (+ optional start_date).
    Previously ValueError on blank duration_count caused 500. Now we validate and return 400.
    """
    try:
        data = json.loads(request.body)

        locker_id = data.get('locker_id')
        duration_type = data.get('duration_type')
        duration_count_raw = data.get('duration_count', 1)
        agree_terms = data.get('agree_terms')
        agree_penalty = data.get('agree_penalty')
        agree_liability = data.get('agree_liability')

        # Convert to boolean if string
        if isinstance(agree_terms, str):
            agree_terms = agree_terms.lower() == 'true'
        if isinstance(agree_penalty, str):
            agree_penalty = agree_penalty.lower() == 'true'
        if isinstance(agree_liability, str):
            agree_liability = agree_liability.lower() == 'true'

        # Validate agreements
        if not (agree_terms and agree_penalty and agree_liability):
            return JsonResponse({
                'success': False,
                'message': 'You must accept all terms and conditions to proceed'
            }, status=400)

        # Validate required fields
        if not (locker_id and duration_type):
            return JsonResponse({'success': False, 'message': 'Missing required booking fields'}, status=400)

        # Parse duration count safely
        try:
            duration_count = int(duration_count_raw)
        except (TypeError, ValueError):
            return JsonResponse({'success': False, 'message': 'Invalid duration count'}, status=400)

        if duration_count <= 0:
            return JsonResponse({'success': False, 'message': 'Duration must be positive'}, status=400)

        # Get locker
        locker = Locker.objects.get(id=locker_id)

        locker_type = locker.locker_type
        if not locker_type:
            return JsonResponse({'success': False, 'message': 'Locker type not configured'}, status=400)

        # Calculate amount based on duration
        if duration_type == 'hourly':
            total_amount = locker_type.hourly_rate * duration_count
            end_date = datetime.now() + timedelta(hours=duration_count)
        elif duration_type == 'daily':
            total_amount = locker_type.daily_rate * duration_count
            end_date = datetime.now() + timedelta(days=duration_count)
        elif duration_type == 'weekly':
            total_amount = locker_type.weekly_rate * duration_count
            end_date = datetime.now() + timedelta(weeks=duration_count)
        elif duration_type == 'monthly':
            total_amount = locker_type.monthly_rate * duration_count
            end_date = datetime.now() + timedelta(days=30 * duration_count)
        else:
            return JsonResponse({'success': False, 'message': 'Invalid duration type'}, status=400)

        # Generate access code
        access_code = locker.generate_access_code()
        
        # Get customer info
        customer_name = request.user.get_full_name() or request.user.username
        customer_email = request.user.email or ''
        customer_phone = data.get('customer_phone', '')
        
        # Create booking
        with transaction.atomic():
            booking = LockerBooking.objects.create(
                created_by=request.user,
                locker=locker,
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone,
                duration_type=duration_type,
                duration_count=duration_count,
                start_date=datetime.now(),
                end_date=end_date,
                access_code=access_code,
                total_amount=total_amount,
                status='pending',
                terms_agreed=agree_terms,
                penalty_agreed=agree_penalty,
                liability_agreed=agree_liability,
            )

            # Process payment using unified service
            payment_method = data.get('payment_method', 'online')
            result = UnifiedPayment.process_booking_payment(
                'locker', booking.id, total_amount, payment_method, request.user
            )
            
            if not result['success']:
                return JsonResponse(result, status=400)

            return JsonResponse({
                'success': True,
                'message': 'Booking confirmed successfully!',
                'booking_id': booking.id,
                'booking_reference': f'LB{booking.id:05d}',
            })

    except Locker.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Locker not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_rental_agreement(request, item_id):
    """Get rental agreement and terms for display"""
    try:
        item = RentalItem.objects.get(id=item_id)
        
        return JsonResponse({
            'success': True,
            'agreement': {
                'item_name': item.name,
                'item_description': item.description,
                'hourly_rate': item.hourly_rate,
                'daily_rate': item.daily_rate,
                'weekly_rate': item.weekly_rate,
                'monthly_rate': item.monthly_rate,
            }
        })
    except RentalItem.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Item not found'}, status=404)


@login_required
@require_http_methods(["GET"])
def get_storage_agreement(request, unit_id):
    """Get storage unit agreement and terms for display"""
    try:
        unit = StorageUnit.objects.get(id=unit_id)
        
        return JsonResponse({
            'success': True,
            'agreement': {
                'unit_number': unit.unit_number,
                'unit_type': unit.get_type_display(),
                'size': unit.size_sqft,
                'location': unit.location,
                'monthly_rate': unit.price_per_month,
                'climate_controlled': unit.is_climate_controlled,
            }
        })
    except StorageUnit.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Unit not found'}, status=404)


@login_required
@require_http_methods(["GET"])
def get_locker_agreement(request, locker_id):
    """Get locker agreement and terms for display"""
    try:
        locker = Locker.objects.get(id=locker_id)
        
        return JsonResponse({
            'success': True,
            'agreement': {
                'locker_number': locker.locker_number,
                'locker_type': locker.locker_type.name,
                'size': locker.locker_type.get_size_display(),
                'location': locker.location,
                'hourly_rate': locker.locker_type.hourly_rate,
                'daily_rate': locker.locker_type.daily_rate,
                'weekly_rate': locker.locker_type.weekly_rate,
                'monthly_rate': locker.locker_type.monthly_rate,
            }
        })
    except Locker.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Locker not found'}, status=404)

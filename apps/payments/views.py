from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .unified_payment import UnifiedPayment
from permissions.decorators import get_user_role
import json

@login_required
def process_payment_view(request):
    """Unified payment processing for all booking types"""
    if request.method == 'POST':
        data = json.loads(request.body)
        booking_type = data.get('booking_type')  # 'rental', 'storage', 'locker', 'order'
        booking_id = data.get('booking_id')
        amount = data.get('amount')
        method = data.get('method', 'online')
        
        result = UnifiedPayment.process_booking_payment(
            booking_type, booking_id, amount, method, request.user
        )
        
        return JsonResponse(result)
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def refund_payment_view(request):
    """Process refund for any booking type"""
    user_role = get_user_role(request.user)
    
    if user_role not in ['superadmin', 'admin', 'supervisor']:
        return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        booking_type = data.get('booking_type')
        booking_id = data.get('booking_id')
        
        booking = UnifiedPayment._get_booking(booking_type, booking_id)
        if booking:
            booking.status = 'cancelled'
            if hasattr(booking, 'payment_status'):
                booking.payment_status = 'refunded'
            booking.save()
            return JsonResponse({'success': True, 'message': 'Refund processed'})
        
        return JsonResponse({'success': False, 'message': 'Booking not found'}, status=404)
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def payment_history(request):
    """View payment history for all booking types"""
    from permissions.decorators import get_user_role
    from rentals.models import RentalBooking
    from storage.models import StorageBooking
    from lockers.models import LockerBooking
    from orders.models import Order
    
    user_role = get_user_role(request.user)
    transactions = []
    
    if user_role in ['superadmin', 'admin', 'supervisor', 'staff']:
        rentals = RentalBooking.objects.all()[:20]
        storage = StorageBooking.objects.all()[:20]
        lockers = LockerBooking.objects.all()[:20]
        orders = Order.objects.all()[:20]
    else:
        rentals = RentalBooking.objects.filter(customer=request.user)[:20]
        storage = StorageBooking.objects.filter(user=request.user)[:20]
        lockers = LockerBooking.objects.filter(created_by=request.user)[:20]
        orders = Order.objects.filter(customer_user=request.user)[:20]
    
    for r in rentals:
        transactions.append({
            'type': 'Rental',
            'id': f'RB{r.id:05d}',
            'amount': r.total_amount,
            'status': r.status,
            'date': r.start_date
        })
    
    for s in storage:
        transactions.append({
            'type': 'Storage',
            'id': f'SB{s.id:05d}',
            'amount': s.total_amount,
            'status': s.status,
            'date': s.start_date
        })
    
    for l in lockers:
        transactions.append({
            'type': 'Locker',
            'id': f'LB{l.id:05d}',
            'amount': l.total_amount,
            'status': l.status,
            'date': l.start_date
        })
    
    for o in orders:
        transactions.append({
            'type': 'Order',
            'id': o.order_number,
            'amount': o.total_amount,
            'status': o.status,
            'date': o.created_at
        })
    
    transactions.sort(key=lambda x: x['date'], reverse=True)
    
    return render(request, 'payments/history.html', {'transactions': transactions})

@login_required
def payment_page(request, booking_type, booking_id):
    """Universal payment page for all booking types"""
    booking = UnifiedPayment._get_booking(booking_type, booking_id)
    if not booking:
        messages.error(request, 'Booking not found')
        return redirect('customers:dashboard')
    
    context = {
        'booking_type': booking_type,
        'booking_id': booking_id,
        'amount': booking.total_amount,
        'booking': booking
    }
    return render(request, 'payments/payment.html', context)

@login_required
def process_payment(request):
    return process_payment_view(request)

@csrf_exempt
def payment_webhook(request):
    return JsonResponse({'status': 'received'})

@login_required
def payment_success(request, booking_type, booking_id):
    """Payment success page"""
    return render(request, 'payments/success.html', {
        'booking_type': booking_type,
        'booking_id': booking_id
    })

@login_required
def payment_failed(request, booking_type, booking_id):
    """Payment failed page"""
    return render(request, 'payments/failed.html', {
        'booking_type': booking_type,
        'booking_id': booking_id
    })

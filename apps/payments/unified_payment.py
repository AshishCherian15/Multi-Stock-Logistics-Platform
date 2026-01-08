"""
Unified Payment Service for all booking types
Handles: Marketplace Orders, Rentals, Storage, Lockers
"""
from django.db import transaction
from decimal import Decimal

class UnifiedPayment:
    PAYMENT_METHODS = ['online', 'cod', 'upi', 'card', 'wallet']
    
    @staticmethod
    def process_booking_payment(booking_type, booking_id, amount, payment_method, user):
        """
        Process payment for any booking type
        booking_type: 'rental', 'storage', 'locker', 'order'
        """
        if payment_method not in UnifiedPayment.PAYMENT_METHODS:
            return {'success': False, 'message': 'Invalid payment method'}
        
        try:
            with transaction.atomic():
                # Get booking object
                booking = UnifiedPayment._get_booking(booking_type, booking_id)
                if not booking:
                    return {'success': False, 'message': 'Booking not found'}
                
                # Validate ownership
                if not UnifiedPayment._validate_ownership(booking, user, booking_type):
                    return {'success': False, 'message': 'Unauthorized'}
                
                # Process payment
                if payment_method == 'cod':
                    booking.status = 'confirmed'
                    booking.payment_status = 'pending'
                else:
                    booking.status = 'active'
                    booking.payment_status = 'paid'
                
                booking.payment_method = payment_method
                booking.save()
                
                # Update related item status
                UnifiedPayment._update_item_status(booking, booking_type)
                
                return {
                    'success': True,
                    'message': 'Payment processed successfully',
                    'booking_id': booking.id,
                    'status': booking.status
                }
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def _get_booking(booking_type, booking_id):
        """Get booking object based on type"""
        if booking_type == 'rental':
            from rentals.models import RentalBooking
            return RentalBooking.objects.filter(id=booking_id).first()
        elif booking_type == 'storage':
            from storage.models import StorageBooking
            return StorageBooking.objects.filter(id=booking_id).first()
        elif booking_type == 'locker':
            from lockers.models import LockerBooking
            return LockerBooking.objects.filter(id=booking_id).first()
        elif booking_type == 'order':
            from orders.models import Order
            return Order.objects.filter(id=booking_id).first()
        return None
    
    @staticmethod
    def _validate_ownership(booking, user, booking_type):
        """Validate user owns the booking"""
        if booking_type == 'rental':
            return booking.customer == user
        elif booking_type == 'storage':
            return booking.user == user
        elif booking_type == 'locker':
            return booking.created_by == user
        elif booking_type == 'order':
            return booking.customer_user == user
        return False
    
    @staticmethod
    def _update_item_status(booking, booking_type):
        """Update item/unit status after booking"""
        if booking_type == 'rental' and hasattr(booking, 'item'):
            booking.item.status = 'booked'
            booking.item.save()
        elif booking_type == 'storage' and hasattr(booking, 'unit'):
            booking.unit.status = 'occupied'
            booking.unit.save()
        elif booking_type == 'locker' and hasattr(booking, 'locker'):
            booking.locker.status = 'occupied'
            booking.locker.save()

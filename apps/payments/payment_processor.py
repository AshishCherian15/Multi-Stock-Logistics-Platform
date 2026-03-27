from decimal import Decimal
from django.utils import timezone


class PaymentProcessor:
    METHODS = ['card', 'upi', 'netbanking', 'cod', 'wallet']

    @staticmethod
    def process_payment(order_id, amount, method, user_id):
        if method not in PaymentProcessor.METHODS:
            return {'status': 'error', 'message': 'Invalid payment method'}
        try:
            from orders.models import Order
            from django.contrib.auth.models import User
            from .models import Payment

            order = Order.objects.get(id=order_id)
            user = User.objects.get(id=user_id)
            payment_status = 'pending' if method == 'cod' else 'completed'
            order_payment_status = 'unpaid' if method == 'cod' else 'paid'

            payment = Payment.objects.create(
                order=order,
                payment_method=method,
                amount=Decimal(str(amount)),
                status=payment_status,
                user=user,
            )
            order.payment_status = order_payment_status
            order.payment_method = method
            order.save(update_fields=['payment_status', 'payment_method', 'updated_at'])

            return {
                'status': 'success',
                'transaction_id': payment.id,
                'payment_status': payment_status,
                'message': 'Payment processed successfully',
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    @staticmethod
    def refund_payment(payment_id, amount):
        try:
            from .models import Payment
            payment = Payment.objects.get(id=payment_id)
            payment.status = 'refunded'
            payment.save(update_fields=['status', 'updated_at'])
            order = payment.order
            order.payment_status = 'refunded'
            order.save(update_fields=['payment_status', 'updated_at'])
            return {'status': 'success', 'message': 'Refund processed'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

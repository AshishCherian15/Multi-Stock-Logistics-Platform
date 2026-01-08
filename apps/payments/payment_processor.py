from django.db import connection
from decimal import Decimal

class PaymentProcessor:
    METHODS = ['card', 'upi', 'netbanking', 'cod', 'wallet']
    
    @staticmethod
    def process_payment(order_id, amount, method, user_id):
        if method not in PaymentProcessor.METHODS:
            return {'status': 'error', 'message': 'Invalid payment method'}
        
        with connection.cursor() as cursor:
            # Create payment record
            cursor.execute('''
                INSERT INTO payments_transaction 
                (order_id, amount, method, status, user_id, created_at)
                VALUES (?, ?, ?, 'pending', ?, datetime('now'))
            ''', [order_id, amount, method, user_id])
            
            transaction_id = cursor.lastrowid
            
            # Simulate payment processing
            if method == 'cod':
                status = 'pending'
            else:
                status = 'completed'
            
            # Update transaction status
            cursor.execute('''
                UPDATE payments_transaction 
                SET status = ?, completed_at = datetime('now')
                WHERE id = ?
            ''', [status, transaction_id])
            
            # Update order payment status
            cursor.execute('''
                UPDATE orders_order 
                SET payment_status = ?, payment_method = ?
                WHERE id = ?
            ''', [status if status == 'completed' else 'unpaid', method, order_id])
        
        return {
            'status': 'success',
            'transaction_id': transaction_id,
            'payment_status': status,
            'message': 'Payment processed successfully'
        }
    
    @staticmethod
    def refund_payment(transaction_id, amount):
        with connection.cursor() as cursor:
            cursor.execute('''
                UPDATE payments_transaction 
                SET status = 'refunded', refund_amount = ?, refunded_at = datetime('now')
                WHERE id = ?
            ''', [amount, transaction_id])
            
            cursor.execute('SELECT order_id FROM payments_transaction WHERE id = ?', [transaction_id])
            order_id = cursor.fetchone()[0]
            
            cursor.execute('''
                UPDATE orders_order SET payment_status = 'refunded' WHERE id = ?
            ''', [order_id])
        
        return {'status': 'success', 'message': 'Refund processed'}

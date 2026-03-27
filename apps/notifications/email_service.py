from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
import logging
import random

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def send_email(to_email, subject, message, email_type='general'):
        """Universal email sender"""
        try:
            result = send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [to_email],
                fail_silently=False
            )
            logger.info(f'{email_type} email sent to {to_email}')
            return result
        except Exception as e:
            logger.error(f'Error sending {email_type} email: {str(e)}')
            return False

class EmailService:
    @staticmethod
    def send_email(to_email, subject, message, email_type='general'):
        """Universal email sender"""
        try:
            result = send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [to_email],
                fail_silently=False
            )
            logger.info(f'{email_type} email sent to {to_email}')
            return result
        except Exception as e:
            logger.error(f'Error sending {email_type} email: {str(e)}')
            return False

def send_order_confirmation(order):
    """Send order confirmation email"""
    try:
        if not order.customer_user or not order.customer_user.email:
            logger.warning(f'Order {order.order_number}: No customer email')
            return
        
        subject = f'Order Confirmation - {order.order_number}'
        message = f'''Dear Customer,

Your order has been confirmed!

Order Number: {order.order_number}
Total Amount: ₹{order.total_amount}
Status: {order.get_status_display()}

Thank you for shopping with MultiStock!

Best regards,
MultiStock Team
'''
        
        result = send_mail(
            subject, 
            message, 
            settings.DEFAULT_FROM_EMAIL, 
            [order.customer_user.email], 
            fail_silently=False
        )
        
        if result:
            logger.info(f'Order confirmation sent to {order.customer_user.email}')
        else:
            logger.error(f'Failed to send order confirmation to {order.customer_user.email}')
            
    except Exception as e:
        logger.error(f'Error sending order confirmation: {str(e)}')

def send_low_stock_alert(goods_code, goods_desc, quantity):
    """Send low stock alert to admins"""
    try:
        from django.contrib.auth.models import User
        admins = User.objects.filter(is_staff=True, email__isnull=False).exclude(email='')
        
        if not admins.exists():
            logger.warning('No admin emails configured for stock alerts')
            return
        
        admin_emails = [a.email for a in admins]
        subject = f'⚠️ Low Stock Alert - {goods_code}'
        message = f'''STOCK ALERT

Product: {goods_desc}
Product Code: {goods_code}
Current Stock: {quantity} units
Status: LOW STOCK

Action Required: Please reorder stock to avoid stockout.

MultiStock Inventory System
'''
        
        result = send_mail(
            subject, 
            message, 
            settings.DEFAULT_FROM_EMAIL, 
            admin_emails, 
            fail_silently=False
        )
        
        if result:
            logger.info(f'Low stock alert sent to {len(admin_emails)} admins')
        else:
            logger.error('Failed to send low stock alert')
            
    except Exception as e:
        logger.error(f'Error sending low stock alert: {str(e)}')

def send_out_of_stock_alert(goods_code, goods_desc):
    """Send out of stock alert to admins"""
    try:
        from django.contrib.auth.models import User
        admins = User.objects.filter(is_staff=True, email__isnull=False).exclude(email='')
        
        if not admins.exists():
            logger.warning('No admin emails configured for stock alerts')
            return
        
        admin_emails = [a.email for a in admins]
        subject = f'🚨 CRITICAL: OUT OF STOCK - {goods_code}'
        message = f'''CRITICAL STOCK ALERT

Product: {goods_desc}
Product Code: {goods_code}
Current Stock: 0 units
Status: OUT OF STOCK

URGENT ACTION REQUIRED: Product is completely out of stock!
Please reorder immediately to fulfill pending orders.

MultiStock Inventory System
'''
        
        result = send_mail(
            subject, 
            message, 
            settings.DEFAULT_FROM_EMAIL, 
            admin_emails, 
            fail_silently=False
        )
        
        if result:
            logger.info(f'Out of stock alert sent to {len(admin_emails)} admins')
        else:
            logger.error('Failed to send out of stock alert')
            
    except Exception as e:
        logger.error(f'Error sending out of stock alert: {str(e)}')

def send_order_cancelled(order):
    """Send order cancellation email"""
    try:
        if not order.customer_user or not order.customer_user.email:
            logger.warning(f'Order {order.order_number}: No customer email')
            return
        
        subject = f'Order Cancelled - {order.order_number}'
        message = f'''Dear Customer,

Your order has been cancelled.

Order Number: {order.order_number}
Total Amount: ₹{order.total_amount}
Status: Cancelled

Stock has been restored to inventory.
If you have any questions, please contact our support team.

Best regards,
MultiStock Team
'''
        
        result = send_mail(
            subject, 
            message, 
            settings.DEFAULT_FROM_EMAIL, 
            [order.customer_user.email], 
            fail_silently=False
        )
        
        if result:
            logger.info(f'Order cancellation sent to {order.customer_user.email}')
        else:
            logger.error(f'Failed to send order cancellation to {order.customer_user.email}')
            
    except Exception as e:
        logger.error(f'Error sending order cancellation: {str(e)}')

def send_welcome_email(user):
    """Send welcome email to new customer"""
    try:
        if not user.email:
            return
        
        subject = 'Welcome to MultiStock!'
        message = f'''Dear {user.username},

Welcome to MultiStock - Your Complete Inventory Management Solution!

Your account has been successfully created. You can now:
- Browse our marketplace
- Place orders
- Track shipments
- Manage your profile

Get started: http://127.0.0.1:8000/dashboard/

Best regards,
MultiStock Team
'''
        
        EmailService.send_email(user.email, subject, message, 'welcome')
    except Exception as e:
        logger.error(f'Error sending welcome email: {str(e)}')

def send_supplier_notification(supplier, product, message_text):
    """Send notification to supplier"""
    try:
        if not hasattr(supplier, 'supplier_contact') or not supplier.supplier_contact:
            return
        
        subject = f'Supplier Notification - {product.goods_name if product else "Product"}'
        message = f'''Dear {supplier.supplier_name},

{message_text}

Product: {product.goods_name if product else "N/A"}
Product Code: {product.goods_code if product else "N/A"}

Please take necessary action.

Best regards,
MultiStock Team
'''
        
        EmailService.send_email(supplier.supplier_contact, subject, message, 'supplier_notification')
    except Exception as e:
        logger.error(f'Error sending supplier notification: {str(e)}')

def send_invoice_email(order, invoice_pdf=None):
    """Send invoice email to customer"""
    try:
        if not order.customer_user or not order.customer_user.email:
            return
        
        subject = f'Invoice - Order {order.order_number}'
        message = f'''Dear Customer,

Please find your invoice for order {order.order_number}.

Order Number: {order.order_number}
Total Amount: ₹{order.total_amount}
Date: {order.created_at.strftime("%Y-%m-%d")}

Thank you for your business!

Best regards,
MultiStock Team
'''
        
        EmailService.send_email(order.customer_user.email, subject, message, 'invoice')
    except Exception as e:
        logger.error(f'Error sending invoice email: {str(e)}')

def send_otp_email(user, otp_code):
    """Send OTP verification email"""
    try:
        if not user.email:
            return
        
        subject = 'Your OTP Code - MultiStock'
        message = f'''Dear {user.username},

Your OTP code is: {otp_code}

This code will expire in 10 minutes.
Do not share this code with anyone.

Best regards,
MultiStock Team
'''
        
        EmailService.send_email(user.email, subject, message, 'otp')
    except Exception as e:
        logger.error(f'Error sending OTP email: {str(e)}')

def generate_otp():
    """Generate 6-digit OTP"""
    return str(random.randint(100000, 999999))

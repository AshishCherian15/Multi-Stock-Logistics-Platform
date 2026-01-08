# Email Notification Utilities

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

def send_order_confirmation_email(order):
    """Send order confirmation email to customer"""
    try:
        subject = f'Order Confirmation - {order.order_number}'
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd;">
                <h2 style="color: #4CAF50;">Order Confirmed!</h2>
                <p>Dear {order.customer_user.get_full_name() or order.customer_user.username},</p>
                <p>Thank you for your order. Your order has been confirmed and is being processed.</p>
                
                <div style="background: #f9f9f9; padding: 15px; margin: 20px 0; border-left: 4px solid #4CAF50;">
                    <h3 style="margin-top: 0;">Order Details</h3>
                    <p><strong>Order Number:</strong> {order.order_number}</p>
                    <p><strong>Order Date:</strong> {order.created_at.strftime('%B %d, %Y')}</p>
                    <p><strong>Total Amount:</strong> ₹{order.grand_total}</p>
                    <p><strong>Payment Status:</strong> {order.get_payment_status_display()}</p>
                </div>
                
                <p style="margin-top: 30px;">You can track your order status in your account dashboard.</p>
                
                <p>Thank you for shopping with MultiStock!</p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="font-size: 12px; color: #666;">
                    This is an automated email. Please do not reply to this message.
                </p>
            </div>
        </body>
        </html>
        """
        
        plain_message = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [order.customer_user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        return True
    except Exception as e:
        print(f"Error sending order confirmation email: {e}")
        return False


def send_booking_confirmation_email(booking, booking_type):
    """Send booking confirmation email"""
    try:
        # Get user email based on booking type
        if booking_type == 'Rental':
            user_email = booking.customer.email
            user_name = booking.customer.get_full_name() or booking.customer.username
        elif booking_type == 'Storage':
            user_email = booking.user.email
            user_name = booking.user.get_full_name() or booking.user.username
        else:  # Locker
            user_email = booking.created_by.email
            user_name = booking.created_by.get_full_name() or booking.created_by.username
        
        subject = f'{booking_type} Booking Confirmation'
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd;">
                <h2 style="color: #2196F3;">{booking_type} Booking Confirmed!</h2>
                <p>Dear {user_name},</p>
                <p>Your {booking_type.lower()} booking has been confirmed.</p>
                
                <div style="background: #f9f9f9; padding: 15px; margin: 20px 0; border-left: 4px solid #2196F3;">
                    <h3 style="margin-top: 0;">Booking Details</h3>
                    <p><strong>Booking ID:</strong> #{booking.id}</p>
                    <p><strong>Status:</strong> {booking.status.title()}</p>
                    <p><strong>Total Amount:</strong> ₹{booking.total_amount}</p>
                </div>
                
                <p>You can view your booking details in your account dashboard.</p>
                
                <p>Thank you for choosing MultiStock!</p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="font-size: 12px; color: #666;">
                    This is an automated email. Please do not reply to this message.
                </p>
            </div>
        </body>
        </html>
        """
        
        plain_message = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        return True
    except Exception as e:
        print(f"Error sending booking confirmation email: {e}")
        return False


def send_ticket_created_email(ticket):
    """Send email when support ticket is created"""
    try:
        subject = f'Support Ticket Created - {ticket.ticket_number}'
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd;">
                <h2 style="color: #FF9800;">Support Ticket Created</h2>
                <p>Dear {ticket.user.get_full_name() or ticket.user.username},</p>
                <p>Your support ticket has been created successfully.</p>
                
                <div style="background: #f9f9f9; padding: 15px; margin: 20px 0; border-left: 4px solid #FF9800;">
                    <h3 style="margin-top: 0;">Ticket Details</h3>
                    <p><strong>Ticket Number:</strong> {ticket.ticket_number}</p>
                    <p><strong>Subject:</strong> {ticket.subject}</p>
                    <p><strong>Status:</strong> {ticket.get_status_display()}</p>
                    <p><strong>Priority:</strong> {ticket.get_priority_display()}</p>
                </div>
                
                <p>Our support team will respond to your ticket shortly.</p>
                
                <p>Thank you for contacting MultiStock Support!</p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="font-size: 12px; color: #666;">
                    This is an automated email. Please do not reply to this message.
                </p>
            </div>
        </body>
        </html>
        """
        
        plain_message = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [ticket.user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        return True
    except Exception as e:
        print(f"Error sending ticket created email: {e}")
        return False

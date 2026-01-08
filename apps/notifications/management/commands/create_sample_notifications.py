from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from notifications.models import Notification

class Command(BaseCommand):
    help = 'Create sample notifications for testing'

    def handle(self, *args, **kwargs):
        # Get superuser
        try:
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                self.stdout.write(self.style.ERROR('No superuser found'))
                return
            
            # Create sample notifications
            notifications = [
                {
                    'title': 'Welcome to MultiStock!',
                    'message': 'Your account has been successfully set up. Start managing your inventory now.',
                    'type': 'success',
                    'category': 'system',
                    'icon': 'check-circle',
                    'link': '/dashboard/'
                },
                {
                    'title': 'Low Stock Alert',
                    'message': 'Product "Memory Foam Pillow" is running low. Only 5 units remaining.',
                    'type': 'warning',
                    'category': 'stock',
                    'icon': 'exclamation-triangle',
                    'link': '/products/'
                },
                {
                    'title': 'New Order Received',
                    'message': 'Order #ORD-10029 has been placed by customer John Doe.',
                    'type': 'info',
                    'category': 'order',
                    'icon': 'shopping-cart',
                    'link': '/orders/'
                },
                {
                    'title': 'Payment Confirmed',
                    'message': 'Payment of ₹15,000 received for Order #ORD-10028.',
                    'type': 'success',
                    'category': 'payment',
                    'icon': 'credit-card',
                    'link': '/orders/'
                },
                {
                    'title': 'Stock Replenished',
                    'message': '50 units of "Power Drill Set" added to warehouse inventory.',
                    'type': 'success',
                    'category': 'stock',
                    'icon': 'boxes',
                    'link': '/stock/'
                },
                {
                    'title': 'New Message',
                    'message': 'You have a new message from supplier ABC Corp.',
                    'type': 'info',
                    'category': 'message',
                    'icon': 'envelope',
                    'link': '/messages/'
                },
                {
                    'title': 'System Maintenance',
                    'message': 'Scheduled maintenance on Dec 10, 2025 from 2:00 AM to 4:00 AM.',
                    'type': 'alert',
                    'category': 'system',
                    'icon': 'tools',
                    'link': '/system-status/'
                },
            ]
            
            created_count = 0
            for notif_data in notifications:
                Notification.objects.create(
                    user=user,
                    **notif_data
                )
                created_count += 1
            
            self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} sample notifications for {user.username}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))

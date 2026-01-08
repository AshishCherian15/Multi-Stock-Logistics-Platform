from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from messaging.models import Message

class Command(BaseCommand):
    help = 'Send welcome message to new users'

    def handle(self, *args, **kwargs):
        from datetime import timedelta
        from django.utils import timezone
        
        yesterday = timezone.now() - timedelta(days=1)
        new_users = User.objects.filter(date_joined__gte=yesterday)
        
        for user in new_users:
            existing = Message.objects.filter(recipient=user, subject__contains='Welcome').exists()
            if not existing:
                Message.objects.create(
                    sender=None,
                    recipient=user,
                    subject='Welcome to MultiStock Logistics Platform!',
                    body=f'''Dear {user.get_full_name() or user.username},

Welcome to MultiStock Logistics Platform - Your Complete Warehouse & Logistics Management Solution!

We're excited to have you on board. Here's what you can do:

✓ Manage Products & Inventory in real-time
✓ Process Sales & Purchase Orders with full tracking
✓ Track Shipments & Deliveries across multiple carriers
✓ Manage Customers & Suppliers efficiently
✓ Generate Reports & Analytics
✓ Access Revenue Modules (Rentals, Storage, Lockers)
✓ Explore Marketplace & Community Forums

Need help? Visit our Help Center or contact support.

Best regards,
MultiStock Team''',
                    is_system_message=True
                )
                self.stdout.write(self.style.SUCCESS(f'Welcome message sent to {user.username}'))

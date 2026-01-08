from django.core.management.base import BaseCommand
from notifications.models import Notification
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Populate notifications'

    def handle(self, *args, **kwargs):
        users = list(User.objects.all()[:10])
        if not users:
            self.stdout.write(self.style.ERROR('No users'))
            return

        types = [
            ('order', 'New order #ORD-{} received', 'info'),
            ('stock', 'Low stock alert for Product-{}', 'warning'),
            ('payment', 'Payment received ₹{}', 'success'),
            ('shipment', 'Shipment #{} dispatched', 'info'),
        ]

        created = 0
        for i in range(30):
            user = random.choice(users)
            ntype, msg, level = random.choice(types)
            
            Notification.objects.create(
                user=user,
                type=ntype,
                title=f'{ntype.title()} Update',
                message=msg.format(random.randint(1000, 9999)),
                category=level,
                is_read=random.choice([True, False]),
                created_at=datetime.now() - timedelta(days=random.randint(0, 7))
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {created} notifications'))

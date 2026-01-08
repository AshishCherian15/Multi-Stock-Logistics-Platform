from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.settings.models import Announcement

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate sample announcements'

    def handle(self, *args, **kwargs):
        superadmin = User.objects.filter(role__role='superadmin').first()
        if not superadmin:
            self.stdout.write(self.style.ERROR('No superadmin found'))
            return

        announcements = [
            {
                'title': 'System Maintenance Scheduled',
                'message': 'Scheduled maintenance on Dec 25, 2024 from 2:00 AM to 4:00 AM. System will be unavailable during this time.',
                'priority': 'high',
                'target_roles': [],
            },
            {
                'title': 'New Feature: Barcode Scanning',
                'message': 'We have added barcode scanning functionality to streamline inventory management. Check it out in the Core Operations section.',
                'priority': 'medium',
                'target_roles': ['superadmin', 'admin', 'supervisor', 'staff'],
            },
            {
                'title': 'Holiday Season Sale',
                'message': 'Special discounts available for bulk orders during the holiday season. Contact sales team for details.',
                'priority': 'low',
                'target_roles': ['customer'],
            },
            {
                'title': 'Security Update Required',
                'message': 'Please update your password if you have not changed it in the last 90 days. Go to Settings > Security.',
                'priority': 'critical',
                'target_roles': [],
            },
            {
                'title': 'Inventory Audit Completed',
                'message': 'Annual inventory audit completed successfully. All discrepancies have been resolved.',
                'priority': 'medium',
                'target_roles': ['superadmin', 'admin', 'supervisor'],
            },
        ]

        created_count = 0
        for ann_data in announcements:
            Announcement.objects.create(
                title=ann_data['title'],
                message=ann_data['message'],
                priority=ann_data['priority'],
                target_roles=ann_data['target_roles'],
                created_by=superadmin,
                is_active=True
            )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Created {created_count} announcements'))


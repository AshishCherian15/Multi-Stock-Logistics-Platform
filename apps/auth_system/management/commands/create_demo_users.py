from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create demo users for testing'

    def handle(self, *args, **options):
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created admin user: admin/admin123'))

        # Create customer user
        if not User.objects.filter(username='customer').exists():
            User.objects.create_user('customer', 'customer@example.com', 'customer123')
            self.stdout.write(self.style.SUCCESS('Created customer user: customer/customer123'))

        self.stdout.write(self.style.SUCCESS('Demo users created successfully!'))
"""
Management command to set up role-based user credentials
Admin: admin / admin123
SuperAdmin: superadmin / superadmin123
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from permissions.models import UserRole


class Command(BaseCommand):
    help = 'Set up role-based user credentials (admin and superadmin)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== Setting up Role Credentials ===\n'))
        
        # 1. Create/Update SuperAdmin user
        self.stdout.write('Setting up SuperAdmin...')
        superadmin_user, created = User.objects.update_or_create(
            username='superadmin',
            defaults={
                'is_superuser': True,
                'is_staff': True,
                'is_active': True,
                'email': 'superadmin@multistock.com',
                'first_name': 'Super',
                'last_name': 'Admin'
            }
        )
        superadmin_user.set_password('superadmin123')
        superadmin_user.save()
        
        action = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(f'  ✅ {action} SuperAdmin user'))
        self.stdout.write(f'     Username: superadmin')
        self.stdout.write(f'     Password: superadmin123')
        self.stdout.write(f'     Role: SuperAdmin (is_superuser=True)')
        
        # 2. Create/Update Admin user
        self.stdout.write('\nSetting up Admin...')
        admin_user, created = User.objects.update_or_create(
            username='admin',
            defaults={
                'is_superuser': False,  # NOT a superuser
                'is_staff': True,
                'is_active': True,
                'email': 'admin@multistock.com',
                'first_name': 'Admin',
                'last_name': 'User'
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()
        
        # Assign admin role via UserRole
        user_role, role_created = UserRole.objects.update_or_create(
            user=admin_user,
            defaults={
                'role': 'admin',
                'scope': {}  # Empty dict for JSONField
            }
        )
        
        action = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(f'  ✅ {action} Admin user'))
        self.stdout.write(f'     Username: admin')
        self.stdout.write(f'     Password: admin123')
        self.stdout.write(f'     Role: admin (via UserRole model)')
        
        self.stdout.write(self.style.SUCCESS('\n=== Credentials Setup Complete ===\n'))
        self.stdout.write('You can now login with:')
        self.stdout.write('  • SuperAdmin: superadmin / superadmin123')
        self.stdout.write('  • Admin: admin / admin123\n')

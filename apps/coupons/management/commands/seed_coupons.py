from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from coupons.models import Coupon

class Command(BaseCommand):
    help = 'Seed sample coupons'

    def handle(self, *args, **kwargs):
        superuser = User.objects.filter(is_superuser=True).first()
        if not superuser:
            self.stdout.write(self.style.ERROR('No superuser found'))
            return

        coupons_data = [
            {
                'code': 'WELCOME10',
                'description': 'Welcome discount - 10% off on first purchase',
                'discount_type': 'percent',
                'discount_value': 10,
                'min_amount': 500,
                'applicable_to': 'all',
                'usage_limit': 100,
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=30)
            },
            {
                'code': 'RENTAL20',
                'description': '20% off on all rentals',
                'discount_type': 'percent',
                'discount_value': 20,
                'min_amount': 1000,
                'max_discount': 500,
                'applicable_to': 'rentals',
                'usage_limit': 50,
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=60)
            },
            {
                'code': 'STORAGE100',
                'description': 'Flat ₹100 off on storage units',
                'discount_type': 'fixed',
                'discount_value': 100,
                'min_amount': 500,
                'applicable_to': 'storage',
                'usage_limit': None,
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=90)
            },
            {
                'code': 'LOCKER50',
                'description': 'Flat ₹50 off on locker bookings',
                'discount_type': 'fixed',
                'discount_value': 50,
                'min_amount': 200,
                'applicable_to': 'lockers',
                'usage_limit': 200,
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=45)
            },
            {
                'code': 'SHOP15',
                'description': '15% off on marketplace purchases',
                'discount_type': 'percent',
                'discount_value': 15,
                'min_amount': 1000,
                'max_discount': 300,
                'applicable_to': 'marketplace',
                'usage_limit': None,
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=30)
            },
            {
                'code': 'MEGA500',
                'description': 'Mega sale - ₹500 off on orders above ₹5000',
                'discount_type': 'fixed',
                'discount_value': 500,
                'min_amount': 5000,
                'applicable_to': 'all',
                'usage_limit': 25,
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=15)
            },
            {
                'code': 'FLASH25',
                'description': 'Flash sale - 25% off (limited time)',
                'discount_type': 'percent',
                'discount_value': 25,
                'min_amount': 2000,
                'max_discount': 1000,
                'applicable_to': 'all',
                'usage_limit': 50,
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=7)
            },
            {
                'code': 'POS10',
                'description': '10% off on POS purchases',
                'discount_type': 'percent',
                'discount_value': 10,
                'min_amount': 500,
                'applicable_to': 'pos',
                'usage_limit': None,
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=60)
            }
        ]

        created = 0
        for data in coupons_data:
            coupon, created_flag = Coupon.objects.get_or_create(
                code=data['code'],
                defaults={**data, 'created_by': superuser}
            )
            if created_flag:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'Created coupon: {coupon.code}'))
            else:
                self.stdout.write(self.style.WARNING(f'Coupon already exists: {coupon.code}'))

        self.stdout.write(self.style.SUCCESS(f'\nTotal coupons created: {created}'))

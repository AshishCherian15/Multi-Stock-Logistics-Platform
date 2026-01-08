from django.core.management.base import BaseCommand
from coupons.models import Coupon
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populate sample coupons'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        
        coupons_data = [
            {'code': 'WELCOME10', 'description': 'Welcome offer - 10% off on first order', 'discount_type': 'percentage', 'discount_value': 10, 'min_purchase': 500, 'max_uses': 100, 'valid_from': now, 'valid_to': now + timedelta(days=30)},
            {'code': 'SAVE20', 'description': 'Save 20% on orders above ₹2000', 'discount_type': 'percentage', 'discount_value': 20, 'min_purchase': 2000, 'max_uses': 50, 'valid_from': now, 'valid_to': now + timedelta(days=15)},
            {'code': 'FLAT100', 'description': 'Flat ₹100 off on all orders', 'discount_type': 'fixed', 'discount_value': 100, 'min_purchase': 1000, 'max_uses': 200, 'valid_from': now, 'valid_to': now + timedelta(days=45)},
            {'code': 'MEGA50', 'description': 'Mega sale - 50% off on orders above ₹5000', 'discount_type': 'percentage', 'discount_value': 50, 'min_purchase': 5000, 'max_uses': 20, 'valid_from': now, 'valid_to': now + timedelta(days=7)},
            {'code': 'FREESHIP', 'description': 'Free shipping on all orders', 'discount_type': 'fixed', 'discount_value': 40, 'min_purchase': 0, 'max_uses': 0, 'valid_from': now, 'valid_to': now + timedelta(days=60)},
        ]
        
        for data in coupons_data:
            coupon, created = Coupon.objects.get_or_create(code=data['code'], defaults=data)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created coupon: {coupon.code}'))
            else:
                self.stdout.write(self.style.WARNING(f'Coupon already exists: {coupon.code}'))
        
        self.stdout.write(self.style.SUCCESS('Successfully populated coupons!'))

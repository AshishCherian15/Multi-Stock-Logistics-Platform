from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from categories.models import Category
from shipping.models import Carrier, ShippingRate
from credit.models import CreditProfile
from coupons.models import Coupon
from customer.models import ListModel as Customer
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting data population...')
        
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            self.stdout.write('No superuser found')
            return
        
        # Categories
        self.stdout.write('1. Categories...')
        cats = [
            {'name': 'Electronics', 'code': 'ELEC', 'category_type': 'product', 'icon': 'fa-laptop'},
            {'name': 'Fashion', 'code': 'FASH', 'category_type': 'product', 'icon': 'fa-tshirt'},
            {'name': 'Home & Garden', 'code': 'HOME', 'category_type': 'product', 'icon': 'fa-home'},
            {'name': 'Sports Equipment', 'code': 'SPRT', 'category_type': 'rental', 'icon': 'fa-basketball-ball'},
            {'name': 'Small Storage', 'code': 'STOR-S', 'category_type': 'storage', 'icon': 'fa-box'},
            {'name': 'Personal Locker', 'code': 'LOCK-P', 'category_type': 'locker', 'icon': 'fa-lock'},
            {'name': 'Office Supplies', 'code': 'OFFC', 'category_type': 'expense', 'icon': 'fa-pen'},
        ]
        for c in cats:
            Category.objects.get_or_create(code=c['code'], defaults={'name': c['name'], 'category_type': c['category_type'], 'icon': c['icon'], 'status': 'active', 'created_by': user})
        
        # Carriers
        self.stdout.write('2. Carriers...')
        carrs = [
            {'name': 'FedEx', 'code': 'FEDEX', 'contact_phone': '+1-800-463-3339'},
            {'name': 'DHL Express', 'code': 'DHL', 'contact_phone': '+1-800-225-5345'},
            {'name': 'Blue Dart', 'code': 'BLUEDART', 'contact_phone': '+91-1860-233-1234'},
        ]
        for c in carrs:
            Carrier.objects.get_or_create(code=c['code'], defaults={'name': c['name'], 'contact_phone': c['contact_phone'], 'is_active': True})
        
        # Rates
        self.stdout.write('3. Shipping Rates...')
        for carrier in Carrier.objects.all():
            ShippingRate.objects.get_or_create(carrier=carrier, service_type='Standard', defaults={'max_weight': 5, 'base_rate': 50, 'per_kg_rate': 10, 'estimated_days': 5, 'is_active': True})
            ShippingRate.objects.get_or_create(carrier=carrier, service_type='Express', defaults={'max_weight': 5, 'base_rate': 100, 'per_kg_rate': 20, 'estimated_days': 2, 'is_active': True})
        
        # Customers
        self.stdout.write('4. Customers...')
        custs = [
            {'name': 'Rajesh Kumar', 'contact': '+91-98765-43210', 'city': 'Mumbai'},
            {'name': 'Priya Sharma', 'contact': '+91-98765-43211', 'city': 'Delhi'},
            {'name': 'Amit Patel', 'contact': '+91-98765-43212', 'city': 'Bangalore'},
        ]
        for c in custs:
            Customer.objects.get_or_create(customer_name=c['name'], defaults={'customer_contact': c['contact'], 'customer_city': c['city'], 'customer_address': f"{c['city']}, India", 'customer_manager': user.username, 'openid': user.username})
        
        # Credits
        self.stdout.write('5. Credit Profiles...')
        for customer in Customer.objects.all()[:3]:
            CreditProfile.objects.get_or_create(customer=customer, defaults={'credit_limit': Decimal(100000), 'used_credit': Decimal(30000), 'available_credit': Decimal(70000), 'risk_level': 'low', 'is_active': True})
        
        # Coupons
        self.stdout.write('6. Coupons...')
        coups = [
            {'code': 'WELCOME10', 'desc': 'Welcome discount for new customers', 'type': 'percentage', 'value': 10, 'min': 500, 'max': 100},
            {'code': 'SAVE500', 'desc': 'Flat 500 off on orders above 5000', 'type': 'fixed', 'value': 500, 'min': 5000, 'max': 50},
            {'code': 'FESTIVE20', 'desc': 'Festival special - 20% off', 'type': 'percentage', 'value': 20, 'min': 1000, 'max': 200},
        ]
        for c in coups:
            Coupon.objects.get_or_create(code=c['code'], defaults={'description': c['desc'], 'discount_type': c['type'], 'discount_value': c['value'], 'min_purchase': c['min'], 'max_uses': c['max'], 'valid_from': timezone.now(), 'valid_to': timezone.now() + timedelta(days=90), 'is_active': True})
        
        self.stdout.write(self.style.SUCCESS('\nData populated successfully!'))
        self.stdout.write(f'Categories: {Category.objects.count()}')
        self.stdout.write(f'Carriers: {Carrier.objects.count()}')
        self.stdout.write(f'Shipping Rates: {ShippingRate.objects.count()}')
        self.stdout.write(f'Customers: {Customer.objects.count()}')
        self.stdout.write(f'Credit Profiles: {CreditProfile.objects.count()}')
        self.stdout.write(f'Coupons: {Coupon.objects.count()}')

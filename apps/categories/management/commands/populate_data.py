from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from categories.models import Category
from shipping.models import Carrier, ShippingRate, Shipment, TrackingEvent
from credit.models import CreditProfile, CreditTransaction
from coupons.models import Coupon
from customer.models import ListModel as Customer
from orders.models import Order
from datetime import datetime, timedelta
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting data population...')
        
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        
        # Categories
        self.stdout.write('\n1. Categories...')
        cats = [
            {'name': 'Electronics', 'code': 'ELEC', 'type': 'product', 'icon': 'fa-laptop'},
            {'name': 'Fashion', 'code': 'FASH', 'type': 'product', 'icon': 'fa-tshirt'},
            {'name': 'Home & Garden', 'code': 'HOME', 'type': 'product', 'icon': 'fa-home'},
            {'name': 'Sports', 'code': 'SPRT', 'type': 'rental', 'icon': 'fa-basketball-ball'},
            {'name': 'Small Storage', 'code': 'STOR-S', 'type': 'storage', 'icon': 'fa-box'},
            {'name': 'Personal Locker', 'code': 'LOCK-P', 'type': 'locker', 'icon': 'fa-lock'},
        ]
        for c in cats:
            Category.objects.get_or_create(code=c['code'], defaults={**c, 'status': 'active', 'created_by': user})
        
        # Carriers
        self.stdout.write('2. Carriers...')
        carrs = [
            {'name': 'FedEx', 'code': 'FEDEX', 'phone': '+1-800-463-3339'},
            {'name': 'DHL', 'code': 'DHL', 'phone': '+1-800-225-5345'},
            {'name': 'Blue Dart', 'code': 'BLUEDART', 'phone': '+91-1860-233-1234'},
        ]
        for c in carrs:
            Carrier.objects.get_or_create(code=c['code'], defaults={**c, 'is_active': True})
        
        # Rates
        self.stdout.write('3. Rates...')
        for carrier in Carrier.objects.all():
            ShippingRate.objects.get_or_create(carrier=carrier, service_type='Standard', defaults={'max_weight': 5, 'base_rate': 50, 'per_kg_rate': 10, 'estimated_days': 5, 'is_active': True})
        
        # Customers
        self.stdout.write('4. Customers...')
        custs = [
            {'name': 'Rajesh Kumar', 'email': 'rajesh@example.com', 'phone': '+91-98765-43210', 'city': 'Mumbai'},
            {'name': 'Priya Sharma', 'email': 'priya@example.com', 'phone': '+91-98765-43211', 'city': 'Delhi'},
            {'name': 'Amit Patel', 'email': 'amit@example.com', 'phone': '+91-98765-43212', 'city': 'Bangalore'},
        ]
        for c in custs:
            Customer.objects.get_or_create(customer_name=c['name'], defaults={'customer_email': c['email'], 'customer_phone': c['phone'], 'customer_city': c['city'], 'customer_address': f"{c['city']}, India", 'customer_status': 1, 'creater': user.username})
        
        # Credits
        self.stdout.write('5. Credits...')
        for customer in Customer.objects.all()[:3]:
            CreditProfile.objects.get_or_create(customer=customer, defaults={'credit_limit': Decimal(100000), 'used_credit': Decimal(30000), 'available_credit': Decimal(70000), 'risk_level': 'low', 'is_active': True})
        
        # Coupons
        self.stdout.write('6. Coupons...')
        coups = [
            {'code': 'WELCOME10', 'desc': 'Welcome discount', 'type': 'percentage', 'value': 10, 'min': 500, 'max': 100},
            {'code': 'SAVE500', 'desc': 'Flat ₹500 off', 'type': 'fixed', 'value': 500, 'min': 5000, 'max': 50},
        ]
        for c in coups:
            Coupon.objects.get_or_create(code=c['code'], defaults={'description': c['desc'], 'discount_type': c['type'], 'discount_value': c['value'], 'min_purchase': c['min'], 'max_uses': c['max'], 'valid_from': datetime.now().date(), 'valid_to': (datetime.now() + timedelta(days=90)).date(), 'is_active': True, 'created_by': user})
        
        # Orders
        self.stdout.write('7. Orders...')
        for i, customer in enumerate(Customer.objects.all()[:3]):
            Order.objects.get_or_create(order_number=f'ORD-{1000+i}', defaults={'customer': customer, 'customer_name': customer.customer_name, 'customer_email': customer.customer_email, 'customer_phone': customer.customer_phone, 'shipping_address': customer.customer_address, 'total_amount': Decimal(10000), 'status': 'completed', 'payment_status': 'paid', 'created_by': user})
        
        # Shipments
        self.stdout.write('8. Shipments...')
        for i, order in enumerate(Order.objects.all()[:3]):
            carrier = Carrier.objects.first()
            Shipment.objects.get_or_create(shipment_number=f'SHIP-{2000+i}', defaults={'order': order, 'carrier': carrier, 'tracking_number': f'{carrier.code}-{100000+i}', 'service_type': 'Standard', 'status': 'delivered', 'sender_name': 'MultiStock', 'sender_address': 'Mumbai', 'sender_city': 'Mumbai', 'sender_phone': '+91-22-1234-5678', 'recipient_name': order.customer_name, 'recipient_address': order.shipping_address, 'recipient_city': order.customer.customer_city, 'recipient_phone': order.customer_phone, 'weight': Decimal(5), 'package_count': 1, 'shipping_cost': Decimal(200), 'total_cost': Decimal(200), 'created_by': user})
        
        self.stdout.write(self.style.SUCCESS('\n✓ Data populated successfully!'))
        self.stdout.write(f'Categories: {Category.objects.count()}')
        self.stdout.write(f'Carriers: {Carrier.objects.count()}')
        self.stdout.write(f'Customers: {Customer.objects.count()}')
        self.stdout.write(f'Credits: {CreditProfile.objects.count()}')
        self.stdout.write(f'Coupons: {Coupon.objects.count()}')
        self.stdout.write(f'Orders: {Order.objects.count()}')
        self.stdout.write(f'Shipments: {Shipment.objects.count()}')

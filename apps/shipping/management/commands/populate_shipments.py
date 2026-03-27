from django.core.management.base import BaseCommand
from shipping.models import Shipment, Carrier, TrackingEvent
from orders.models import Order
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Populate shipments with sample data'

    def handle(self, *args, **kwargs):
        carriers = Carrier.objects.all()
        if not carriers.exists():
            self.stdout.write('No carriers found')
            return

        orders = Order.objects.filter(status='confirmed')[:20]
        
        statuses = ['pending', 'in_transit', 'delivered', 'returned']
        
        for i, order in enumerate(orders):
            if not Shipment.objects.filter(order=order).exists():
                carrier = random.choice(carriers)
                status = random.choice(statuses)
                
                shipment = Shipment.objects.create(
                    order=order,
                    carrier=carrier,
                    shipment_number=f'SHP{timezone.now().strftime("%Y%m%d")}{1000+i}',
                    tracking_number=f'TRK{random.randint(100000, 999999)}',
                    service_type='Standard',
                    status=status,
                    sender_name='MultiStock Warehouse',
                    sender_address='123 Warehouse St',
                    sender_city='Mumbai',
                    sender_phone='+91 9876543210',
                    recipient_name=f'Customer {order.id}',
                    recipient_address=order.delivery_address if hasattr(order, 'delivery_address') else 'Customer Address',
                    recipient_city='Delhi',
                    recipient_phone='+91 9999999999',
                    weight=random.uniform(1, 10),
                    shipping_cost=random.uniform(50, 500),
                    total_cost=random.uniform(50, 500),
                    pickup_date=(timezone.now() - timedelta(days=random.randint(1, 10))).date(),
                    estimated_delivery=(timezone.now() + timedelta(days=random.randint(1, 5))).date()
                )
                
                TrackingEvent.objects.create(
                    shipment=shipment,
                    status='picked_up',
                    location='Warehouse',
                    description='Package picked up from warehouse',
                    event_time=timezone.now() - timedelta(days=random.randint(1, 5))
                )
                
                if status in ['in_transit', 'delivered']:
                    TrackingEvent.objects.create(
                        shipment=shipment,
                        status='in_transit',
                        location='Transit Hub',
                        description='Package in transit',
                        event_time=timezone.now() - timedelta(days=random.randint(0, 3))
                    )
                
                if status == 'delivered':
                    TrackingEvent.objects.create(
                        shipment=shipment,
                        status='delivered',
                        location='Customer Address',
                        description='Package delivered successfully',
                        event_time=timezone.now()
                    )
        
        self.stdout.write(self.style.SUCCESS(f'Created shipments for {orders.count()} orders'))

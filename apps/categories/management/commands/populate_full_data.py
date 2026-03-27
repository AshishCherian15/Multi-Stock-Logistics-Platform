from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from customer.models import ListModel as Customer
from orders.models import Order
from billing.models import Invoice, InvoiceItem
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Populate historical data from August'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating historical data...')
        
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            self.stdout.write('No superuser found')
            return
        
        customers = list(Customer.objects.all())
        if not customers:
            self.stdout.write('No customers. Run populate_all first.')
            return
        
        self.stdout.write(f'Found {len(customers)} customers')
        self.stdout.write('Creating orders (Aug-Dec 2024)...')
        
        # Create orders in bulk
        orders_to_create = []
        start_date = datetime(2024, 8, 1, tzinfo=timezone.get_current_timezone())
        end_date = timezone.now()
        current_date = start_date
        order_num = 1000
        
        while current_date <= end_date:
            for _ in range(random.randint(3, 6)):
                customer = random.choice(customers)
                order_time = current_date.replace(hour=random.randint(9, 20), minute=random.randint(0, 59))
                amount = Decimal(random.randint(5000, 150000))
                
                order = Order(
                    order_number=f'ORD-{order_num}',
                    order_type='sale',
                    customer=customer,
                    delivery_address=customer.customer_address,
                    delivery_phone=customer.customer_contact,
                    total_amount=amount,
                    grand_total=amount + Decimal('40'),
                    status=random.choice(['delivered', 'delivered', 'delivered', 'processing']),
                    payment_status=random.choice(['paid', 'paid', 'paid', 'unpaid']),
                    openid=user.username,
                    created_by=user,
                    created_at=order_time,
                    updated_at=order_time
                )
                orders_to_create.append(order)
                order_num += 1
            
            current_date += timedelta(days=1)
        
        # Bulk create orders (bypasses signals)
        Order.objects.bulk_create(orders_to_create, ignore_conflicts=True)
        self.stdout.write(f'Created {len(orders_to_create)} orders')
        
        # Create invoices
        self.stdout.write('Creating invoices...')
        delivered_orders = Order.objects.filter(status='delivered', payment_status='paid')[:200]
        invoices_to_create = []
        invoice_num = 2000
        
        for order in delivered_orders:
            invoice = Invoice(
                invoice_number=f'INV-{invoice_num}',
                invoice_type='sales',
                customer_name=order.customer.customer_name,
                customer_email=f'{order.customer.customer_name.lower().replace(" ", "")}@example.com',
                customer_phone=order.delivery_phone,
                customer_address=order.delivery_address,
                invoice_date=order.created_at.date(),
                due_date=(order.created_at + timedelta(days=30)).date(),
                subtotal=order.total_amount,
                tax_rate=Decimal('18'),
                tax_amount=order.total_amount * Decimal('0.18'),
                discount_amount=Decimal('0'),
                grand_total=order.total_amount * Decimal('1.18'),
                status='paid',
                payment_method=random.choice(['bank_transfer', 'card', 'upi', 'cash']),
                created_by=user,
                created_at=order.created_at,
                updated_at=order.created_at
            )
            invoices_to_create.append(invoice)
            invoice_num += 1
        
        Invoice.objects.bulk_create(invoices_to_create, ignore_conflicts=True)
        self.stdout.write(f'Created {len(invoices_to_create)} invoices')
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('DATA POPULATION COMPLETED!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'\nFinal Summary:')
        self.stdout.write(f'  Total Orders: {Order.objects.count()}')
        self.stdout.write(f'  Total Invoices: {Invoice.objects.count()}')
        self.stdout.write(f'  Delivered Orders: {Order.objects.filter(status="delivered").count()}')
        self.stdout.write(f'  Paid Invoices: {Invoice.objects.filter(status="paid").count()}')
        
        from django.db.models import Sum
        total_revenue = Invoice.objects.filter(status='paid').aggregate(total=Sum('grand_total'))['total'] or 0
        self.stdout.write(f'  Total Revenue: Rs. {total_revenue}')
        self.stdout.write(self.style.SUCCESS('\nAnalytics page now shows historical data from August!'))

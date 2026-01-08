from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from orders.models import Order
from stock.models import StockMovement
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed sample data for dashboard charts'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding chart data...')
        
        user = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('❌ No users found'))
            return
        
        now = timezone.now()
        
        # Orders
        self.stdout.write('📦 Creating orders...')
        for i in range(30):
            order_num = f'ORD-{10000 + i}'
            if not Order.objects.filter(order_number=order_num).exists():
                Order.objects.create(
                    order_number=order_num,
                    order_type='sale',
                    total_amount=Decimal(str(500 + (i * 100))),
                    status='delivered',
                    payment_status='paid',
                    created_by=user,
                    created_at=now - timedelta(days=i * 3)
                )
        
        # Stock movements
        self.stdout.write('📊 Creating stock movements...')
        for i in range(40):
            created = now - timedelta(days=i * 2)
            goods_code = f'PROD-{100 + i}'
            if not StockMovement.objects.filter(goods_code=goods_code, movement_type='in', created_at=created).exists():
                StockMovement.objects.create(
                    goods_code=goods_code,
                    movement_type='in',
                    quantity=50 + (i * 5),
                    reason='Purchase',
                    user=user,
                    created_at=created
                )
            if not StockMovement.objects.filter(goods_code=goods_code, movement_type='out', created_at=created).exists():
                StockMovement.objects.create(
                    goods_code=goods_code,
                    movement_type='out',
                    quantity=30 + (i * 3),
                    reason='Sale',
                    user=user,
                    created_at=created
                )
        
        self.stdout.write(self.style.SUCCESS('✅ Chart data seeded!'))

from django.core.management.base import BaseCommand
from stock.models import StockMovement, StockListModel
from goods.models import ListModel as Product
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Populate stock movements with realistic data'

    def handle(self, *args, **kwargs):
        # Get products and user
        products = list(Product.objects.filter(is_delete=False)[:20])
        user = User.objects.filter(is_superuser=True).first()
        
        if not products:
            self.stdout.write(self.style.ERROR('No products found'))
            return
        
        if not user:
            self.stdout.write(self.style.ERROR('No superuser found'))
            return

        movement_types = [
            ('Stock In', 'Purchase'),
            ('Stock In', 'Return from Customer'),
            ('Stock Out', 'Sale'),
            ('Stock Out', 'Damage'),
            ('Adjustment', 'Inventory Correction'),
            ('Transfer', 'Warehouse Transfer')
        ]

        created_count = 0
        
        # Create movements for last 30 days
        for i in range(50):
            product = random.choice(products)
            movement_type, reason = random.choice(movement_types)
            quantity = random.randint(1, 50)
            
            # Adjust quantity sign based on type
            if 'Out' in movement_type or 'Transfer' in movement_type:
                quantity = -quantity
            
            # Random date in last 30 days
            days_ago = random.randint(0, 30)
            created_at = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
            
            movement = StockMovement.objects.create(
                goods_code=product.goods_code,
                movement_type=movement_type,
                quantity=quantity,
                reason=reason,
                user=user,
                created_at=created_at
            )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} stock movements'))

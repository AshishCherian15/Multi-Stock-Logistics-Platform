from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from goods.models import ListModel as Product
from stock.models import StockListModel
from warehouse.models import ListModel as Warehouse
from supplier.models import ListModel as Supplier
from customer.models import ListModel as Customer
from orders.models import Order, OrderItem
from django.conf import settings
from decimal import Decimal
import random
from pathlib import Path


class Command(BaseCommand):
    help = 'Bootstrap a fresh database with core sample data (warehouse, suppliers, customers, products, stock).'

    def handle(self, *args, **options):
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@multistock.com',
                password='admin123',
            )
            self.stdout.write(self.style.WARNING('Created default superuser: admin / admin123'))

        Warehouse.objects.get_or_create(
            warehouse_name='Main Warehouse',
            defaults={
                'warehouse_city': 'Lagos',
                'warehouse_address': '1 Logistics Avenue',
                'warehouse_contact': '+2340000000',
                'warehouse_manager': 'Warehouse Manager',
                'creater': admin_user.username,
            },
        )

        suppliers = [
            ('Apple Distribution', 'Lagos'),
            ('Samsung Trade Hub', 'Abuja'),
            ('Home Essentials Ltd', 'Port Harcourt'),
            ('Athletic Pro Supply', 'Ibadan'),
            ('Smart Home Imports', 'Enugu'),
        ]
        for name, city in suppliers:
            Supplier.objects.get_or_create(
                supplier_name=name,
                defaults={
                    'supplier_city': city,
                    'supplier_address': f'{city} Business District',
                    'supplier_contact': '+2340000000',
                    'supplier_manager': 'Supplier Manager',
                    'supplier_level': 1,
                    'openid': 'system',
                },
            )

        customers = [
            ('Prime Retail', 'Lagos'),
            ('City Market', 'Abuja'),
            ('HomePro Stores', 'Kano'),
            ('Mega Mart', 'Port Harcourt'),
            ('Urban Commerce', 'Lagos'),
        ]
        for name, city in customers:
            Customer.objects.get_or_create(
                customer_name=name,
                defaults={
                    'customer_city': city,
                    'customer_address': f'{city} Central',
                    'customer_contact': '+2340000000',
                    'customer_manager': 'Sales Manager',
                    'customer_level': 1,
                    'openid': 'system',
                },
            )

        products = [
            ('PRD-1001', 'iPhone 15 Pro', 'Apple Distribution', 980.0, 1299.0, 'Electronics', 'Apple', 'iPhone_15_Pro_Max.webp'),
            ('PRD-1002', 'Samsung Galaxy S24', 'Samsung Trade Hub', 850.0, 1199.0, 'Electronics', 'Samsung', 'Samsung_Galaxy_S24_Ultra.jpg'),
            ('PRD-1003', 'MacBook Pro M3', 'Apple Distribution', 1450.0, 1899.0, 'Electronics', 'Apple', 'MacBook_Pro_M3.webp'),
            ('PRD-1004', 'Dell XPS 15', 'Home Essentials Ltd', 1100.0, 1549.0, 'Electronics', 'Dell', 'Dell_XPS_15.jpg'),
            ('PRD-1005', 'Wireless Earbuds', 'Smart Home Imports', 45.0, 89.0, 'Accessories', 'SoundCore', 'Wireless_Earbuds.webp'),
            ('PRD-1006', 'Bluetooth Speaker', 'Smart Home Imports', 55.0, 99.0, 'Accessories', 'JBL', 'Bluetooth_Speaker.webp'),
            ('PRD-1007', 'Running Shoes', 'Athletic Pro Supply', 38.0, 79.0, 'Sports', 'Kalenji', 'Running_Shoes.webp'),
            ('PRD-1008', 'Smartwatch Pro', 'Smart Home Imports', 120.0, 219.0, 'Wearables', 'FitPro', 'Smartwatch_Pro.webp'),
            ('PRD-1009', 'Cordless Drill', 'Home Essentials Ltd', 68.0, 129.0, 'Tools', 'Bosch', 'Cordless_Drill.webp'),
            ('PRD-1010', 'Laser Measure', 'Home Essentials Ltd', 28.0, 59.0, 'Tools', 'Bosch', 'Laser_Measure.webp'),
        ]

        stock_images_path = Path(settings.MEDIA_ROOT) / 'stock_images'

        for code, desc, supplier, cost, price, klass, brand, image_name in products:
            product, _ = Product.objects.get_or_create(
                goods_code=code,
                defaults={
                    'goods_desc': desc,
                    'goods_supplier': supplier,
                    'goods_weight': 1.0,
                    'goods_w': 10.0,
                    'goods_d': 10.0,
                    'goods_h': 10.0,
                    'goods_unit': 'pcs',
                    'goods_class': klass,
                    'goods_brand': brand,
                    'safety_stock': 10,
                    'goods_cost': cost,
                    'goods_price': price,
                    'bar_code': '',
                    'min_stock_level': 10,
                    'reorder_point': 15,
                    'openid': 'system',
                    'created_by': admin_user,
                },
            )

            stock, _ = StockListModel.objects.get_or_create(
                goods_code=product.goods_code,
                defaults={
                    'goods_desc': product.goods_desc,
                    'onhand_stock': random.randint(60, 220),
                    'ordered_stock': 0,
                    'damage_stock': random.randint(0, 5),
                    'supplier': product.goods_supplier,
                    'openid': 'system',
                },
            )

            image_file = stock_images_path / image_name
            if image_file.exists() and not stock.goods_image:
                stock.goods_image.name = f'stock_images/{image_name}'
                stock.save(update_fields=['goods_image', 'update_time'])

        self.create_sample_orders(admin_user)

        self.stdout.write(self.style.SUCCESS('Fresh database bootstrap complete.'))
        self.stdout.write(self.style.SUCCESS(f'Products: {Product.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Stock rows: {StockListModel.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Orders: {Order.objects.count()}'))

    def create_sample_orders(self, admin_user):
        customers = list(Customer.objects.all()[:5])
        suppliers = list(Supplier.objects.all()[:5])
        products = list(Product.objects.all())

        if not customers or not suppliers or not products:
            return

        for order_index in range(1, 13):
            customer = random.choice(customers)
            supplier = random.choice(suppliers)
            order, created = Order.objects.get_or_create(
                order_number=f'ORD-2026-{order_index:04d}',
                defaults={
                    'order_type': 'sale',
                    'customer': customer,
                    'supplier': supplier,
                    'status': random.choice(['pending', 'confirmed', 'processing', 'shipped', 'delivered']),
                    'payment_status': random.choice(['unpaid', 'paid']),
                    'total_amount': Decimal('0.00'),
                    'discount_amount': Decimal('0.00'),
                    'delivery_fee': Decimal('40.00'),
                    'delivery_address': customer.customer_address,
                    'delivery_phone': customer.customer_contact,
                    'payment_method': random.choice(['cash', 'card', 'bank_transfer']),
                    'assigned_to': admin_user,
                    'openid': 'system',
                    'created_by': admin_user,
                },
            )

            if not created:
                continue

            selected_products = random.sample(products, k=min(3, len(products)))
            total = Decimal('0.00')
            for product in selected_products:
                quantity = random.randint(1, 4)
                unit_price = Decimal(str(round(product.goods_price, 2)))
                line_total = unit_price * quantity
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.goods_desc,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=line_total,
                    seller=product.goods_supplier,
                )
                total += line_total

            order.total_amount = total
            order.save(update_fields=['total_amount', 'grand_total', 'updated_at'])

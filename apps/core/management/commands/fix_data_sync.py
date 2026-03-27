"""
Django Management Command to Fix Data Synchronization Issues
Usage: python manage.py fix_data_sync --check  (to check only)
       python manage.py fix_data_sync --fix    (to fix issues)
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count, Sum, Q
from goods.models import ListModel as Product
from warehouse.models import ListModel as Warehouse
from stock.models import StockListModel as Stock
from orders.models import Order, OrderItem
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Fix data synchronization issues across the platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check',
            action='store_true',
            help='Check for issues without fixing',
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Fix identified issues',
        )

    def handle(self, *args, **options):
        check_only = options['check']
        fix_issues = options['fix']

        if not check_only and not fix_issues:
            self.stdout.write(self.style.ERROR('Please specify --check or --fix'))
            return

        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('DATA SYNCHRONIZATION AUDIT'))
        self.stdout.write(self.style.SUCCESS('=' * 80))

        issues_found = 0

        # Issue 1: Product Count Mismatch
        issues_found += self.check_product_count()

        # Issue 2: Warehouse Count Mismatch
        issues_found += self.check_warehouse_count()

        # Issue 3: Stock Quantity Inconsistencies
        issues_found += self.check_stock_quantities(fix_issues)

        # Issue 4: Negative Stock
        issues_found += self.check_negative_stock(fix_issues)

        # Issue 5: Products Without Stock
        issues_found += self.check_products_without_stock(fix_issues)

        # Issue 6: Orphaned Stock Records
        issues_found += self.check_orphaned_stock()

        # Issue 7: Duplicate Goods Codes
        issues_found += self.check_duplicate_goods_codes()

        # Issue 8: Duplicate Stock Records
        issues_found += self.check_duplicate_stock_records(fix_issues)

        # Issue 9: Orders Without Items
        issues_found += self.check_orders_without_items()

        # Issue 10: Order Total Mismatch
        issues_found += self.check_order_totals(fix_issues)

        # Summary
        self.stdout.write(self.style.SUCCESS('=' * 80))
        if issues_found == 0:
            self.stdout.write(self.style.SUCCESS('✓ No issues found! Data is synchronized.'))
        else:
            self.stdout.write(self.style.WARNING(f'✗ Found {issues_found} issues'))
            if check_only:
                self.stdout.write(self.style.WARNING('Run with --fix to fix these issues'))
        self.stdout.write(self.style.SUCCESS('=' * 80))

    def check_product_count(self):
        total = Product.objects.count()
        active = Product.objects.filter(is_delete=False).count()
        deleted = Product.objects.filter(is_delete=True).count()

        self.stdout.write('\n1. PRODUCT COUNT CHECK')
        self.stdout.write(f'   Total Products: {total}')
        self.stdout.write(f'   Active Products: {active}')
        self.stdout.write(f'   Deleted Products: {deleted}')

        if deleted > 0:
            self.stdout.write(self.style.WARNING(f'   ⚠ {deleted} soft-deleted products found'))
            self.stdout.write(self.style.WARNING('   → Dashboard should use .filter(is_delete=False).count()'))
            return 1
        else:
            self.stdout.write(self.style.SUCCESS('   ✓ No issues'))
            return 0

    def check_warehouse_count(self):
        total = Warehouse.objects.count()
        active = Warehouse.objects.filter(is_delete=False).count()
        deleted = Warehouse.objects.filter(is_delete=True).count()

        self.stdout.write('\n2. WAREHOUSE COUNT CHECK')
        self.stdout.write(f'   Total Warehouses: {total}')
        self.stdout.write(f'   Active Warehouses: {active}')
        self.stdout.write(f'   Deleted Warehouses: {deleted}')

        if deleted > 0:
            self.stdout.write(self.style.WARNING(f'   ⚠ {deleted} soft-deleted warehouses found'))
            self.stdout.write(self.style.WARNING('   → All queries should use .filter(is_delete=False)'))
            return 1
        else:
            self.stdout.write(self.style.SUCCESS('   ✓ No issues'))
            return 0

    def check_stock_quantities(self, fix=False):
        inconsistent = Stock.objects.exclude(
            can_order_stock=Q(onhand_stock=0) | Q(onhand_stock__gt=0)
        ).filter(
            can_order_stock__gt=Q(onhand_stock=0)
        )

        # Better check: can_order_stock should = onhand_stock - ordered_stock - damage_stock
        issues = []
        for stock in Stock.objects.all():
            expected = max(0, stock.onhand_stock - stock.ordered_stock - stock.damage_stock)
            if stock.can_order_stock != expected:
                issues.append((stock, expected))

        self.stdout.write('\n3. STOCK QUANTITY CONSISTENCY CHECK')
        self.stdout.write(f'   Total Stock Records: {Stock.objects.count()}')
        self.stdout.write(f'   Inconsistent Records: {len(issues)}')

        if issues:
            self.stdout.write(self.style.WARNING(f'   ⚠ {len(issues)} stock records have inconsistent quantities'))
            for stock, expected in issues[:5]:  # Show first 5
                self.stdout.write(f'      {stock.goods_code}: can_order={stock.can_order_stock}, expected={expected}')

            if fix:
                with transaction.atomic():
                    for stock, expected in issues:
                        stock.can_order_stock = expected
                        stock.goods_qty = stock.onhand_stock
                        stock.save(update_fields=['can_order_stock', 'goods_qty'])
                self.stdout.write(self.style.SUCCESS(f'   ✓ Fixed {len(issues)} records'))
            return len(issues)
        else:
            self.stdout.write(self.style.SUCCESS('   ✓ No issues'))
            return 0

    def check_negative_stock(self, fix=False):
        negative = Stock.objects.filter(
            Q(goods_qty__lt=0) | Q(onhand_stock__lt=0) | Q(can_order_stock__lt=0)
        )

        self.stdout.write('\n4. NEGATIVE STOCK CHECK')
        self.stdout.write(f'   Records with negative stock: {negative.count()}')

        if negative.exists():
            self.stdout.write(self.style.ERROR(f'   ✗ {negative.count()} records have negative stock!'))
            for stock in negative[:5]:
                self.stdout.write(f'      {stock.goods_code}: qty={stock.goods_qty}, onhand={stock.onhand_stock}, available={stock.can_order_stock}')

            if fix:
                with transaction.atomic():
                    for stock in negative:
                        stock.goods_qty = max(0, stock.goods_qty)
                        stock.onhand_stock = max(0, stock.onhand_stock)
                        stock.can_order_stock = max(0, stock.can_order_stock)
                        stock.save()
                self.stdout.write(self.style.SUCCESS(f'   ✓ Fixed {negative.count()} records'))
            return negative.count()
        else:
            self.stdout.write(self.style.SUCCESS('   ✓ No issues'))
            return 0

    def check_products_without_stock(self, fix=False):
        products_without_stock = Product.objects.filter(
            is_delete=False
        ).exclude(
            goods_code__in=Stock.objects.values_list('goods_code', flat=True)
        )

        self.stdout.write('\n5. PRODUCTS WITHOUT STOCK RECORDS')
        self.stdout.write(f'   Products without stock: {products_without_stock.count()}')

        if products_without_stock.exists():
            self.stdout.write(self.style.WARNING(f'   ⚠ {products_without_stock.count()} products have no stock records'))
            for product in products_without_stock[:5]:
                self.stdout.write(f'      {product.goods_code}: {product.goods_desc}')

            if fix:
                with transaction.atomic():
                    for product in products_without_stock:
                        Stock.objects.create(
                            goods_code=product.goods_code,
                            goods_desc=product.goods_desc,
                            goods_qty=0,
                            onhand_stock=0,
                            can_order_stock=0,
                            ordered_stock=0,
                            damage_stock=0,
                            supplier=product.goods_supplier,
                            openid=product.openid
                        )
                self.stdout.write(self.style.SUCCESS(f'   ✓ Created {products_without_stock.count()} stock records'))
            return products_without_stock.count()
        else:
            self.stdout.write(self.style.SUCCESS('   ✓ No issues'))
            return 0

    def check_orphaned_stock(self):
        orphaned = Stock.objects.exclude(
            goods_code__in=Product.objects.filter(is_delete=False).values_list('goods_code', flat=True)
        )

        self.stdout.write('\n6. ORPHANED STOCK RECORDS')
        self.stdout.write(f'   Orphaned stock records: {orphaned.count()}')

        if orphaned.exists():
            self.stdout.write(self.style.WARNING(f'   ⚠ {orphaned.count()} stock records have no matching product'))
            for stock in orphaned[:5]:
                self.stdout.write(f'      {stock.goods_code}: {stock.goods_desc}')
            self.stdout.write(self.style.WARNING('   → Consider deleting or linking to products'))
            return orphaned.count()
        else:
            self.stdout.write(self.style.SUCCESS('   ✓ No issues'))
            return 0

    def check_duplicate_goods_codes(self):
        duplicates = Product.objects.filter(
            is_delete=False
        ).values('goods_code').annotate(
            count=Count('id')
        ).filter(count__gt=1)

        self.stdout.write('\n7. DUPLICATE GOODS CODES')
        self.stdout.write(f'   Duplicate goods codes: {duplicates.count()}')

        if duplicates.exists():
            self.stdout.write(self.style.ERROR(f'   ✗ {duplicates.count()} goods codes are duplicated!'))
            for dup in duplicates[:5]:
                self.stdout.write(f'      {dup["goods_code"]}: {dup["count"]} occurrences')
            self.stdout.write(self.style.ERROR('   → Manual intervention required'))
            return duplicates.count()
        else:
            self.stdout.write(self.style.SUCCESS('   ✓ No issues'))
            return 0

    def check_duplicate_stock_records(self, fix=False):
        duplicates = Stock.objects.values('goods_code').annotate(
            count=Count('id')
        ).filter(count__gt=1)

        self.stdout.write('\n8. DUPLICATE STOCK RECORDS')
        self.stdout.write(f'   Duplicate stock records: {duplicates.count()}')

        if duplicates.exists():
            self.stdout.write(self.style.ERROR(f'   ✗ {duplicates.count()} goods codes have multiple stock records!'))
            for dup in duplicates[:5]:
                self.stdout.write(f'      {dup["goods_code"]}: {dup["count"]} records')

            if fix:
                self.stdout.write(self.style.WARNING('   → Merging duplicates (keeping first, summing quantities)'))
                with transaction.atomic():
                    for dup in duplicates:
                        stocks = Stock.objects.filter(goods_code=dup['goods_code']).order_by('id')
                        first = stocks.first()
                        others = stocks.exclude(id=first.id)

                        # Sum quantities
                        first.goods_qty += sum(s.goods_qty for s in others)
                        first.onhand_stock += sum(s.onhand_stock for s in others)
                        first.can_order_stock += sum(s.can_order_stock for s in others)
                        first.ordered_stock += sum(s.ordered_stock for s in others)
                        first.damage_stock += sum(s.damage_stock for s in others)
                        first.save()

                        # Delete duplicates
                        others.delete()
                self.stdout.write(self.style.SUCCESS(f'   ✓ Merged {duplicates.count()} duplicate records'))
            return duplicates.count()
        else:
            self.stdout.write(self.style.SUCCESS('   ✓ No issues'))
            return 0

    def check_orders_without_items(self):
        orders_without_items = Order.objects.annotate(
            item_count=Count('items')
        ).filter(item_count=0)

        self.stdout.write('\n9. ORDERS WITHOUT ITEMS')
        self.stdout.write(f'   Orders without items: {orders_without_items.count()}')

        if orders_without_items.exists():
            self.stdout.write(self.style.WARNING(f'   ⚠ {orders_without_items.count()} orders have no items'))
            for order in orders_without_items[:5]:
                self.stdout.write(f'      {order.order_number}: {order.status}')
            self.stdout.write(self.style.WARNING('   → Consider cancelling these orders'))
            return orders_without_items.count()
        else:
            self.stdout.write(self.style.SUCCESS('   ✓ No issues'))
            return 0

    def check_order_totals(self, fix=False):
        issues = []
        for order in Order.objects.all():
            items_total = order.items.aggregate(total=Sum('total_price'))['total'] or 0
            if abs(order.total_amount - items_total) > 0.01:
                issues.append((order, items_total))

        self.stdout.write('\n10. ORDER TOTAL MISMATCH')
        self.stdout.write(f'   Orders with total mismatch: {len(issues)}')

        if issues:
            self.stdout.write(self.style.WARNING(f'   ⚠ {len(issues)} orders have incorrect totals'))
            for order, items_total in issues[:5]:
                self.stdout.write(f'      {order.order_number}: order_total={order.total_amount}, items_total={items_total}')

            if fix:
                with transaction.atomic():
                    for order, items_total in issues:
                        order.total_amount = items_total
                        order.grand_total = items_total + order.delivery_fee - order.discount_amount
                        order.save(update_fields=['total_amount', 'grand_total'])
                self.stdout.write(self.style.SUCCESS(f'   ✓ Fixed {len(issues)} orders'))
            return len(issues)
        else:
            self.stdout.write(self.style.SUCCESS('   ✓ No issues'))
            return 0

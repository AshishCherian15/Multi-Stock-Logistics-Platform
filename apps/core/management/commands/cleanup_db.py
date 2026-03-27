from django.core.management.base import BaseCommand
from django.db.models import Count
from datetime import datetime, timedelta

class Command(BaseCommand):
	help = 'Clean up and organize database'

	def add_arguments(self, parser):
		parser.add_argument('--full', action='store_true', help='Run full cleanup')
		parser.add_argument('--orphaned', action='store_true', help='Remove orphaned records')
		parser.add_argument('--duplicates', action='store_true', help='Remove duplicates')
		parser.add_argument('--inactive', action='store_true', help='Remove inactive data')

	def handle(self, *args, **options):
		self.stdout.write(self.style.SUCCESS('=' * 60))
		self.stdout.write(self.style.SUCCESS('DATABASE CLEANUP'))
		self.stdout.write(self.style.SUCCESS('=' * 60))

		if options['full'] or options['orphaned']:
			self.cleanup_orphaned()

		if options['full'] or options['duplicates']:
			self.cleanup_duplicates()

		if options['full'] or options['inactive']:
			self.cleanup_inactive()

		self.stdout.write(self.style.SUCCESS('\n✓ Cleanup completed!'))

	def cleanup_orphaned(self):
		self.stdout.write('\n[1] Removing Orphaned Records...')
		
		try:
			from orders.models import OrderItem
			orphaned = OrderItem.objects.filter(order__isnull=True)
			count = orphaned.count()
			orphaned.delete()
			self.stdout.write(f'   ✓ Deleted {count} orphaned OrderItems')
		except Exception as e:
			self.stdout.write(f'   ⚠ OrderItem cleanup skipped: {str(e)}')

		try:
			from messaging.models import Message
			orphaned = Message.objects.filter(conversation__isnull=True)
			count = orphaned.count()
			orphaned.delete()
			self.stdout.write(f'   ✓ Deleted {count} orphaned Messages')
		except Exception as e:
			self.stdout.write(f'   ⚠ Message cleanup skipped: {str(e)}')

		try:
			from notifications.models import Notification
			orphaned = Notification.objects.filter(user__isnull=True)
			count = orphaned.count()
			orphaned.delete()
			self.stdout.write(f'   ✓ Deleted {count} orphaned Notifications')
		except Exception as e:
			self.stdout.write(f'   ⚠ Notification cleanup skipped: {str(e)}')

	def cleanup_duplicates(self):
		self.stdout.write('\n[2] Removing Duplicates...')
		
		try:
			from products.models import Product
			products = Product.objects.values('name').annotate(count=Count('id')).filter(count__gt=1)
			dup_count = 0
			for product in products:
				dupes = Product.objects.filter(name=product['name']).order_by('id')[1:]
				dup_count += dupes.count()
				dupes.delete()
			self.stdout.write(f'   ✓ Deleted {dup_count} duplicate Products')
		except Exception as e:
			self.stdout.write(f'   ⚠ Product duplicate cleanup skipped: {str(e)}')

	def cleanup_inactive(self):
		self.stdout.write('\n[3] Cleaning Inactive Data...')
		
		old_date = datetime.now() - timedelta(days=365)
		
		try:
			from orders.models import Order
			old_orders = Order.objects.filter(status='cancelled', created_at__lt=old_date)
			count = old_orders.count()
			old_orders.delete()
			self.stdout.write(f'   ✓ Deleted {count} old cancelled Orders')
		except Exception as e:
			self.stdout.write(f'   ⚠ Order cleanup skipped: {str(e)}')

		try:
			from notifications.models import Notification
			old_notif = Notification.objects.filter(created_at__lt=old_date, is_read=True)
			count = old_notif.count()
			old_notif.delete()
			self.stdout.write(f'   ✓ Deleted {count} old Notifications')
		except Exception as e:
			self.stdout.write(f'   ⚠ Notification cleanup skipped: {str(e)}')

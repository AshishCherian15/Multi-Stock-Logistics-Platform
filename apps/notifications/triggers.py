from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from orders.models import Order
from stock.models import StockListModel
from .models import Notification

@receiver(post_save, sender=Order)
def order_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.created_by,
            title='New Order Created',
            message=f'Order {instance.order_number} has been created successfully.',
            type='info',
            category='order'
        )
    elif instance.status == 'delivered':
        Notification.objects.create(
            user=instance.created_by,
            title='Order Delivered',
            message=f'Order {instance.order_number} has been delivered.',
            type='success',
            category='order'
        )

@receiver(pre_save, sender=StockListModel)
def low_stock_notification(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = StockListModel.objects.get(pk=instance.pk)
            if old_instance.goods_qty > 10 and instance.goods_qty <= 10:
                from django.contrib.auth.models import User
                admins = User.objects.filter(is_staff=True)
                for admin in admins:
                    Notification.objects.create(
                        user=admin,
                        title='Low Stock Alert',
                        message=f'Product {instance.goods_code} is running low (Qty: {instance.goods_qty})',
                        type='warning',
                        category='stock'
                    )
        except StockListModel.DoesNotExist:
            pass

def send_custom_notification(user, title, message, notification_type='info'):
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        type=notification_type,
        category='system'
    )

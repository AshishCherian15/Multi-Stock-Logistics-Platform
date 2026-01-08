from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Order, OrderItem
from stock.models import StockListModel
from django.db import transaction


@receiver(post_save, sender=Order)
def sync_stock_on_order_status_change(sender, instance, created, **kwargs):
    """
    Sync stock when order status changes:
    - confirmed: Reserve stock (increase ordered_stock)
    - cancelled/returned: Release stock (decrease ordered_stock)
    - delivered: Deduct stock (decrease onhand_stock)
    """
    if not created:
        # Check if status changed
        try:
            old_order = Order.objects.get(pk=instance.pk)
            if old_order.status == instance.status:
                return  # No status change
        except Order.DoesNotExist:
            return
    
    with transaction.atomic():
        if instance.status == 'confirmed' and created:
            # Reserve stock for new confirmed orders
            for item in instance.items.all():
                if item.product:
                    try:
                        stock = StockListModel.objects.select_for_update().get(
                            goods_code=item.product.goods_code
                        )
                        stock.ordered_stock += item.quantity
                        stock.save()
                    except StockListModel.DoesNotExist:
                        pass
        
        elif instance.status in ['cancelled', 'returned']:
            # Release reserved stock
            for item in instance.items.all():
                if item.product:
                    try:
                        stock = StockListModel.objects.select_for_update().get(
                            goods_code=item.product.goods_code
                        )
                        stock.ordered_stock = max(0, stock.ordered_stock - item.quantity)
                        stock.save()
                    except StockListModel.DoesNotExist:
                        pass
        
        elif instance.status == 'delivered':
            # Deduct from onhand stock
            for item in instance.items.all():
                if item.product:
                    try:
                        stock = StockListModel.objects.select_for_update().get(
                            goods_code=item.product.goods_code
                        )
                        stock.onhand_stock = max(0, stock.onhand_stock - item.quantity)
                        stock.ordered_stock = max(0, stock.ordered_stock - item.quantity)
                        stock.save()
                    except StockListModel.DoesNotExist:
                        pass


@receiver(post_save, sender=OrderItem)
def validate_stock_on_order_item(sender, instance, created, **kwargs):
    """
    Validate stock availability when order item is created
    """
    if created and instance.product:
        try:
            stock = StockListModel.objects.get(goods_code=instance.product.goods_code)
            if stock.can_order_stock < instance.quantity:
                # Log warning but don't block (business decision)
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(
                    f"Order {instance.order.order_number} item {instance.product.goods_code} "
                    f"quantity {instance.quantity} exceeds available stock {stock.can_order_stock}"
                )
        except StockListModel.DoesNotExist:
            pass

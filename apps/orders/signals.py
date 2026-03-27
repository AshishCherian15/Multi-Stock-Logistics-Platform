from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import OrderItem


@receiver(post_save, sender=OrderItem)
@receiver(post_delete, sender=OrderItem)
def recalculate_order_total(sender, instance, **kwargs):
    """Auto-recalculate grand_total when items change."""
    order = instance.order
    from django.db.models import Sum
    items_total = order.items.aggregate(total=Sum('total_price'))['total'] or 0
    order.total_amount = items_total
    order.grand_total = items_total + order.delivery_fee - order.discount_amount
    order.save(update_fields=['total_amount', 'grand_total', 'updated_at'])

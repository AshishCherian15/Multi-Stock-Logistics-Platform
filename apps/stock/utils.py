from .models import StockListModel, StockAlert

def check_low_stock(goods_code, threshold=10):
    """Check if stock is low and create alert"""
    stock = StockListModel.objects.filter(goods_code=goods_code).first()
    if not stock:
        return
    
    existing_alert = StockAlert.objects.filter(goods_code=goods_code, is_resolved=False).first()
    
    if stock.can_order_stock <= 0:
        if not existing_alert or existing_alert.alert_level != 'critical':
            StockAlert.objects.create(
                goods_code=goods_code,
                alert_level='critical',
                message=f'OUT OF STOCK: {stock.goods_desc} has 0 available units'
            )
            from notifications.email_service import send_out_of_stock_alert
            send_out_of_stock_alert(goods_code, stock.goods_desc)
    elif stock.can_order_stock <= threshold:
        if not existing_alert or existing_alert.alert_level != 'warning':
            StockAlert.objects.create(
                goods_code=goods_code,
                alert_level='warning',
                message=f'LOW STOCK: {stock.goods_desc} has only {stock.can_order_stock} units left'
            )
            from notifications.email_service import send_low_stock_alert
            send_low_stock_alert(goods_code, stock.goods_desc, stock.can_order_stock)
    else:
        if existing_alert:
            existing_alert.is_resolved = True
            from django.utils import timezone
            existing_alert.resolved_at = timezone.now()
            existing_alert.save()

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from .models import StockListModel
from goods.models import ListModel

class StockAlertManager:
    @staticmethod
    def check_low_stock():
        """Check all products for low stock and send alerts"""
        alerts = []
        products = ListModel.objects.filter(is_delete=False)
        
        for product in products:
            stock = StockListModel.objects.filter(goods_code=product.goods_code).first()
            if stock:
                min_level = getattr(product, 'min_stock_level', 10)
                reorder_point = getattr(product, 'reorder_point', 5)
                
                if stock.goods_qty <= reorder_point:
                    alerts.append({
                        'product': product,
                        'stock': stock,
                        'level': 'critical',
                        'message': f'{product.goods_name} is critically low ({stock.goods_qty} units)'
                    })
                elif stock.goods_qty <= min_level:
                    alerts.append({
                        'product': product,
                        'stock': stock,
                        'level': 'warning',
                        'message': f'{product.goods_name} is running low ({stock.goods_qty} units)'
                    })
        
        if alerts:
            StockAlertManager.send_alerts(alerts)
        
        return alerts
    
    @staticmethod
    def send_alerts(alerts):
        """Send email alerts to authorized users"""
        recipients = User.objects.filter(
            is_active=True
        ).filter(
            is_superuser=True
        ) | User.objects.filter(
            groups__name__in=['Admin', 'Manager', 'Admin']
        ).distinct()
        
        if not recipients:
            return
        
        critical = [a for a in alerts if a['level'] == 'critical']
        warning = [a for a in alerts if a['level'] == 'warning']
        
        subject = f'Stock Alert: {len(critical)} Critical, {len(warning)} Warning'
        
        message = f"""
Stock Alert Summary
===================

Critical Stock Alerts ({len(critical)}):
"""
        for alert in critical:
            message += f"\n- {alert['message']}"
        
        message += f"\n\nWarning Stock Alerts ({len(warning)}):"
        for alert in warning:
            message += f"\n- {alert['message']}"
        
        message += "\n\nPlease take immediate action to reorder these items."
        message += "\n\nMultiStock Inventory System"
        
        email_list = [user.email for user in recipients if user.email]
        
        if email_list:
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    email_list,
                    fail_silently=False,
                )
                print(f"✅ Stock alerts sent to {len(email_list)} recipients")
            except Exception as e:
                print(f"❌ Failed to send stock alerts: {e}")

class StockMovementTracker:
    @staticmethod
    def add_stock(goods_code, quantity, reason='Purchase', user=None):
        """Add stock with tracking"""
        stock = StockListModel.objects.filter(goods_code=goods_code).first()
        if stock:
            stock.goods_qty += quantity
            stock.save()
            
            # Log movement
            from .models import StockMovement
            StockMovement.objects.create(
                goods_code=goods_code,
                movement_type='in',
                quantity=quantity,
                reason=reason,
                user=user
            )
            return True
        return False
    
    @staticmethod
    def remove_stock(goods_code, quantity, reason='Sale', user=None):
        """Remove stock with tracking"""
        stock = StockListModel.objects.filter(goods_code=goods_code).first()
        if stock and stock.goods_qty >= quantity:
            stock.goods_qty -= quantity
            stock.save()
            
            # Log movement
            from .models import StockMovement
            StockMovement.objects.create(
                goods_code=goods_code,
                movement_type='out',
                quantity=quantity,
                reason=reason,
                user=user
            )
            
            # Check if alert needed
            product = ListModel.objects.filter(goods_code=goods_code, is_delete=False).first()
            if product:
                min_level = getattr(product, 'min_stock_level', 10)
                if stock.goods_qty <= min_level:
                    StockAlertManager.check_low_stock()
            
            return True
        return False

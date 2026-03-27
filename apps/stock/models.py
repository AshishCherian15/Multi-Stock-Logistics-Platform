from django.db import models
from django.contrib.auth.models import User

class StockListModel(models.Model):
    goods_code = models.CharField(max_length=255, verbose_name="Goods Code")
    goods_desc = models.CharField(max_length=255, verbose_name="Goods Description")
    goods_qty = models.BigIntegerField(default=0, verbose_name="Total Qty")
    onhand_stock = models.BigIntegerField(default=0, verbose_name='On Hand Stock')
    can_order_stock = models.BigIntegerField(default=0, verbose_name='Available Stock')
    ordered_stock = models.BigIntegerField(default=0, verbose_name='Ordered Stock')
    damage_stock = models.BigIntegerField(default=0, verbose_name='Damage Stock')
    supplier = models.CharField(default='', max_length=255, verbose_name='Supplier')
    goods_image = models.ImageField(upload_to='stock_images/', null=True, blank=True, verbose_name='Product Image')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="Create Time")
    update_time = models.DateTimeField(auto_now=True, verbose_name="Update Time")
    openid = models.CharField(max_length=255, default='', verbose_name='User')

    class Meta:
        db_table = 'stocklist'
        verbose_name = 'Stock'
        verbose_name_plural = "Stock"
        ordering = ['-id']
        indexes = [
            models.Index(fields=['goods_code'], name='idx_stock_goods'),
            models.Index(fields=['goods_code', 'openid'], name='idx_stock_user'),
            models.Index(fields=['create_time'], name='idx_stock_created'),
        ]

    def __str__(self):
        return f"{self.goods_code} - {self.goods_qty} units"
    
    def save(self, *args, **kwargs):
        # Auto-sync quantities
        self.goods_qty = self.onhand_stock
        self.can_order_stock = max(0, self.onhand_stock - self.ordered_stock - self.damage_stock)
        super().save(*args, **kwargs)

class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjust', 'Adjustment'),
    ]
    
    goods_code = models.CharField(max_length=255)
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    reason = models.CharField(max_length=200)
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['goods_code'], name='idx_movement_goods'),
            models.Index(fields=['movement_type'], name='idx_movement_type'),
            models.Index(fields=['created_at'], name='idx_movement_created'),
        ]
    
    def __str__(self):
        return f"{self.goods_code} - {self.movement_type} - {self.quantity}"

class StockAlert(models.Model):
    ALERT_LEVELS = [
        ('critical', 'Critical'),
        ('warning', 'Warning'),
        ('info', 'Info'),
    ]
    
    goods_code = models.CharField(max_length=255)
    alert_level = models.CharField(max_length=10, choices=ALERT_LEVELS)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['goods_code'], name='idx_alert_goods'),
            models.Index(fields=['is_resolved'], name='idx_alert_resolved'),
            models.Index(fields=['alert_level', 'is_resolved'], name='idx_alert_active'),
        ]
    
    def __str__(self):
        return f"{self.goods_code} - {self.alert_level}"
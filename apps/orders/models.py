from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    ORDER_TYPES = [
        ('sale', 'Sales Order'),
        ('purchase', 'Purchase Order'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('packed', 'Packed'),
        ('ready_to_ship', 'Ready to Ship'),
        ('shipped', 'Shipped'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
    ]
    PAYMENT_STATUS = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    
    order_number = models.CharField(max_length=100, unique=True)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPES)
    customer = models.ForeignKey('customer.ListModel', on_delete=models.CASCADE, null=True, blank=True)
    customer_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_orders')
    supplier = models.ForeignKey('supplier.ListModel', on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='unpaid')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=40)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_address = models.TextField(blank=True)
    delivery_phone = models.CharField(max_length=20, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_orders')
    internal_notes = models.TextField(blank=True)
    openid = models.CharField(max_length=255, verbose_name="OpenID", help_text="Store/User Identifier", default="")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order_number} - {self.get_order_type_display()}"
    
    class Meta:
        indexes = [
            models.Index(fields=['order_number'], name='idx_order_number'),
            models.Index(fields=['status'], name='idx_order_status'),
            models.Index(fields=['payment_status'], name='idx_payment_status'),
            models.Index(fields=['created_at'], name='idx_order_created'),
            models.Index(fields=['status', 'payment_status'], name='idx_order_state'),
        ]
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            import uuid
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        if not self.delivery_date and self.status == 'confirmed' and self.created_at:
            from datetime import timedelta
            self.delivery_date = self.created_at.date() + timedelta(days=7)
        self.grand_total = self.total_amount + self.delivery_fee - self.discount_amount
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('goods.ListModel', on_delete=models.CASCADE, null=True, blank=True)
    product_name = models.CharField(max_length=200)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    seller = models.CharField(max_length=200, blank=True)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.order.order_number}: {self.old_status} → {self.new_status}"
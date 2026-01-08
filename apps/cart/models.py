from django.db import models
from django.contrib.auth.models import User
from goods.models import ListModel

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart - {self.user.username}"
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

class CartItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('product', 'Marketplace Product'),
        ('rental', 'Rental Item'),
        ('storage', 'Storage Unit'),
        ('locker', 'Locker'),
    ]
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES, default='product')
    
    # Product fields (for marketplace products)
    product = models.ForeignKey(ListModel, on_delete=models.CASCADE, null=True, blank=True)
    product_name = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    seller = models.CharField(max_length=200, blank=True)
    image_url = models.URLField(blank=True)
    
    # Rental/Storage/Locker specific fields
    rental_item = models.ForeignKey('rentals.RentalItem', on_delete=models.CASCADE, null=True, blank=True)
    storage_unit = models.ForeignKey('storage.StorageUnit', on_delete=models.CASCADE, null=True, blank=True)
    locker = models.ForeignKey('lockers.Locker', on_delete=models.CASCADE, null=True, blank=True)
    
    # Duration fields for rentals/storage/lockers
    duration_type = models.CharField(max_length=20, blank=True, help_text="hourly, daily, weekly, monthly")
    duration_count = models.IntegerField(default=1, help_text="Number of duration units")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
    
    @property
    def get_item(self):
        """Get the actual item object based on item_type"""
        if self.item_type == 'product':
            return self.product
        elif self.item_type == 'rental':
            return self.rental_item
        elif self.item_type == 'storage':
            return self.storage_unit
        elif self.item_type == 'locker':
            return self.locker
        return None

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=[('percentage', 'Percentage'), ('fixed', 'Fixed'), ('shipping', 'Free Shipping')])
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    usage_limit = models.IntegerField(default=0)
    used_count = models.IntegerField(default=0)
    
    def __str__(self):
        return self.code
    
    def is_valid(self):
        from django.utils import timezone
        return self.is_active and self.valid_from <= timezone.now() <= self.valid_to and (self.usage_limit == 0 or self.used_count < self.usage_limit)

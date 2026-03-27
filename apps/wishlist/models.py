from django.db import models
from django.contrib.auth.models import User
from goods.models import ListModel

class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Wishlist - {self.user.username}"

class WishlistItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('product', 'Marketplace Product'),
        ('rental', 'Rental Item'),
        ('storage', 'Storage Unit'),
        ('locker', 'Locker'),
    ]
    
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES, default='product')
    
    # Product fields (for marketplace products)
    product = models.ForeignKey(ListModel, on_delete=models.CASCADE, null=True, blank=True)
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    seller = models.CharField(max_length=200, blank=True)
    image_url = models.URLField(blank=True)
    
    # Rental/Storage/Locker specific fields
    rental_item = models.ForeignKey('rentals.RentalItem', on_delete=models.CASCADE, null=True, blank=True)
    storage_unit = models.ForeignKey('storage.StorageUnit', on_delete=models.CASCADE, null=True, blank=True)
    locker = models.ForeignKey('lockers.Locker', on_delete=models.CASCADE, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product_name}"
    
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

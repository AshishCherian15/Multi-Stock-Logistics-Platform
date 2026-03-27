from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Coupon(models.Model):
    DISCOUNT_TYPES = [
        ('percent', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    APPLICABLE_TO = [
        ('all', 'All Services'),
        ('rentals', 'Rentals'),
        ('storage', 'Storage Units'),
        ('lockers', 'Lockers'),
        ('marketplace', 'Marketplace'),
        ('pos', 'POS'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    applicable_to = models.CharField(max_length=20, choices=APPLICABLE_TO, default='all')
    usage_limit = models.IntegerField(null=True, blank=True, help_text="Total usage limit")
    usage_count = models.IntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False, "Coupon is inactive"
        if now < self.valid_from:
            return False, "Coupon not yet valid"
        if now > self.valid_until:
            return False, "Coupon has expired"
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False, "Coupon usage limit reached"
        return True, "Valid"
    
    def calculate_discount(self, amount):
        if self.discount_type == 'percent':
            discount = (amount * self.discount_value) / 100
            if self.max_discount:
                discount = min(discount, self.max_discount)
        else:
            discount = self.discount_value
        return min(discount, amount)
    
    def __str__(self):
        return f"{self.code} - {self.discount_value}{'%' if self.discount_type == 'percent' else '₹'}"
    
    class Meta:
        ordering = ['-created_at']

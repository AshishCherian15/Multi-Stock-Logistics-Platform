from django.db import models
from django.contrib.auth.models import User

class StockAdjustment(models.Model):
    ADJUSTMENT_TYPES = [
        ('count','Stock Count'),('correction','Correction'),
        ('damage','Damage Write-off'),('expiry','Expiry Write-off'),('return','Return to Stock'),
    ]
    STATUS_CHOICES = [('pending','Pending'),('approved','Approved'),('rejected','Rejected')]

    product = models.ForeignKey('goods.ListModel', on_delete=models.CASCADE, related_name='adjustments')
    adjustment_type = models.CharField(max_length=20, choices=ADJUSTMENT_TYPES)
    quantity = models.IntegerField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_adjustments')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_adjustments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product} | {self.adjustment_type} | {self.quantity}"

from django.db import models
from django.contrib.auth.models import User

class ReturnRequest(models.Model):
    STATUS = [('pending','Pending'),('approved','Approved'),('rejected','Rejected'),('completed','Completed')]
    REASONS = [('defective','Defective'),('wrong_item','Wrong Item'),('not_as_described','Not as Described'),('damaged_in_transit','Damaged in Transit'),('other','Other')]
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='return_requests')
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=30, choices=REASONS)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    handled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='handled_returns')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at']

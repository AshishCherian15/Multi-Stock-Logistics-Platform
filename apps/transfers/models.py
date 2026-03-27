from django.db import models
from django.contrib.auth.models import User

class StockTransfer(models.Model):
    STATUS = [('pending','Pending'),('in_transit','In Transit'),('completed','Completed'),('cancelled','Cancelled')]
    product = models.ForeignKey('goods.ListModel', on_delete=models.CASCADE)
    from_warehouse = models.ForeignKey('warehouse.ListModel', on_delete=models.CASCADE, related_name='outgoing_transfers')
    to_warehouse = models.ForeignKey('warehouse.ListModel', on_delete=models.CASCADE, related_name='incoming_transfers')
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at']

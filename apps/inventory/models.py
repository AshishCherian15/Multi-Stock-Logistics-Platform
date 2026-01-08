from django.db import models
from django.contrib.auth.models import User

class InventoryTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjustment', 'Adjustment'),
        ('transfer', 'Transfer'),
    ]
    
    product = models.ForeignKey('goods.ListModel', on_delete=models.CASCADE)
    warehouse = models.ForeignKey('warehouse.ListModel', on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    reference_number = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reference_number} - {self.get_transaction_type_display()}"

class StockAlert(models.Model):
    ALERT_TYPES = [
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('overstock', 'Overstock'),
    ]
    
    product = models.ForeignKey('goods.ListModel', on_delete=models.CASCADE)
    warehouse = models.ForeignKey('warehouse.ListModel', on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    current_quantity = models.IntegerField()
    threshold_quantity = models.IntegerField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

class InventoryReport(models.Model):
    REPORT_TYPES = [
        ('stock_summary', 'Stock Summary'),
        ('movement_report', 'Movement Report'),
        ('valuation_report', 'Valuation Report'),
    ]
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    file_path = models.CharField(max_length=500, blank=True)
    parameters = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
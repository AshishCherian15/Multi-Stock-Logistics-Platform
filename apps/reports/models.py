from django.db import models
from django.contrib.auth.models import User

class Report(models.Model):
    REPORT_TYPES = [
        ('inventory', 'Inventory Report'),
        ('sales', 'Sales Report'),
        ('purchase', 'Purchase Report'),
        ('customer', 'Customer Report'),
        ('financial', 'Financial Report'),
        ('stock_movement', 'Stock Movement Report'),
    ]
    
    FORMAT_TYPES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ]
    
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    format_type = models.CharField(max_length=20, choices=FORMAT_TYPES, default='pdf')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    parameters = models.JSONField(default=dict, blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_report_type_display()}"

class ScheduledReport(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50, choices=Report.REPORT_TYPES)
    format_type = models.CharField(max_length=20, choices=Report.FORMAT_TYPES, default='pdf')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    recipients = models.TextField(help_text='Comma-separated email addresses')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    last_run = models.DateTimeField(blank=True, null=True)
    next_run = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.frequency}"

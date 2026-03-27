from django.db import models
from django.contrib.auth.models import User

class DashboardWidget(models.Model):
    WIDGET_TYPES = [
        ('kpi', 'KPI Card'),
        ('chart', 'Chart'),
        ('table', 'Table'),
        ('list', 'List'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboard_widgets')
    title = models.CharField(max_length=100)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    data_source = models.CharField(max_length=100)
    position = models.IntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    config = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['position']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"

class AnalyticsReport(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    parameters = models.JSONField(default=dict, blank=True)
    schedule = models.CharField(max_length=50, blank=True)
    last_run = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

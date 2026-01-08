from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class SystemSettings(models.Model):
    company_name = models.CharField(max_length=200, default='MultiStock Logistics')
    currency = models.CharField(max_length=10, default='INR')
    timezone = models.CharField(max_length=50, default='Asia/Kolkata')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'settings'
        verbose_name_plural = 'System Settings'

class MaintenanceMode(models.Model):
    is_active = models.BooleanField(default=False)
    message = models.TextField(default='System is under maintenance. Please check back later.')
    allowed_roles = models.JSONField(default=list, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'settings'
        verbose_name_plural = 'Maintenance Mode'

class Announcement(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    target_roles = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        app_label = 'settings'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

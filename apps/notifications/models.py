from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    TYPES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('success', 'Success'),
        ('alert', 'Alert'),
    ]
    
    CATEGORIES = [
        ('system', 'System'),
        ('order', 'Order'),
        ('stock', 'Stock'),
        ('user', 'User'),
        ('message', 'Message'),
        ('payment', 'Payment'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPES, default='info')
    category = models.CharField(max_length=20, choices=CATEGORIES, default='system')
    link = models.CharField(max_length=500, blank=True)
    icon = models.CharField(max_length=50, blank=True)
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', 'is_read'])]

    def __str__(self):
        return f"{self.title} - {self.user.username}"

class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    email_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)
    stock_alerts = models.BooleanField(default=True)
    order_updates = models.BooleanField(default=True)
    message_notifications = models.BooleanField(default=True)
    system_notifications = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username} preferences"
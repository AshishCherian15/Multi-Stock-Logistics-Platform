from django.contrib import admin
from .models import Notification, NotificationPreference

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'type', 'category', 'is_read', 'created_at']
    list_filter = ['type', 'category', 'is_read', 'is_archived', 'created_at']
    search_fields = ['title', 'message', 'user__username']

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_enabled', 'push_enabled', 'stock_alerts', 'order_updates']
    list_filter = ['email_enabled', 'push_enabled']
from django.contrib import admin
from .models import SystemSettings, MaintenanceMode, Announcement

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'currency', 'timezone', 'updated_at']

@admin.register(MaintenanceMode)
class MaintenanceModeAdmin(admin.ModelAdmin):
    list_display = ['is_active', 'started_at', 'updated_at']

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'is_active', 'created_by', 'created_at', 'expires_at']
    list_filter = ['priority', 'is_active', 'created_at']

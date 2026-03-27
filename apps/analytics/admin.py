from django.contrib import admin
from .models import DashboardWidget, AnalyticsReport

@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'widget_type', 'position', 'is_visible']
    list_filter = ['widget_type', 'is_visible']

@admin.register(AnalyticsReport)
class AnalyticsReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'created_by', 'last_run', 'created_at']
    list_filter = ['report_type', 'created_at']

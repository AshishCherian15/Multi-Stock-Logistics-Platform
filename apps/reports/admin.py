from django.contrib import admin
from .models import Report, ScheduledReport

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'format_type', 'created_by', 'status', 'created_at']
    list_filter = ['report_type', 'format_type', 'status', 'created_at']
    search_fields = ['name', 'created_by__username']

@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'frequency', 'is_active', 'last_run', 'next_run']
    list_filter = ['report_type', 'frequency', 'is_active']
    search_fields = ['name', 'recipients']

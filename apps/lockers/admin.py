from django.contrib import admin
from .models import LockerType, Locker, LockerBooking, LockerAccessLog


@admin.register(LockerType)
class LockerTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'size', 'daily_rate', 'monthly_rate', 'has_climate_control', 'is_active']
    list_filter = ['size', 'has_climate_control', 'is_active']
    search_fields = ['name', 'description']


@admin.register(Locker)
class LockerAdmin(admin.ModelAdmin):
    list_display = ['locker_number', 'locker_type', 'location', 'status', 'access_code', 'is_active']
    list_filter = ['status', 'locker_type', 'is_active']
    search_fields = ['locker_number', 'location']
    actions = ['mark_available', 'mark_maintenance', 'generate_codes']
    
    def mark_available(self, request, queryset):
        queryset.update(status='available')
    mark_available.short_description = "Mark selected lockers as available"
    
    def mark_maintenance(self, request, queryset):
        queryset.update(status='maintenance')
    mark_maintenance.short_description = "Mark selected lockers for maintenance"
    
    def generate_codes(self, request, queryset):
        for locker in queryset:
            locker.generate_access_code()
    generate_codes.short_description = "Generate new access codes"


@admin.register(LockerBooking)
class LockerBookingAdmin(admin.ModelAdmin):
    list_display = ['booking_number', 'locker', 'customer_name', 'duration_type', 'start_date', 'end_date', 'status', 'paid']
    list_filter = ['status', 'duration_type', 'paid']
    search_fields = ['booking_number', 'customer_name', 'customer_email']
    date_hierarchy = 'created_at'


@admin.register(LockerAccessLog)
class LockerAccessLogAdmin(admin.ModelAdmin):
    list_display = ['locker', 'action', 'booking', 'user', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['locker__locker_number']
    date_hierarchy = 'timestamp'

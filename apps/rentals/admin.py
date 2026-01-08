from django.contrib import admin
from .models import RentalCategory, RentalItem, RentalBooking, MaintenanceSchedule

@admin.register(RentalCategory)
class RentalCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'created_at']
    list_filter = ['category_type']
    search_fields = ['name', 'description']

@admin.register(RentalItem)
class RentalItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'daily_rate', 'status', 'created_at']
    list_filter = ['category', 'status']
    search_fields = ['name', 'description']

@admin.register(RentalBooking)
class RentalBookingAdmin(admin.ModelAdmin):
    list_display = ['item', 'customer', 'start_date', 'end_date', 'status', 'total_amount']
    list_filter = ['status', 'start_date']
    search_fields = ['item__name', 'customer__username']

@admin.register(MaintenanceSchedule)
class MaintenanceScheduleAdmin(admin.ModelAdmin):
    list_display = ['item', 'scheduled_date', 'completed', 'created_at']
    list_filter = ['completed', 'scheduled_date']
    search_fields = ['item__name', 'description']

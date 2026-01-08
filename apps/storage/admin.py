from django.contrib import admin
from .models import StorageUnit, StorageBooking

@admin.register(StorageUnit)
class StorageUnitAdmin(admin.ModelAdmin):
    list_display = ['unit_number', 'type', 'size_sqft', 'location', 'status', 'price_per_month']
    list_filter = ['type', 'status', 'is_climate_controlled']
    search_fields = ['unit_number', 'location']

@admin.register(StorageBooking)
class StorageBookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'unit', 'start_date', 'end_date', 'status', 'total_amount']
    list_filter = ['status', 'start_date']
    search_fields = ['user__username', 'unit__unit_number']

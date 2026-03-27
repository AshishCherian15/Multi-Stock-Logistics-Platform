from django.contrib import admin
from .models import Carrier, ShippingRate, Shipment, TrackingEvent

@admin.register(Carrier)
class CarrierAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'contact_phone', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'code']

@admin.register(ShippingRate)
class ShippingRateAdmin(admin.ModelAdmin):
    list_display = ['carrier', 'service_type', 'min_weight', 'max_weight', 'base_rate', 'estimated_days', 'is_active']
    list_filter = ['carrier', 'is_active']
    search_fields = ['service_type']

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['shipment_number', 'order', 'carrier', 'tracking_number', 'status', 'recipient_name', 'created_at']
    list_filter = ['status', 'carrier', 'created_at']
    search_fields = ['shipment_number', 'tracking_number', 'recipient_name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(TrackingEvent)
class TrackingEventAdmin(admin.ModelAdmin):
    list_display = ['shipment', 'status', 'location', 'event_time']
    list_filter = ['status', 'event_time']
    search_fields = ['shipment__shipment_number', 'location']

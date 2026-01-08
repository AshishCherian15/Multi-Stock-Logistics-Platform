from django.contrib import admin
from .models import StockListModel, StockMovement, StockAlert

@admin.register(StockListModel)
class StockAdmin(admin.ModelAdmin):
    list_display = ['goods_code', 'goods_desc', 'goods_qty', 'onhand_stock', 'can_order_stock', 'ordered_stock']
    list_filter = ['supplier']
    search_fields = ['goods_code', 'goods_desc']
    readonly_fields = ['create_time', 'update_time']

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['goods_code', 'movement_type', 'quantity', 'reason', 'user', 'created_at']
    list_filter = ['movement_type', 'created_at']
    search_fields = ['goods_code', 'reason']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ['goods_code', 'alert_level', 'message', 'is_resolved', 'created_at']
    list_filter = ['alert_level', 'is_resolved', 'created_at']
    search_fields = ['goods_code', 'message']
    readonly_fields = ['created_at']
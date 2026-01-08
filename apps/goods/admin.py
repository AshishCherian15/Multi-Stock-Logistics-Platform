from django.contrib import admin
from .models import ListModel

@admin.register(ListModel)
class GoodsAdmin(admin.ModelAdmin):
    list_display = ['goods_code', 'goods_desc', 'goods_supplier', 'goods_price', 'safety_stock']
    list_filter = ['goods_class', 'goods_brand', 'goods_supplier']
    search_fields = ['goods_code', 'goods_desc']
    readonly_fields = ['create_time', 'update_time']
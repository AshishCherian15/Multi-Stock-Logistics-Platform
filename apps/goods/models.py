from django.db import models
from django.contrib.auth.models import User

class ListModel(models.Model):
    goods_code = models.CharField(max_length=255, unique=True, verbose_name="Goods Code")
    goods_desc = models.CharField(max_length=255, verbose_name="Goods Description")
    goods_supplier = models.CharField(max_length=255, verbose_name="Goods Supplier")
    goods_weight = models.FloatField(default=0, verbose_name="Goods Weight")
    goods_w = models.FloatField(default=0, verbose_name="Goods Width")
    goods_d = models.FloatField(default=0, verbose_name="Goods Depth")
    goods_h = models.FloatField(default=0, verbose_name="Goods Height")
    goods_unit = models.CharField(max_length=255, verbose_name="Goods Unit")
    goods_class = models.CharField(max_length=255, verbose_name="Goods Class")
    goods_brand = models.CharField(max_length=255, verbose_name="Goods Brand")
    safety_stock = models.BigIntegerField(default=0, verbose_name="Safety Stock")
    goods_cost = models.FloatField(default=0, verbose_name="Goods Cost")
    goods_price = models.FloatField(default=0, verbose_name="Goods Price")
    bar_code = models.CharField(max_length=255, blank=True, verbose_name="Bar Code")
    min_stock_level = models.IntegerField(default=10, verbose_name="Minimum Stock Level")
    reorder_point = models.IntegerField(default=5, verbose_name="Reorder Point")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="Expiry Date")
    openid = models.CharField(max_length=255, verbose_name="OpenID", help_text="User/Store Identifier", default="")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Created By")
    is_delete = models.BooleanField(default=False, verbose_name='Delete Label')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="Create Time")
    update_time = models.DateTimeField(auto_now=True, verbose_name="Update Time")

    class Meta:
        db_table = 'goods'
        verbose_name = 'Goods'
        verbose_name_plural = "Goods"
        ordering = ['-id']
        indexes = [
            models.Index(fields=['goods_code'], name='idx_goods_code'),
            models.Index(fields=['goods_class'], name='idx_goods_class'),
            models.Index(fields=['goods_brand'], name='idx_goods_brand'),
            models.Index(fields=['bar_code'], name='idx_bar_code'),
            models.Index(fields=['create_time'], name='idx_goods_created'),
            models.Index(fields=['goods_code', 'is_delete'], name='idx_goods_active'),
        ]

    def __str__(self):
        return f"{self.goods_code} - {self.goods_desc}"
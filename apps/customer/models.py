from django.db import models

class ListModel(models.Model):
    customer_name = models.CharField(max_length=255, verbose_name="Customer Name")
    customer_city = models.CharField(max_length=255, verbose_name="Customer City")
    customer_address = models.CharField(max_length=255, verbose_name="Customer Address")
    customer_contact = models.CharField(max_length=255, verbose_name="Customer Contact")
    customer_manager = models.CharField(max_length=255, verbose_name="Customer Manager")
    customer_level = models.BigIntegerField(default=1, verbose_name="Customer Level")
    openid = models.CharField(max_length=255, verbose_name="OpenID", help_text="Store Identifier", default="")
    is_delete = models.BooleanField(default=False, verbose_name='Delete Label')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="Create Time")
    update_time = models.DateTimeField(auto_now=True, verbose_name="Update Time")

    class Meta:
        db_table = 'customer'
        verbose_name = 'Customer'
        verbose_name_plural = "Customers"
        ordering = ['customer_name']
        indexes = [
            models.Index(fields=['customer_name'], name='idx_customer_name'),
            models.Index(fields=['customer_city'], name='idx_customer_city'),
            models.Index(fields=['create_time'], name='idx_customer_created'),
        ]

    def __str__(self):
        return self.customer_name
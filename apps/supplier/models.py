from django.db import models

class ListModel(models.Model):
    supplier_name = models.CharField(max_length=255, verbose_name="Supplier Name")
    supplier_city = models.CharField(max_length=255, verbose_name="Supplier City")
    supplier_address = models.CharField(max_length=255, verbose_name="Supplier Address")
    supplier_contact = models.CharField(max_length=255, verbose_name="Supplier Contact")
    supplier_manager = models.CharField(max_length=255, verbose_name="Supplier Manager")
    supplier_level = models.BigIntegerField(default=1, verbose_name="Supplier Level")
    openid = models.CharField(max_length=255, verbose_name="OpenID", help_text="Store Identifier", default="")
    is_delete = models.BooleanField(default=False, verbose_name='Delete Label')
    
    # Marketplace Integration - NEW FIELDS
    # badge = models.ForeignKey('multistock.Badge', on_delete=models.SET_NULL, null=True, blank=True, related_name='suppliers')
    is_marketplace_seller = models.BooleanField(default=True, verbose_name="Can sell in marketplace")
    can_list_rentals = models.BooleanField(default=True, verbose_name="Can list rental items")
    can_list_storage = models.BooleanField(default=True, verbose_name="Can list storage units")
    # can_list_auctions = models.BooleanField(default=True, verbose_name="Can create auctions")
    
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="Create Time")
    update_time = models.DateTimeField(auto_now=True, verbose_name="Update Time")

    class Meta:
        db_table = 'supplier'
        verbose_name = 'Supplier'
        verbose_name_plural = "Suppliers"
        ordering = ['supplier_name']

    def __str__(self):
        return self.supplier_name
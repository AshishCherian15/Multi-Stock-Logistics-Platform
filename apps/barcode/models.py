from django.db import models

class BarcodeLabel(models.Model):
    PAPER_SIZES = [
        ('a4', 'A4'),
        ('letter', 'Letter'),
        ('label', 'Label Sheet'),
    ]
    
    product = models.ForeignKey('goods.ListModel', on_delete=models.CASCADE)
    warehouse = models.ForeignKey('warehouse.ListModel', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    paper_size = models.CharField(max_length=20, choices=PAPER_SIZES, default='a4')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Barcode for {self.product.goods_desc}"
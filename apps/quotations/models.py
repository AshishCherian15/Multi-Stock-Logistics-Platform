from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime


def default_expiry():
    return timezone.now() + datetime.timedelta(days=30)


class Quotation(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
        ('converted', 'Converted to Order'),
    ]

    quotation_number = models.CharField(max_length=30, unique=True, editable=False)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=30, blank=True)
    customer_company = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    terms = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                   help_text="Tax percentage, e.g. 10 for 10%")
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valid_from = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(default=default_expiry)
    converted_order_id = models.PositiveIntegerField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='quotations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'quotations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['customer_email']),
        ]

    def save(self, *args, **kwargs):
        if not self.quotation_number:
            stamp = timezone.now().strftime('%Y%m%d')
            last = Quotation.objects.filter(
                quotation_number__startswith=f'QT-{stamp}'
            ).count() + 1
            self.quotation_number = f'QT-{stamp}-{last:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quotation_number} – {self.customer_name}"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at and self.status not in ('converted', 'rejected')

    def recalculate_totals(self):
        """Recompute subtotal/tax/total from line items."""
        self.subtotal = sum(item.line_total for item in self.items.all())
        self.tax_amount = (self.subtotal * self.tax_rate / 100).quantize(
            self.subtotal.__class__('0.01')
        )
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        self.save(update_fields=['subtotal', 'tax_amount', 'total_amount', 'updated_at'])


class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=12, decimal_places=3, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                       help_text="Line-level discount percentage")

    class Meta:
        db_table = 'quotation_items'

    def __str__(self):
        return f"{self.quotation.quotation_number} – {self.description}"

    @property
    def line_total(self):
        gross = self.quantity * self.unit_price
        return gross * (1 - self.discount_pct / 100)

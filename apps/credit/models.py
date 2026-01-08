from django.db import models
from customer.models import ListModel as Customer

class CreditProfile(models.Model):
    RISK_LEVELS = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
    ]
    
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='credit_profile')
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    available_credit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    used_credit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, default='low')
    payment_terms_days = models.IntegerField(default=30)
    overdue_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'credit_profiles'
    
    def __str__(self):
        return f"{self.customer.customer_name} - ${self.credit_limit}"

class CreditTransaction(models.Model):
    TYPE_CHOICES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
        ('payment', 'Payment'),
        ('adjustment', 'Adjustment'),
    ]
    
    profile = models.ForeignKey(CreditProfile, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'credit_transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.profile.customer.customer_name} - {self.transaction_type} - ${self.amount}"

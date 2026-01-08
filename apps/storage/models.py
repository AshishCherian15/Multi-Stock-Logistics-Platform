from django.db import models
from django.contrib.auth.models import User

class StorageUnit(models.Model):
    TYPE_CHOICES = [
        ('locker', 'Locker'),
        ('mini', 'Mini Warehouse'),
        ('standard', 'Standard Unit'),
        ('large', 'Large Unit'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Maintenance'),
    ]
    
    unit_number = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    size_sqft = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    floor = models.IntegerField(default=1)
    zone = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=dict)
    access_code = models.CharField(max_length=20, blank=True)
    is_climate_controlled = models.BooleanField(default=False)
    image = models.ImageField(upload_to='storage_images/', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_storage_units')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_storage_units')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'storage_units'
        ordering = ['unit_number']
    
    def __str__(self):
        return f"{self.unit_number} - {self.get_type_display()}"

class StorageBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    
    unit = models.ForeignKey(StorageUnit, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_method = models.CharField(max_length=50, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    access_code = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    terms_agreed = models.BooleanField(default=False)
    penalty_agreed = models.BooleanField(default=False)
    liability_agreed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'storage_bookings'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.unit.unit_number}"

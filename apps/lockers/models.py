from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
import string


class LockerType(models.Model):
    """Different types of lockers available"""
    LOCKER_SIZES = [
        ('small', 'Small (12" x 12" x 18")'),
        ('medium', 'Medium (18" x 18" x 24")'),
        ('large', 'Large (24" x 24" x 36")'),
        ('xlarge', 'Extra Large (36" x 36" x 48")'),
        ('climate', 'Climate Controlled'),
    ]
    
    name = models.CharField(max_length=100)
    size = models.CharField(max_length=20, choices=LOCKER_SIZES)
    description = models.TextField(blank=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    weekly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    has_climate_control = models.BooleanField(default=False)
    has_security_monitoring = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'locker_types'
        ordering = ['size', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.get_size_display()}"


class Locker(models.Model):
    """Individual locker units"""
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('reserved', 'Reserved'),
        ('maintenance', 'Under Maintenance'),
        ('disabled', 'Disabled'),
    ]
    
    locker_number = models.CharField(max_length=20, unique=True)
    locker_type = models.ForeignKey(LockerType, on_delete=models.CASCADE, related_name='lockers')
    location = models.CharField(max_length=200, help_text="Building/Floor/Section")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    access_code = models.CharField(max_length=10, blank=True)
    image = models.ImageField(upload_to='locker_images/', null=True, blank=True)
    notes = models.TextField(blank=True)
    last_maintenance = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_lockers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_lockers')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lockers'
        ordering = ['locker_number']
    
    def __str__(self):
        return f"Locker {self.locker_number} - {self.status}"
    
    def generate_access_code(self):
        """Generate a random 6-digit access code"""
        self.access_code = ''.join(random.choices(string.digits, k=6))
        self.save()
        return self.access_code
    
    def is_available(self):
        return self.status == 'available' and self.is_active


class LockerBooking(models.Model):
    """Locker rental bookings"""
    DURATION_TYPES = [
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('overdue', 'Overdue'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    
    booking_number = models.CharField(max_length=20, unique=True)
    locker = models.ForeignKey(Locker, on_delete=models.CASCADE, related_name='bookings')
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    duration_type = models.CharField(max_length=20, choices=DURATION_TYPES)
    duration_count = models.IntegerField(default=1, help_text="Number of hours/days/weeks/months")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    access_code = models.CharField(max_length=10)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_method = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    items_description = models.TextField(blank=True, help_text="Description of items stored")
    notes = models.TextField(blank=True)
    terms_agreed = models.BooleanField(default=False)
    penalty_agreed = models.BooleanField(default=False)
    liability_agreed = models.BooleanField(default=False)
    notification_sent = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'locker_bookings'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Booking {self.booking_number} - {self.customer_name}"
    
    def save(self, *args, **kwargs):
        if not self.booking_number:
            self.booking_number = f"LB-{timezone.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        super().save(*args, **kwargs)
    
    def is_overdue(self):
        return timezone.now() > self.end_date and self.status == 'active'


class LockerAccessLog(models.Model):
    """Log of locker access events"""
    ACTION_TYPES = [
        ('open', 'Opened'),
        ('close', 'Closed'),
        ('access_denied', 'Access Denied'),
        ('maintenance', 'Maintenance Access'),
    ]
    
    locker = models.ForeignKey(Locker, on_delete=models.CASCADE, related_name='access_logs')
    booking = models.ForeignKey(LockerBooking, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    access_code_used = models.CharField(max_length=10, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'locker_access_logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.locker.locker_number} - {self.action} at {self.timestamp}"

from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Carrier(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    tracking_url = models.URLField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    logo = models.ImageField(upload_to='carriers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ShippingRate(models.Model):
    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE)
    service_type = models.CharField(max_length=100)
    min_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_weight = models.DecimalField(max_digits=10, decimal_places=2)
    base_rate = models.DecimalField(max_digits=10, decimal_places=2)
    per_kg_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estimated_days = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def calculate_cost(self, weight):
        return self.base_rate + (weight * self.per_kg_rate)

    def __str__(self):
        return f"{self.carrier.name} - {self.service_type}"

class Shipment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('picked', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled'),
    ]
    
    shipment_number = models.CharField(max_length=50, unique=True)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='shipments')
    carrier = models.ForeignKey(Carrier, on_delete=models.SET_NULL, null=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    service_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    sender_name = models.CharField(max_length=200)
    sender_address = models.TextField()
    sender_city = models.CharField(max_length=100)
    sender_phone = models.CharField(max_length=20)
    
    recipient_name = models.CharField(max_length=200)
    recipient_address = models.TextField()
    recipient_city = models.CharField(max_length=100)
    recipient_phone = models.CharField(max_length=20)
    
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    dimensions = models.CharField(max_length=100, blank=True)
    package_count = models.IntegerField(default=1)
    
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)
    insurance_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    pickup_date = models.DateField(null=True, blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    actual_delivery = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.shipment_number} - {self.recipient_name}"

class TrackingEvent(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='tracking_events')
    status = models.CharField(max_length=50)
    location = models.CharField(max_length=200)
    description = models.TextField()
    event_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-event_time']

    def __str__(self):
        return f"{self.shipment.shipment_number} - {self.status}"

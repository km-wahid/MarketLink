from django.db import models
from vendors.models import VendorProfile

# Create your models here.
class Service(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=255)
    description = models.TextField()
    is_active = models.BooleanField(default=True)


class ServiceVariant(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="variants")
    name = models.CharField(max_length=100)  # Basic, Premium
    price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_minutes = models.IntegerField()
    stock = models.IntegerField()   # simultaneous bookings allowed

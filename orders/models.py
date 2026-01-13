from django.db import models
from users.models import User
from vendors.models import VendorProfile
from services.models import ServiceVariant
import uuid
# Create your models here.

class RepairOrder(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )

    order_id = models.UUIDField(default=uuid.uuid4, unique=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE)
    variant = models.ForeignKey(ServiceVariant, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




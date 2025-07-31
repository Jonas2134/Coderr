from django.db import models
from django.conf import settings

from offers_app.models import OfferDetail

# Create your models here.

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    offer_detail_id = models.ForeignKey(OfferDetail, on_delete=models.CASCADE)
    customer_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_orders')
    business_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='business_orders')
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

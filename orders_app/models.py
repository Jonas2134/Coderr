from django.db import models
from django.conf import settings

from offers_app.models import OfferDetail

# Create your models here.

class Order(models.Model):
    """
    Represents a purchase order linking a customer to a business for a specific OfferDetail.

    Fields:
        offer_detail (OfferDetail): The specific variant being ordered.
        customer_user (CustomUser): The customer placing the order (type='customer').
        business_user (CustomUser): The business fulfilling the order (type='business').
        status (str): Current status of the order; one of 'in_progress', 'completed', or 'cancelled'.
        created_at (datetime): Timestamp when the order was created (auto-generated).
        updated_at (datetime): Timestamp when the order was last modified (auto-updated).

    Methods:
        __str__() → str:
            Returns a human-readable summary in the form
            "Order <id> - <offer title> (<status>)".
    """
    ORDER_STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    offer_detail = models.ForeignKey(OfferDetail, on_delete=models.CASCADE, related_name='orders')
    customer_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_orders', limit_choices_to={"type": "customer"})
    business_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='business_orders', limit_choices_to={"type": "business"})
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Return a concise, human-readable representation of the order.

        Format:
            "Order <id> - <offer_detail.title> (<status>)"

        Returns:
            str: Summary string including order ID, offer title, and status.
        """
        return f"Order {self.id} - {self.offer_detail.title} ({self.status})"

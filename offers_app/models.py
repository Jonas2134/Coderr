from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

# Create your models here.

class Offer(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='offer_pictures/', blank=True, null=True)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='offers', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.pk}: {self.title}"

    def clean(self):
        super().clean()
        detail_types = set(self.details.values_list('offer_type', flat=True))
        required = {'basic', 'standard', 'premium'}
        if detail_types != required:
            raise ValidationError('An Offer must have exactly one basic, one standard, and one premium detail.')


class OfferDetail(models.Model):
    BASIC = 'basic'
    STANDARD = 'standard'
    PREMIUM = 'premium'

    OFFER_TYPE_CHOICES = [
        (BASIC, 'Basic'),
        (STANDARD, 'Standard'),
        (PREMIUM, 'Premium'),
    ]

    offer = models.ForeignKey(Offer, related_name='details', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    revisions = models.IntegerField(default=0)
    delivery_time_in_days = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField()
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)

    class Meta:
        unique_together = ('offer', 'offer_type')

    def __str__(self):
        return f"{self.offer.title} - {self.offer_type}"

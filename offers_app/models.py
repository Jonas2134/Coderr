from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

# Create your models here.

class Offer(models.Model):
    """
    Represents a top-level offer, grouping multiple detail variants (basic, standard, premium).

    Fields:
        title (str): Short, human-readable title of the offer.
        image (Image): Optional image illustrating the offer.
        description (str): Optional longer text describing the offer.
        created_at (datetime): Timestamp when this offer was first created (auto).
        updated_at (datetime): Timestamp when this offer was last modified (auto).
        creator (User): ForeignKey to the user who created this offer.

    Methods:
        __str__() -> str:
            Returns a string in the format "<id>: <title>" for readability.
        clean() -> None:
            Validates that exactly one detail of each required type exists.
    """
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='offer_pictures/', blank=True, null=True)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='offers', on_delete=models.CASCADE)

    def __str__(self):
        """
        Return a human-readable representation of the offer.

        Returns:
            str: Formatted as "<pk>: <title>".
        """
        return f"{self.pk}: {self.title}"

    def clean(self):
        """
        Ensure that the offer has exactly one detail of each required type.

        Raises:
            ValidationError: If the set of detail types is not exactly
                             {'basic', 'standard', 'premium'}.
        """
        super().clean()
        detail_types = set(self.details.values_list('offer_type', flat=True))
        required = {'basic', 'standard', 'premium'}
        if detail_types != required:
            raise ValidationError('An Offer must have exactly one basic, one standard, and one premium detail.')


class OfferDetail(models.Model):
    """
    Represents a single variant of an offer (basic, standard, or premium).

    Fields:
        offer (Offer): The parent offer this detail belongs to.
        title (str): Title of this specific detail variant.
        revisions (int): Number of revisions included in this package.
        delivery_time_in_days (int): Delivery time in days for this variant.
        price (Decimal): Price charged for this variant.
        features (JSON): List or dict of features included.
        offer_type (str): One of 'basic', 'standard', or 'premium'.

    Meta:
        unique_together: Ensures one detail per (offer, offer_type).

    Methods:
        __str__() -> str:
            Returns "<offer.title> – <offer_type>".
    """
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
        """
        Return a human-readable representation of the detail.

        Returns:
            str: Formatted as "<offer.title> – <offer_type>".
        """
        return f"{self.offer.title} - {self.offer_type}"

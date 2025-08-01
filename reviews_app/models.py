from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

# Create your models here.

class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 11)]

    business_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='business_reviews', limit_choices_to={"type": "business"})
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews', limit_choices_to={"type": "customer"})
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Rating from 1 to 10, where 1 is the worst and 10 is the best."
    )

    def clean(self):
        super().clean()
        errors = {}
        if self.business_user.type != 'business':
            errors['business_user'] = "The business_user must be of type 'business'."
        if self.reviewer.type != 'customer':
            errors['reviewer'] = "The reviewer must be of type 'customer'."
        if errors:
            raise ValidationError(errors)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(rating__gte=1, rating__lte=10),
                name='rating_between_1_and_10'
            )
        ]

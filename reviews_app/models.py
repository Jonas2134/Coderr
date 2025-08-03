from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

# Create your models here.

class Review(models.Model):
    """
    Represents a review left by a customer user for a business user.

    Fields:
        - business_user (ForeignKey): The user who is being reviewed.
            Must be a user of type 'business'.
        - reviewer (ForeignKey): The user who writes the review.
            Must be a user of type 'customer'.
        - description (TextField): Optional text describing the review.
        - rating (PositiveSmallIntegerField): A numeric score from 1 to 10.
            Uses choices and validators to enforce valid values.
        - created_at (DateTimeField): Timestamp of when the review was created.
        - updated_at (DateTimeField): Timestamp of the last update.

    Constraints:
        - Enforces that `rating` is between 1 and 10 using a database-level check constraint.

    Validation:
        - `clean()` method ensures that:
            - `business_user` has user type 'business'
            - `reviewer` has user type 'customer'
          If either condition fails, a `ValidationError` is raised.

    String Representation:
        - Defaults to the base `__str__()` implementation.
    """
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

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(rating__gte=1, rating__lte=10),
                name='rating_between_1_and_10'
            )
        ]

    def __str__(self):
        """
        Returns a human-readable string representation of the Review instance.

        Format:
            "Review (<rating>/10) by <reviewer> for <business_user>"

        This method helps identify the review by showing who created it,
        for which business user, and what rating was given.

        Returns:
            str: A concise summary of the review.
        """
        return f"Review ({self.rating}/10) by {self.reviewer} for {self.business_user}"

    def clean(self):
        """
        Validates the review instance.

        Ensures that:
            - `business_user` is of type 'business'.
            - `reviewer` is of type 'customer'.

        Raises:
            ValidationError: if either condition is violated.
        """
        super().clean()
        errors = {}
        if self.business_user.type != 'business':
            errors['business_user'] = "The business_user must be of type 'business'."
        if self.reviewer.type != 'customer':
            errors['reviewer'] = "The reviewer must be of type 'customer'."
        if errors:
            raise ValidationError(errors)

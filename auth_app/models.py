from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    """
    Custom user model extending Django's built-in AbstractUser to distinguish
    between regular (customer) and business users.

    Attributes:
        USER_TYPE_CHOICES (list of tuple): Available user type options.
            - "customer": Custom User (end-customer)
            - "business": Business User (company account)
        type (str): The user’s account type. Must be one of the keys defined
            in USER_TYPE_CHOICES.
    """
    USER_TYPE_CHOICES = [
        ("customer", "Custom User"),
        ("business", "Business User"),
    ]

    type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

    def __str__(self):
        """
        Return a human-readable representation of the user.

        Overrides the default __str__ to include the display name of the
        `type` field in parentheses.

        Returns:
            str: A string of the form "username (Customer)" or
                "username (Business User)".
        """
        return f"{self.username} ({self.get_type_display()})"

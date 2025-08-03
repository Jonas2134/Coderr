from django.db import models
from django.conf import settings

# Create your models here.

class UserProfile(models.Model):
    """
    Represents additional profile data for a user.

    Fields:
        user (CustomUser): One-to-one link to the user.
        location (str): Optional free-form location text.
        tel (str): Optional telephone number.
        description (str): Optional long-form profile description.
        working_hours (str): Optional working hours specification.
        file (Image): Optional profile picture or document.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    location = models.CharField(max_length=255, blank=True, default="")
    tel = models.CharField(max_length=50, blank=True, default="")
    description = models.TextField(blank=True, default="")
    working_hours = models.CharField(max_length=100, blank=True, default="")
    file = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        """
        Return a human-readable representation of the profile.

        Returns:
            str: The username followed by “'s Profile”.
        """
        return f"{self.user.username}'s Profile"

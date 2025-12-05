from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # GOK / Ajira Alignment Fields
    ajira_id = models.CharField(max_length=20, blank=True, help_text="e.g., AJ-123456")
    phone_number = models.CharField(max_length=15, blank=True)

    # Verification Status
    is_verified = models.BooleanField(default=False)
    bio = models.TextField(blank=True, max_length=500)

    def __str__(self):
        return f"{self.user.username}'s Profile"
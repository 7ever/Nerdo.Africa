from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    ajira_id = models.CharField(max_length=20, blank=True, help_text="e.g., AJ-123456")
    phone_number = models.CharField(max_length=15, blank=True)
    
    # NEW: Fields for OTP Logic
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(auto_now=True)
    
    is_verified = models.BooleanField(default=False)
    bio = models.TextField(blank=True, max_length=500)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
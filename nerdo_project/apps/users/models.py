from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Identity
    ajira_id = models.CharField(max_length=20, blank=True, help_text="e.g., AJ-123456")
    phone_number = models.CharField(max_length=15, blank=True)
    
    # OTP & Verification
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(auto_now=True)
    
    # Status Flags
    is_verified = models.BooleanField(default=False) # Ajira verified
    is_phone_verified = models.BooleanField(default=False) # Phone Verified
    
    bio = models.TextField(blank=True, max_length=500)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
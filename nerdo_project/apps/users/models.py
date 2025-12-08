from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Roles
    ROLE_CHOICES = [
        ('job_seeker', 'Job Seeker'),
        ('employer', 'Employer'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='job_seeker')

    # Identity
    ajira_id = models.CharField(max_length=20, blank=True, help_text="e.g., AJ-123456")
    phone_number = models.CharField(max_length=15, blank=True)
    
    # Profile Data
    avatar = models.ImageField(upload_to='avatars/', default='defaults/default_avatar.png', blank=True)
    cv = models.FileField(upload_to='cvs/', blank=True, null=True, help_text="Upload your CV/Resume (PDF/Docx)")

    # NEW: OTP Fields
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(auto_now=True)

    # Status Flags
    is_verified = models.BooleanField(default=False) 
    is_phone_verified = models.BooleanField(default=False) # New flag
    is_employer_verified = models.BooleanField(default=False, help_text="Designates if this employer can post jobs.")
    is_premium = models.BooleanField(default=False, help_text="Designates if the user has paid for premium access.")

    bio = models.TextField(blank=True, max_length=500)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Signals
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
from django.db import models
from django.conf import settings

# Create your models here.

class LearningPath(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='learning_paths')
    topic = models.CharField(max_length=255)
    skill_level = models.CharField(max_length=50, default='beginner')
    duration = models.IntegerField(help_text="Duration in weeks")
    roadmap_data = models.JSONField(help_text="The generated roadmap structure")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.topic} ({self.skill_level})"

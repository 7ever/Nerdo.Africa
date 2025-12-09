from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Job(models.Model):
    # 1. Job Types
    TYPE_CHOICES = [
        ('Freelance', 'Freelance / Gig'),
        ('Contract', 'Short-Term Contract'),
        ('Part-Time', 'Part-Time'),
        ('Full-Time', 'Full-Time'),
        ('Internship', 'Internship / Attachment'),
    ]

    # 2. Categories (Ajira Aligned)
    CATEGORY_CHOICES = [
        ('Tech', 'Software Development & IT'),
        ('Design', 'Graphic Design & Creative'),
        ('Writing', 'Content Writing & Translation'),
        ('Admin', 'Virtual Assistant & Data Entry'),
        ('Marketing', 'Digital Marketing & Sales'),
        ('Video', 'Video Editing & Animation'),
    ]

    # 3. Experience Levels
    LEVEL_CHOICES = [
        ('Entry', 'Entry Level (Beginner)'),
        ('Intermediate', 'Intermediate'),
        ('Expert', 'Expert'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200, help_text="e.g., 'Looking for a Logo Designer'")
    description = models.TextField(help_text="Detailed requirements, deliverables, and skills needed.")
    budget = models.DecimalField(max_digits=10, decimal_places=2, help_text="Project budget in KES")
    job_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Freelance')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Tech')
    experience_level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='Entry')
    
    # Moderation
    is_approved = models.BooleanField(default=False, help_text="Job must be approved by admin before being visible.")

    # Logistics
    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.author.username if self.author else 'Unknown'}"
    
class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_applications')
    cover_letter = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'applicant') # Prevent double applying

    def __str__(self):
        return f"{self.applicant.username} -> {self.job.title}"

class JobReminder(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='reminders')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_reminders')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'user') # Prevent duplicate reminders

    def __str__(self):
        return f"Reminder: {self.user.username} -> {self.job.title}"
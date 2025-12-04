from django.db import models
from django.utils import timezone

class Job(models.Model):
    # 1. Job Types: Standard freelancing definitions
    TYPE_CHOICES = [
            ('Freelance', 'Freelance / One-off'),
            ('Contract', 'Contract (Long-term)'),
            ('Part-Time', 'Part-Time'),
            ('Full-Time', 'Full-Time'),
            ('Internship', 'Internship / Attachment'),
        ]

    # 2. Categories: Aligned with Ajira Digital & Upwork for easier AI matching later
    CATEGORY_CHOICES = [
            ('Tech', 'Software Dev & IT'),
            ('Design', 'Graphic Design & Creative'),
            ('Writing', 'Content Writing & Translation'),
            ('Admin', 'Virtual Assistant & Data Entry'),
            ('Marketing', 'Digital Marketing & Sales'),
            ('Video', 'Video Editing & Animation'),
        ]

    # 3. Experience: Helps beginners (youth) filter jobs they can actually do
    LEVEL_CHOICES = [
            ('Entry', 'Entry Level (Beginner)'),
            ('Intermediate', 'Intermediate'),
            ('Expert', 'Expert'),
        ]

    title = models.CharField(max_length=200, help_text="e.g. 'Looking for a Logo Designer'")
    description = models.TextField(help_text="Detailed requirements, deliverables, and skills needed.")
        
    # Financials
    budget = models.DecimalField(max_digits=10, decimal_places=2, help_text="Project budget in KES")
        
    # Classification
    job_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Freelance')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Tech')
    experience_level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='Entry')
        
    # Logistics
    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
            ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_job_type_display()})"
from django.db import models

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

    title = models.CharField(max_length=200)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)

    job_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Freelance')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Tech')
    experience_level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='Entry')

    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
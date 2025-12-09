from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.opportunities.models import Job, Application
from apps.users.utils import send_otp_sms
from datetime import timedelta

class Command(BaseCommand):
    help = 'Checks for jobs closing in 3 days and notifies applicants'

    def handle(self, *args, **kwargs):
        self.stdout.write("Checking for upcoming deadlines...")
        
        # 1. Calculate the target date (Today + 3 Days)
        today = timezone.now().date()
        target_date = today + timedelta(days=3)
        
        # 2. Find Jobs expiring exactly on that day
        # Note: Depending on your 'deadline' field type (Date vs DateTime), this might need adjustment.
        # Assuming DateField based on common practice.
        expiring_jobs = Job.objects.filter(deadline=target_date)
        
        if not expiring_jobs.exists():
            self.stdout.write(self.style.SUCCESS(f"No jobs expiring on {target_date} (in 3 days)."))
            return

        count = 0
        for job in expiring_jobs:
            self.stdout.write(f"Found expiring job: {job.title}")
            
            # 3. Get all applicants for this job
            applications = Application.objects.filter(job=job)
            
            for app in applications:
                user = app.applicant
                if hasattr(user, 'profile') and user.profile.phone_number:
                    phone = user.profile.phone_number
                    msg = f"Reminder: The job '{job.title}' you applied for closes on {job.deadline}. Good luck!"
                    
                    self.stdout.write(f" -> Queued SMS for {user.username} ({phone})")
                    
                    # Send SMS using the refactored utility
                    success = send_otp_sms(phone_number=phone, message=msg)
                    
                    if success:
                       count += 1
                    else:
                       self.stdout.write(self.style.WARNING(f"    Failed to send SMS to {user.username}"))
        
        self.stdout.write(self.style.SUCCESS(f"Done. Sent {count} reminders."))

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.opportunities.models import Job, Application
from apps.users.utils import send_sms
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
            
            # Notify Applicants
            for app in applications:
                user = app.applicant
                if hasattr(user, 'profile') and user.profile.phone_number:
                    phone = user.profile.phone_number
                    msg = f"Reminder: The job '{job.title}' closes in 3 days ({job.deadline})."
                    
                    self.stdout.write(f" -> Queued SMS for Applicant {user.username} ({phone})")
                    send_sms(phone, msg)
                    count += 1

            # 4. Notify Reminder Subscribers (NEW)
            from apps.opportunities.models import JobReminder
            reminders = JobReminder.objects.filter(job=job)
            
            for reminder in reminders:
                user = reminder.user
                # Avoid duplicate SMS if user is also an applicant (optional optimization)
                if applications.filter(applicant=user).exists():
                    continue

                if hasattr(user, 'profile') and user.profile.phone_number:
                    phone = user.profile.phone_number
                    msg = f"Reminder: The job '{job.title}' closes in 3 days ({job.deadline})."
                    
                    self.stdout.write(f" -> Queued SMS for Subscriber {user.username} ({phone})")
                    send_sms(phone, msg)
                    count += 1
        
        self.stdout.write(self.style.SUCCESS(f"Done. Sent {count} reminders."))

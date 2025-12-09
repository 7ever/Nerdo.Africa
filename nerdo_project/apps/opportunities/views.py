
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Job, Application
from .forms import JobForm
from apps.users.decorators import premium_required, is_verified_employer

# 1. SPLIT VIEW: JOB MARKET WITH SEARCH & FILTERS
def job_market(request):
    # Start with all APPROVED jobs
    # Optimized: Fetch author efficiently
    jobs = Job.objects.filter(is_approved=True).select_related('author')
    
    # --- SEARCH & FILTER LOGIC ---
    query = request.GET.get('q')
    category_filter = request.GET.get('category')
    type_filter = request.GET.get('type')
    level_filter = request.GET.get('level')

    if query:
        # Search in Title OR Description
        jobs = jobs.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query)
        )
    
    if category_filter:
        jobs = jobs.filter(category=category_filter)
        
    if type_filter:
        jobs = jobs.filter(job_type=type_filter)
        
    if level_filter:
        jobs = jobs.filter(experience_level=level_filter)

    # --- SPLIT VIEW SELECTION ---
    # Check if a specific job was clicked via ?job_id=...
    selected_job_id = request.GET.get('job_id')
    
    selected_job = None
    if selected_job_id:
        # Allow selecting unapproved jobs IF you are the author (preview)
        selected_job = get_object_or_404(Job.objects.select_related('author').prefetch_related('applications'), pk=selected_job_id)
    else:
        # Default to the first job in the filtered list
        selected_job = jobs.prefetch_related('applications').first() if jobs.exists() else None

    context = {
        "jobs": jobs,
        "selected_job": selected_job,
        # Pass choices for Filter Pills
        "categories": Job.CATEGORY_CHOICES,
        "types": Job.TYPE_CHOICES,
        "levels": Job.LEVEL_CHOICES,
    }
    return render(request, "opportunities/job_list.html", context)

# 2. READ ONE (Details Page - Mobile Fallback)
def job_detail(request, pk):
    # Optimized: Fetch author and applications
    job = get_object_or_404(Job.objects.select_related('author').prefetch_related('applications'), pk=pk)
    context = {"job": job}

    return render(request, "opportunities/job_detail.html", context)

# 3. CREATE (Restricted to Verify Employer)
@login_required
@user_passes_test(is_verified_employer, login_url='employer_dashboard', redirect_field_name=None)
def create_job(request):
    form = JobForm()
    
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.author = request.user
            job.save()
            messages.success(request, "Job posted successfully!")
            return redirect("job_market")
    
    context = {"form": form}
    return render(request, "opportunities/job_form.html", context)

# 4. UPDATE
@login_required
def update_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if job.author != request.user:
        messages.error(request, "You are not authorized to edit this job.")
        return redirect('job_detail', pk=pk)

    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully!")
            return redirect('job_market') 
    else:
        form = JobForm(instance=job)
            
    context = {"form": form, "title": "Edit Job"}
    return render(request, "opportunities/job_form.html", context)

# 5. DELETE
@login_required
def delete_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if job.author != request.user:
        messages.error(request, "You are not authorized to delete this job.")
        return redirect('job_detail', pk=pk)

    if request.method == "POST":
        job.delete()
        messages.success(request, "Job deleted successfully.")
        return redirect('job_market')

    context = {"item": job}
    return render(request, "opportunities/delete_confirm.html", context)

# 6. Apply Logic
@login_required
def apply_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if job.author == request.user:
         messages.error(request, "You cannot apply to your own job.")
         return redirect('job_market')
         
    # Check if already applied
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect('job_market')

    # RESTRICTION: Employers cannot apply
    if hasattr(request.user, 'profile') and request.user.profile.role == 'employer':
        messages.error(request, "Employers cannot apply for jobs.")
        return redirect('job_market')

    # Create Application
    Application.objects.create(job=job, applicant=request.user)
    
    messages.success(request, f"Application submitted for {job.title}!")
    return redirect('job_market')

# 7. My Jobs
@login_required
def my_jobs(request):
    jobs = Job.objects.filter(author=request.user)
    return render(request, "opportunities/job_list.html", {"jobs": jobs})

@login_required
@premium_required
def toggle_reminder(request, job_id):
    """
    Toggle the reminder status for a user on a specific job.
    """
    from .models import JobReminder
    
    
    job = get_object_or_404(Job, pk=job_id)
    
    # RESTRICTION: Employers cannot set reminders
    if hasattr(request.user, 'profile') and request.user.profile.role == 'employer':
        messages.error(request, "Employers cannot set reminders.")
        # Redirect back to referring page or job market
        return redirect(request.META.get('HTTP_REFERER', 'job_market'))

    # Toggle logic
    reminder, created = JobReminder.objects.get_or_create(user=request.user, job=job)
    
    if not created:
        # If it already existed, delete it (Toggle OFF)
        reminder.delete()
        messages.info(request, f"Reminder removed for '{job.title}'.")
    else:
        # If it was just created (Toggle ON)
        messages.success(request, f"Reminder set! We'll notify you 3 days before the deadline.")
        
    # Redirect back to where they came from, or job market
    next_url = request.META.get('HTTP_REFERER', 'job_market')
    return redirect(next_url)
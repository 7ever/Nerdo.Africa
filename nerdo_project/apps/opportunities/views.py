from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Job
from .forms import JobForm

# Helper to check if user is verified
def is_premium_user(user):
    return user.is_authenticated and user.profile.is_verified

# 1. READ ALL (Market)
def job_market(request):
    jobs = Job.objects.all()
    context = {"jobs": jobs}
    return render(request, "opportunities/job_list.html", context)

# 2. READ ONE (Details)
def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    context = {"job": job}
    return render(request, "opportunities/job_detail.html", context)

# 3. CREATE (Restricted to Premium)
@login_required
@user_passes_test(is_premium_user, login_url='pay_premium', redirect_field_name=None)
def create_job(request):
    form = JobForm()
    
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            # Save without committing to DB yet
            job = form.save(commit=False)
            # Assign the logged-in user as Author
            job.author = request.user
            # Now save
            job.save()
            
            messages.success(request, "Job posted successfully!")
            return redirect("job_market")
    
    context = {"form": form}
    return render(request, "opportunities/job_form.html", context)

# 4. UPDATE (Restricted to Author)
@login_required
def update_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    
    # Security Check
    if job.author != request.user:
        messages.error(request, "You are not authorized to edit this job.")
        return redirect('job_detail', pk=pk)

    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully!")
            return redirect('job_detail', pk=pk)
    else:
        form = JobForm(instance=job)
            
    context = {"form": form, "title": "Edit Job"}
    return render(request, "opportunities/job_form.html", context)

# 5. DELETE (Restricted to Author)
@login_required
def delete_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    
    # Security Check: Only the author can delete
    if job.author != request.user:
        messages.error(request, "You are not authorized to delete this job.")
        return redirect('job_detail', pk=pk)

    if request.method == "POST":
        job.delete()
        messages.success(request, "Job deleted successfully.")
        return redirect('job_market')

    context = {"item": job}
    return render(request, "opportunities/delete_confirm.html", context)
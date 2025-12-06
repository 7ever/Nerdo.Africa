from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Job
from .forms import JobForm

# 1. Define the Check Function
def is_premium_user(user):
    # Returns True if user is verified (Premium), False otherwise
    return user.is_authenticated and user.profile.is_verified

# 2. READ ALL
def job_market(request):
    jobs = Job.objects.all()
    context = {"jobs": jobs}
    return render(request, "opportunities/job_list.html", context)

# 3. READ ONE
def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    context = {"job": job}
    return render(request, "opportunities/job_detail.html", context)

# 4. CREATE (RESTRICTED)
@login_required
@user_passes_test(is_premium_user, login_url='pay_premium', redirect_field_name=None)
def create_job(request):
    """
    Only allows Premium (Verified) users to post jobs.
    Redirects others to the Payment page.
    """
    form = JobForm()
    
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Job posted successfully!")
            return redirect("job_market")
    
    context = {"form": form}
    return render(request, "opportunities/job_form.html", context)
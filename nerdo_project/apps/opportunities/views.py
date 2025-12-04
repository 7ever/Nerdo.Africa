from django.shortcuts import render, redirect, get_object_or_404
from .models import Job
from .forms import JobForm

def job_market(request):
    jobs = Job.objects.all()
    return render(request, 'opportunities/job_list.html', {'jobs': jobs})

def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    return render(request, 'opportunities/job_detail.html', {'job': job})

def create_job(request):
    form = JobForm()
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('job_market')
    return render(request, 'opportunities/job_form.html', {'form': form})
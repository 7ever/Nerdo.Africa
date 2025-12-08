from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .utils import get_youtube_roadmap
from apps.opportunities.models import Job # To reuse categories

@login_required
def learning_home(request):
    # Pass job categories so users can pick what to learn
    categories = Job.CATEGORY_CHOICES
    return render(request, 'learning/home.html', {'categories': categories})

@login_required
def roadmap_view(request):
    # Get the selected skill from the URL (e.g., ?skill=Python)
    skill = request.GET.get('skill', 'Digital Skills')

    # Fetch data from YouTube
    playlists = get_youtube_roadmap(skill)

    context = {
        'skill': skill,
        'playlists': playlists
    }
    return render(request, 'learning/roadmap.html', context)

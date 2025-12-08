from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .utils import generate_complete_roadmap
from .models import LearningPath
from .decorators import premium_required
import logging

logger = logging.getLogger(__name__)

@login_required
@premium_required
def learning_home(request):
    """Home page with search, categories, and learning history"""
    from apps.opportunities.models import Job
    
    # Get popular categories for quick selection
    categories = Job.CATEGORY_CHOICES if hasattr(Job, 'CATEGORY_CHOICES') else []
    
    # Get recent searches (still useful for session-based quick access)
    recent_searches = request.session.get('recent_searches', [])[:5]
    
    # Get User's Learning History (Active Learning Paths)
    learning_paths = LearningPath.objects.filter(user=request.user).order_by('-created_at')[:3]
    
    context = {
        'categories': categories,
        'recent_searches': recent_searches,
        'learning_paths': learning_paths,
        'skill_levels': [
            ('beginner', 'Beginner 👶'),
            ('intermediate', 'Intermediate 🚀'),
            ('advanced', 'Advanced 🏆')
        ],
        'durations': [
            (4, '1 Month (Fast Track)'),
            (8, '2 Months (Standard)'),
            (12, '3 Months (Comprehensive)'),
            (24, '6 Months (Deep Dive)')
        ]
    }
    return render(request, 'learning/home.html', context)

@login_required
@premium_required
def search_roadmap(request):
    """Handle custom topic search"""
    if request.method == 'POST':
        topic = request.POST.get('topic', '').strip()
        skill_level = request.POST.get('skill_level', 'beginner')
        duration = int(request.POST.get('duration', 12))
        
        if not topic:
            messages.error(request, "Please enter a topic to learn")
            return redirect('learning_home')
        
        # Save to recent searches
        recent_searches = request.session.get('recent_searches', [])
        if topic not in recent_searches:
            recent_searches.insert(0, topic)
            request.session['recent_searches'] = recent_searches[:10]  # Keep last 10
            request.session.modified = True
        
        # Check if identical roadmap already exists for this user to avoid duplicates
        existing_path = LearningPath.objects.filter(
            user=request.user, 
            topic__iexact=topic, 
            skill_level=skill_level,
            duration=duration
        ).first()

        if existing_path:
            # Redirect to existing one
            return redirect('roadmap_view_id', path_id=existing_path.id)

        # Redirect to generation view which will create the DB entry
        from django.urls import reverse
        from django.utils.http import urlencode
        
        base_url = reverse('roadmap_view')
        query_string = urlencode({'topic': topic, 'level': skill_level, 'duration': duration})
        url = f"{base_url}?{query_string}"
        
        return redirect(url)
    
    return redirect('learning_home')

@login_required
@premium_required
def roadmap_view(request):
    """Generate and Display roadmap (Creates new DB entry if needed)"""
    # Get parameters
    topic = request.GET.get('topic', '').strip()
    skill_level = request.GET.get('level', 'beginner')
    
    try:
        duration = int(request.GET.get('duration', 12))
    except:
        duration = 12
    
    if not topic:
        messages.warning(request, "No topic specified. Try searching for something!")
        return redirect('learning_home')
        
    # Check if a similar path exists recently (e.g. created/updated in last few minutes? or just exact match)
    # For now, let's look for exact match to prevent re-generation on page refresh if params are same
    existing_path = LearningPath.objects.filter(
        user=request.user, 
        topic__iexact=topic, 
        skill_level=skill_level,
        duration=duration
    ).first()

    if existing_path:
        return render(request, 'learning/roadmap.html', {'roadmap': existing_path, 'roadmap_data': existing_path.roadmap_data})
    
    try:
        # Generate complete roadmap
        roadmap_data = generate_complete_roadmap(topic, skill_level, duration)
        
        # Save to Database
        learning_path = LearningPath.objects.create(
            user=request.user,
            topic=topic,
            skill_level=skill_level,
            duration=duration,
            roadmap_data=roadmap_data
        )
        
        return render(request, 'learning/roadmap.html', {'roadmap': learning_path, 'roadmap_data': roadmap_data})
        
    except Exception as e:
        logger.error(f"Error generating roadmap: {e}")
        messages.error(request, f"Could not generate roadmap. Error: {str(e)}")
        return redirect('learning_home')

@login_required
@premium_required
def roadmap_view_id(request, path_id):
    """View a specific saved roadmap"""
    learning_path = get_object_or_404(LearningPath, id=path_id, user=request.user)
    return render(request, 'learning/roadmap.html', {'roadmap': learning_path, 'roadmap_data': learning_path.roadmap_data})

@login_required
@premium_required
def quick_search(request, topic):
    """Quick search from navbar or recent searches"""
    # Check existing first
    existing = LearningPath.objects.filter(user=request.user, topic__iexact=topic).first()
    if existing:
        return redirect('roadmap_view_id', path_id=existing.id)

    from django.urls import reverse
    url = reverse('roadmap_view') + f'?topic={topic}&level=beginner&duration=12'
    return redirect(url)

@login_required
@premium_required
def learning_history(request):
    """View full learning history"""
    from .models import LearningPath
    
    # Get all paths
    paths_list = LearningPath.objects.filter(user=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(paths_list, 9)  # 9 per page
    page = request.GET.get('page')
    learning_paths = paginator.get_page(page)
    
    return render(request, 'learning/history.html', {'learning_paths': learning_paths})

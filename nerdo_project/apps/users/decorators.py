from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from django.urls import reverse

def premium_required(view_func):
    """
    Decorator to ensure the user has premium access.
    Redirects to payment page if not premium.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # 1. Check if user is authenticated (standard check)
        if not request.user.is_authenticated:
            return redirect('login')
        
        # 2. Check if user has a profile and is premium
        if hasattr(request.user, 'profile') and request.user.profile.is_premium:
            return view_func(request, *args, **kwargs)
        
        # 3. If not premium, redirect to payment with a nice message
        messages.warning(request, "Premium access required for this feature. Please upgrade.")
        
        # Smart Redirect Logic
        failure_url = reverse('pay_premium')
        success_destination = request.path
        # Where to go if they skip (Referer is safer than request.path to avoid loops)
        cancel_destination = request.META.get('HTTP_REFERER', reverse('profile'))
        
        return redirect(f'{failure_url}?next={success_destination}&cancel={cancel_destination}')
        
    return _wrapped_view

def is_verified_employer(user):
    """
    Test function for user_passes_test decorator.
    Checks if the user is authenticated, is an employer, and is verified.
    """
    if not user.is_authenticated:
        return False
    
    if not hasattr(user, 'profile'):
        return False
        
    return user.profile.role == 'employer' and user.profile.is_employer_verified

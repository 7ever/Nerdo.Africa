from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

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
        messages.warning(request, "Premium access required for this feature. Please upgrade to continue learning.")
        return redirect('pay_premium')
        
    return _wrapped_view

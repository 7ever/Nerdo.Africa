import logging
from django.shortcuts import render
from django.conf import settings

logger = logging.getLogger(__name__)

class AIServiceErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_exception(self, request, exception):
        # Handle AI API errors gracefully
        if 'google.generativeai' in str(exception.__class__.__module__):
            logger.error(f"Gemini API Error: {exception}")
            if settings.DEBUG:
                return render(request, 'learning/error.html', {
                    'error': 'AI Service temporarily unavailable',
                    'message': 'Please try again in a few minutes.'
                }, status=503)
        
        return None

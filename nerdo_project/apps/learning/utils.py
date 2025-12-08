import requests
import logging
from django.conf import settings
from django.core.cache import cache
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Configure Gemini AI
try:
    if hasattr(settings, 'GEMINI_API_KEY') and settings.GEMINI_API_KEY:
        genai.configure(api_key=settings.GEMINI_API_KEY)
except Exception as e:
    logger.error(f"Failed to configure Gemini AI: {e}")

def generate_roadmap_topics(user_query, skill_level="beginner", duration_weeks=12):
    """
    Uses Gemini AI to generate structured, practical, project-based learning phases
    from a user's search query, tailored to skill level and duration.
    
    Args:
        user_query (str): User's input like "Learn Python" or "blockchain"
        skill_level (str): Beginner, Intermediate, Advanced
        duration_weeks (int): Total weeks for the course
    
    Returns:
        list: Structured learning topics/phases
    """
    try:
        # Initialize the Gemini model (using flash for speed/cost balance)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Adjust phase count based on skill level
        if skill_level.lower() == 'beginner':
            # Beginners need shorter, less overwhelming roadmaps
            num_phases = min(6, max(3, duration_weeks // 2))
        else:
            num_phases = duration_weeks // 2 if duration_weeks < 8 else 6
        
        # Custom instructions based on skill level
        if skill_level.lower() == 'beginner':
            focus_instruction = """
            1. Focus primarily on "WHAT IS" and FOUNDATIONAL CONCEPTS (e.g., "What is Python?", "Understanding Variables", "How the Blockchain works").
            2. Start with definitions and conceptual understanding before moving to syntax or usage.
            3. Keep topics simple, clear, and easy to digest for an absolute beginner.
            """
        else:
            focus_instruction = """
            1. Make it PRACTICAL and PROJECT-BASED (e.g., "Build a Weather App" instead of "Variables").
            2. Focus on implementation, building, and real-world application.
            """

        # Create a structured prompt that respects the user's parameters
        prompt = f"""You are an expert curriculum designer creating a unique learning path. 
        A student wants to learn about: "{user_query}"
        
        Parameters:
        - Current Skill Level: {skill_level}
        - Available Time: {duration_weeks} weeks
        - Target Phase Count: Roughly {num_phases}
        
        Create a partitioned learning roadmap.
        CRITICAL: 
        {focus_instruction}
        3. Ensure it is UNIQUE to this specific request. 
        4. Each phase MUST be a search-friendly topic for YouTube.

        Format your response EXACTLY as a numbered list:
        1. [Phase Title]
        2. [Phase Title]
        ...

        Requirements:
        - Phases should be 4-8 words long.
        - Include terms like "tutorial", "explained", "course", "crash course" where appropriate.
        - Ensure the progression makes logical sense for a {skill_level}.
        
        Now create the roadmap topics:
        """
        
        # Generate content
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.8, # Increase temperature for uniqueness
                max_output_tokens=500,
            )
        )
        
        # Parse the response
        roadmap_text = response.text.strip()
        
        # Extract numbered lines
        topics = []
        for line in roadmap_text.split('\n'):
            line = line.strip()
            # Remove numbering: "1. " or "1) " or "- "
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove the number and any punctuation
                parts = line.split('.', 1)
                if len(parts) > 1:
                    topic = parts[-1].strip()
                else:
                    # Try splitting by paren if dot failed
                    parts = line.split(')', 1)
                    if len(parts) > 1:
                        topic = parts[-1].strip()
                    else:
                        topic = line.lstrip('-0123456789. )').strip()
                        
                if topic:
                    topics.append(topic)
        
        logger.info(f"Generated {len(topics)} roadmap topics for: {user_query}")
        return topics[:8]  # Cap at 8 phases max
        
    except Exception as e:
        logger.error(f"Gemini AI Error: {e}")
        # Fallback: return a generic structure based on the query
        return [
            f"{user_query} crash course for {skill_level}",
            f"{user_query} practical project tutorial",
            f"Build a real world app with {user_query}",
            f"{user_query} step by step guide",
            f"{user_query} best practices and tips",
        ]



def get_next_api_key():
    """Round-robin API key rotation to handle quota limits"""
    api_keys = getattr(settings, 'YOUTUBE_API_KEYS', [])
    
    # Fallback to single key if list is empty or not defined
    if not api_keys:
        single_key = getattr(settings, 'YOUTUBE_API_KEY', '')
        return single_key if single_key else None
        
    # Filter out None/Empty keys just in case
    valid_keys = [k for k in api_keys if k]
    if not valid_keys:
        return None

    key_index = cache.get('youtube_key_index', 0)
    
    # Safety check if index is out of bounds (e.g. keys removed)
    if key_index >= len(valid_keys):
        key_index = 0
        
    key = valid_keys[key_index]
    
    # Move to next key
    next_index = (key_index + 1) % len(valid_keys)
    cache.set('youtube_key_index', next_index, timeout=None)
    
    return key


def get_youtube_videos_for_topic(topic, max_results=3):
    """
    Fetches YouTube playlists/videos for a specific learning topic.
    
    Args:
        topic (str): A roadmap phase/topic
        max_results (int): Number of results per topic
    
    Returns:
        list: Video/playlist objects
    """
    base_url = "https://www.googleapis.com/youtube/v3/search"
    cache_key = f"yt_search_{topic.replace(' ', '_')}_{max_results}"
    
    # Check cache
    cached = cache.get(cache_key)
    if cached:
        return cached

    # Try each key if quota is exceeded (403)
    max_retries = 3 
    try:
        all_keys = getattr(settings, 'YOUTUBE_API_KEYS', [])
        if all_keys:
            max_retries = len(all_keys)
    except:
        pass

    for attempt in range(max_retries + 1):
        api_key = get_next_api_key()
        if not api_key:
            if attempt == 0:
                logger.warning("No YouTube API Key configured")
            continue
    
        params = {
            'part': 'snippet',
            'q': topic,
            'type': 'video',  # Prioritize videos for better immediate watching
            'videoDuration': 'long', # Prefer in-depth content
            'maxResults': max_results,
            'key': api_key,
            'relevanceLanguage': 'en',
            'order': 'relevance'
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                videos = []
                
                for item in data.get('items', []):
                    # Safely get thumbnails
                    thumbnails = item['snippet'].get('thumbnails', {})
                    thumb_url = thumbnails.get('medium', {}).get('url', 
                                thumbnails.get('default', {}).get('url', ''))

                    videos.append({
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'thumbnail': thumb_url,
                        'video_id': item['id'].get('videoId', ''),
                        'playlist_id': item['id'].get('playlistId', ''),
                        'channel': item['snippet']['channelTitle'],
                        'published_at': item['snippet']['publishedAt'][:10]
                    })
                
                # Cache for 24 hours
                cache.set(cache_key, videos, 86400)
                return videos

            elif response.status_code == 403:
                # Quota exceeded or permission denied, try next key
                logger.warning(f"YouTube API Key {api_key[:5]}... failed (403). Rotating to next key.")
                continue

            else:
                logger.error(f"YouTube API Error: {response.status_code} - {response.text}")
                # For other errors (400, 500), don't retry blindly
                return []
                
        except Exception as e:
            logger.error(f"YouTube Connection Error: {e}")
            if attempt < max_retries:
                continue # Retry network errors too
            return []

    return [] # All retries failed


def generate_complete_roadmap(user_query, skill_level="beginner", duration_weeks=12):
    """
    MAIN FUNCTION: Generates AI-powered roadmap with YouTube videos.
    
    Args:
        user_query (str): What the user wants to learn
        skill_level (str): Difficulty
        duration_weeks (int): Duration
    
    Returns:
        list: List of phase objects compatible with the LearningPath model
    """
    
    # Step 1: Use AI to generate learning phases
    roadmap_topics = generate_roadmap_topics(user_query, skill_level, duration_weeks)
    
    # Step 2: For each phase, fetch YouTube videos
    roadmap_phases = []
    
    for idx, topic in enumerate(roadmap_topics, 1):
        videos = get_youtube_videos_for_topic(topic, max_results=3)
        
        # Estimate duration per phase
        phase_weeks = max(1, duration_weeks // len(roadmap_topics))
        
        roadmap_phases.append({
            'phase_number': idx,
            'phase_title': topic, # Use 'phase_title' to match legacy usage or 'title'
            'title': topic,       # Redundant but safe for template compatibility
            'estimated_duration': f"{phase_weeks} week(s)",
            'videos': videos,
            'search_query': topic
        })
    
    return roadmap_phases

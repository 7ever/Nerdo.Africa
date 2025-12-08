import requests
from django.conf import settings

def get_youtube_roadmap(skill_name):
    """
    Fetches structured playlists for a given skill (e.g., 'Python').
    Returns a list of video/playlist objects.
    """
    api_key = settings.YOUTUBE_API_KEY
    base_url = "https://www.googleapis.com/youtube/v3/search"

    # We search for "playlists" specifically to get full courses
    params = {
        'part': 'snippet',
        'q': f"{skill_name} full course for beginners",
        'type': 'playlist',
        'maxResults': 6,
        'key': api_key,
        'relevanceLanguage': 'en'
    }

    try:
        print(f"--> Fetching Roadmap for: {skill_name}")
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            playlists = []
            for item in data.get('items', []):
                playlists.append({
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                    'playlist_id': item['id']['playlistId'],
                    'channel': item['snippet']['channelTitle']
                })
            return playlists
        else:
            print(f"YouTube API Error: {response.status_code} - {response.text}")
            return []

    except Exception as e:
        print(f"Connection Error: {e}")
        return []

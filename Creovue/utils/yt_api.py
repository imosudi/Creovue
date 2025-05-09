

"""Module: yt_api.py."""
# utils/yt_api.py
import requests
import datetime
import time
import datetime



from Creovue.app_secets import creo_api_key, cre_base_url



def fetch_youtube_analytics(channel_id, days=700):
    """
    Fetches and simulates key YouTube analytics from public statistics.
    """
    print("channel_id: ", channel_id)
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days)

    url = f'{cre_base_url}/channels'
    params = {
        'part': 'statistics',
        'id': channel_id,
        'key': creo_api_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code} - {data.get('error', {}).get('message', '')}")

    if not data.get("items"):
        raise Exception("No channel data returned.")

    stats = data['items'][0]['statistics']
    total_views = int(stats.get("viewCount", 0))
    subscriber_count = int(stats.get("subscriberCount", 0))
    video_count = int(stats.get("videoCount", 1))

    # Simulated analytics based on stats
    avg_watch_time = round((total_views * 3.5) / 1000, 2)  # Simulate 3.5 mins per 1000 views
    engagement_rate = round(min(100, ((subscriber_count / total_views) * 100)), 2)

    # Simulated daily views
    daily_views = [int(total_views / days * (0.9 + 0.2 * i / days)) for i in range(1, days + 1)]

    return {
        "total_views": total_views,
        "subscriber_count": subscriber_count,
        "video_count": video_count,
        "avg_watch_time": avg_watch_time,
        "engagement_rate": engagement_rate,
        "daily_views": daily_views
    }

    


def validate_api_key():
    """
    Simple function to validate if the API key works at all.
    
    Returns:
        bool: True if the API key is valid, False otherwise
    """
    test_url = f"{cre_base_url}/videos"
    params = {
        'part': 'snippet',
        'chart': 'mostPopular',
        'maxResults': 1,
        'key': creo_api_key
    }
    
    response = requests.get(test_url, params=params)
    return response.status_code == 200



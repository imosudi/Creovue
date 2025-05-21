

"""Module: yt_api.py."""
# utils/yt_api.py
import requests
import datetime
import time
import datetime



from Creovue.config import creo_api_key, cre_base_url


import datetime
import requests

def fetch_youtube_analytics(channel_id, days=700, max_videos=10):
    """
    Fetches YouTube analytics including channel stats and a list of recent videos with their view counts,
    and identifies the most viewed video.
    """

    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days)

    # Fetch channel statistics and uploads playlist ID
    url_channel = f'{cre_base_url}/channels'
    params_channel = {
        'part': 'statistics,contentDetails',
        'id': channel_id,
        'key': creo_api_key
    }

    response_channel = requests.get(url_channel, params=params_channel)
    data_channel = response_channel.json()

    if response_channel.status_code != 200:
        raise Exception(f"API Error: {response_channel.status_code} - {data_channel.get('error', {}).get('message', '')}")

    if not data_channel.get("items"):
        raise Exception("No channel data returned.")

    stats = data_channel['items'][0]['statistics']
    content_details = data_channel['items'][0]['contentDetails']
    uploads_playlist_id = content_details['relatedPlaylists']['uploads']

    total_views = int(stats.get("viewCount", 0))
    subscriber_count = int(stats.get("subscriberCount", 0))
    video_count = int(stats.get("videoCount", 1))  # Avoid division by zero

    # Fetch recent videos from uploads playlist
    url_playlist_items = f'{cre_base_url}/playlistItems'
    params_playlist = {
        'part': 'snippet',
        'playlistId': uploads_playlist_id,
        'maxResults': max_videos,
        'key': creo_api_key
    }

    response_playlist = requests.get(url_playlist_items, params=params_playlist)
    data_playlist = response_playlist.json()

    if response_playlist.status_code != 200:
        raise Exception(f"API Error: {response_playlist.status_code} - {data_playlist.get('error', {}).get('message', '')}")

    videos = []
    video_ids = []
    video_items = data_playlist.get("items", [])
    for item in video_items:
        print("video_item: ", item, "\n")
    time.sleep(300)
    for item in data_playlist.get("items", []):
        video_id = item['snippet']['resourceId']['videoId']
        title = item['snippet']['title']
        #video["ctr"] #= round(random.uniform(2, 10), 2)
        #video["impressions"] #= random.randint(5000, 25000)
        #video["retention"] #= round(random.uniform(20, 60), 1)
        video_ids.append(video_id)
        videos.append({'video_id': video_id, 'title': title, 'views': 0})  # placeholder for views
        


    # Fetch video statistics in batch
    if video_ids:
        url_videos = f'{cre_base_url}/videos'
        params_videos = {
            'part': 'statistics',
            'id': ','.join(video_ids),
            'key': creo_api_key
        }
        response_videos = requests.get(url_videos, params=params_videos)
        data_videos = response_videos.json()

        if response_videos.status_code != 200:
            raise Exception(f"API Error: {response_videos.status_code} - {data_videos.get('error', {}).get('message', '')}")

        stats_map = {item['id']: item['statistics'] for item in data_videos.get('items', [])}

        for video in videos:
            vid_stats = stats_map.get(video['video_id'], {})
            video['views'] = int(vid_stats.get('viewCount', 0))

    # Identify the most viewed video
    most_viewed_video = None
    if videos:
        most_viewed_video = max(videos, key=lambda v: v['views'])

    # Simulated analytics based on stats
    avg_watch_time = round((total_views * 3.5) / 1000, 2)  # Simulate 3.5 mins per 1000 views
    engagement_rate = round(min(100, ((subscriber_count / total_views) * 100)) if total_views else 0, 2)

    views_per_video = round(total_views / video_count, 2)
    watch_time_per_video = round(avg_watch_time / video_count, 2)

        


    # Simulated daily views (simple linear growth for demonstration)
    daily_views = [int(total_views / days * (0.9 + 0.2 * i / days)) for i in range(1, days + 1)]

    return {
        "total_views": total_views,
        "subscriber_count": subscriber_count,
        "video_count": video_count,
        "avg_watch_time": avg_watch_time,
        "engagement_rate": engagement_rate,
        "views_per_video": views_per_video,
        "watch_time_per_video": watch_time_per_video,
        "daily_views": daily_views,
        "videos": videos,
        "most_viewed_video": most_viewed_video  # dict with title, views, video_id
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



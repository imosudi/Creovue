

"""Module: yt_api.py."""
# utils/yt_api.py
from flask import session
from flask_security import current_user
import requests
import datetime
import time
import datetime

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

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
        print("video_item: ", item, "\n\n")
    #time.sleep(300)
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
 
def calculate_ctr_metrics(channel_id, days=700):
    """
    Fetches comprehensive CTR metrics, impressions, and retention data for all videos
    in a YouTube channel using the YouTube Analytics API.
    
    Args:
        days (int): Number of days of historical data to retrieve (default: 700)
        
    Returns:
        dict: Dictionary containing CTR metrics, impressions, and retention data for all videos
    """
    # First check if user is authenticated and has credentials
    if not current_user.is_authenticated:
        raise Exception("User not authenticated")
    
    # Get channel_id from the current user
    channel_id = current_user.channel_id
    #print("channel_id: ", channel_id); time.sleep(300)
    if not channel_id:
        # If channel_id is not stored in the user model, fetch it using the credentials
        creds = Credentials(**session['youtube_token'])
        print("creds: ", creds); time.sleep(300)
        response = requests.get(
            'https://www.googleapis.com/youtube/v3/channels',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={'part': 'snippet', 'mine': 'true'}
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch channel ID: {response.status_code}")
            
        channel_data = response.json()
        if not channel_data.get('items'):
            raise Exception("No channels found for this user")
            
        channel_id = channel_data['items'][0]['id']
    else:
        # Use credentials from session
        creds = Credentials(**session['youtube_token'])
    
    # Set up dates for the query
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days)
    
    # Convert dates to strings in YYYY-MM-DD format for the API
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    # Build the YouTube and YouTube Analytics services with session credentials
    youtube = build('youtube', 'v3', credentials=creds)
    youtube_analytics = build('youtubeAnalytics', 'v2', credentials=creds)
    
    # First, get the uploads playlist ID for this channel
    url_channel = f'{cre_base_url}/channels'
    params_channel = {
        'part': 'contentDetails',
        'id': channel_id,
        'key': creo_api_key
    }
    
    response_channel = requests.get(url_channel, params=params_channel)
    data_channel = response_channel.json()
    
    if response_channel.status_code != 200:
        raise Exception(f"API Error: {response_channel.status_code} - {data_channel.get('error', {}).get('message', '')}")
    
    if not data_channel.get("items"):
        raise Exception("No channel data returned.")
    
    content_details = data_channel['items'][0]['contentDetails']
    uploads_playlist_id = content_details['relatedPlaylists']['uploads']
    
    # Fetch all video IDs from the uploads playlist
    video_ids = []
    next_page_token = None
    
    while True:
        url_playlist_items = f'{cre_base_url}/playlistItems'
        params_playlist = {
            'part': 'snippet',
            'playlistId': uploads_playlist_id,
            'maxResults': 50,  # Maximum allowed by the API
            'key': creo_api_key
        }
        
        if next_page_token:
            params_playlist['pageToken'] = next_page_token
        
        response_playlist = requests.get(url_playlist_items, params=params_playlist)
        data_playlist = response_playlist.json()
        
        if response_playlist.status_code != 200:
            raise Exception(f"API Error: {response_playlist.status_code} - {data_playlist.get('error', {}).get('message', '')}")
        
        for item in data_playlist.get("items", []):
            video_id = item['snippet']['resourceId']['videoId']
            video_ids.append(video_id)
        
        next_page_token = data_playlist.get('nextPageToken')
        if not next_page_token:
            break
    
    print(f"Found {len(video_ids)} videos in the channel")
    
    # Process videos in batches to avoid API limits
    batch_size = 25
    video_batches = [video_ids[i:i + batch_size] for i in range(0, len(video_ids), batch_size)]
    
    all_video_data = []
    
    for batch_num, video_batch in enumerate(video_batches):
        print(f"Processing batch {batch_num + 1} of {len(video_batches)}")
        
        # Create a filter string for this batch of videos
        video_filter = ';'.join(video_batch)
        
        try:
            # 1. Get CTR and Impressions metrics
            ctr_response = youtube_analytics.reports().query(
                ids=f'channel=={channel_id}',
                startDate=start_date_str,
                endDate=end_date_str,
                metrics='impressions,impressionClickRate,views',
                dimensions='video',
                filters=f'video=={video_filter}',
                sort='-impressions'
            ).execute()
            
            # 2. Get Retention and Watch Time metrics
            retention_response = youtube_analytics.reports().query(
                ids=f'channel=={channel_id}',
                startDate=start_date_str,
                endDate=end_date_str,
                metrics='averageViewDuration,averageViewPercentage,estimatedMinutesWatched',
                dimensions='video',
                filters=f'video=={video_filter}'
            ).execute()
            
            # 3. Get Engagement metrics
            engagement_response = youtube_analytics.reports().query(
                ids=f'channel=={channel_id}',
                startDate=start_date_str,
                endDate=end_date_str,
                metrics='likes,dislikes,comments,shares,subscribersGained',
                dimensions='video',
                filters=f'video=={video_filter}'
            ).execute()
            
            # Create dictionaries to map videos to their data
            ctr_data = {row[0]: {'impressions': row[1], 'ctr': row[2], 'views': row[3]} 
                        for row in ctr_response.get('rows', [])}
            
            retention_data = {row[0]: {'avgViewDuration': row[1], 'retention': row[2], 'watchTime': row[3]} 
                             for row in retention_response.get('rows', [])}
            
            engagement_data = {row[0]: {'likes': row[1], 'dislikes': row[2], 'comments': row[3], 
                                        'shares': row[4], 'newSubs': row[5]} 
                              for row in engagement_response.get('rows', [])}
            
            # Get video metadata for this batch
            url_videos = f'{cre_base_url}/videos'
            params_videos = {
                'part': 'snippet,statistics,contentDetails',
                'id': ','.join(video_batch),
                'key': creo_api_key
            }
            
            response_videos = requests.get(url_videos, params=params_videos)
            data_videos = response_videos.json()
            
            if response_videos.status_code != 200:
                raise Exception(f"API Error: {response_videos.status_code} - {data_videos.get('error', {}).get('message', '')}")
            
            # Combine all data
            for item in data_videos.get('items', []):
                video_id = item['id']
                
                video_data = {
                    'video_id': video_id,
                    'title': item['snippet']['title'],
                    'publishedAt': item['snippet']['publishedAt'],
                    'duration': item['contentDetails']['duration'],
                    'totalViews': int(item['statistics'].get('viewCount', 0)),
                    'likeCount': int(item['statistics'].get('likeCount', 0)),
                    'dislikeCount': int(item['statistics'].get('dislikeCount', 0)),
                    'commentCount': int(item['statistics'].get('commentCount', 0)),
                    # Add CTR data
                    'impressions': int(ctr_data.get(video_id, {}).get('impressions', 0)),
                    'ctr': float(ctr_data.get(video_id, {}).get('ctr', 0)) * 100,  # Convert to percentage
                    'periodViews': int(ctr_data.get(video_id, {}).get('views', 0)),
                    # Add retention data
                    'avgViewDuration': float(retention_data.get(video_id, {}).get('avgViewDuration', 0)),
                    'retention': float(retention_data.get(video_id, {}).get('retention', 0)),
                    'watchTime': float(retention_data.get(video_id, {}).get('watchTime', 0)),
                    # Add engagement data from period
                    'periodLikes': int(engagement_data.get(video_id, {}).get('likes', 0)),
                    'periodDislikes': int(engagement_data.get(video_id, {}).get('dislikes', 0)),
                    'periodComments': int(engagement_data.get(video_id, {}).get('comments', 0)),
                    'periodShares': int(engagement_data.get(video_id, {}).get('shares', 0)),
                    'newSubscribers': int(engagement_data.get(video_id, {}).get('newSubs', 0))
                }
                
                all_video_data.append(video_data)
            
            # Prevent hitting rate limits
            time.sleep(1)
            
        except HttpError as error:
            #print(f"An error occurred processing batch {batch_num + 1}: {error}")
            # Continue with next batch
            continue
    
    # Sort videos by impressions (descending)
    all_video_data.sort(key=lambda x: x['impressions'], reverse=True)
    
    # Calculate channel-level metrics
    total_impressions = sum(video['impressions'] for video in all_video_data)
    total_views = sum(video['periodViews'] for video in all_video_data)
    total_watch_time = sum(video['watchTime'] for video in all_video_data)
    
    # Calculate overall CTR
    overall_ctr = (total_views / total_impressions * 100) if total_impressions > 0 else 0
    
    # Calculate average retention
    avg_retention = sum(video['retention'] for video in all_video_data) / len(all_video_data) if all_video_data else 0
    
    # Find best performing videos
    best_ctr_video = max(all_video_data, key=lambda x: x['ctr']) if all_video_data else None
    best_retention_video = max(all_video_data, key=lambda x: x['retention']) if all_video_data else None
    most_impressions_video = max(all_video_data, key=lambda x: x['impressions']) if all_video_data else None
    
    return {
        "overall_metrics": {
            "total_impressions": total_impressions,
            "total_views": total_views,
            "overall_ctr": round(overall_ctr, 2),
            "avg_retention": round(avg_retention, 2),
            "total_watch_time": round(total_watch_time, 2)
        },
        "best_performers": {
            "best_ctr_video": best_ctr_video,
            "best_retention_video": best_retention_video,
            "most_impressions_video": most_impressions_video
        },
        "all_videos": all_video_data
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



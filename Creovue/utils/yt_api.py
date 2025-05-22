

"""Module: yt_api.py."""
# utils/yt_api.py
from flask import logging, session
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
import re

def is_valid_video_id(video_id):
    return bool(re.match(r'^[a-zA-Z0-9_-]{11}$', video_id))



def fetch_youtube_analytics(channel_id, days=3700, max_videos=10):
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
 
def calculate_ctr_metrics(channel_id, days):
    """
    Fetches comprehensive CTR metrics, impressions, and retention data for all videos
    in a YouTube channel using the YouTube Analytics API.
    
    Args:
        days (int): Number of days of historical data to retrieve (default: 700)
        
    Returns:
        dict: Dictionary containing CTR metrics, impressions, and retention data for all videos
    """
    # Validate session and token
    if not current_user.is_authenticated:
        raise Exception("User not authenticated")

    if 'youtube_token' not in session:
        raise Exception("YouTube credentials not found in session")

    # Session-based credentials
    creds = Credentials(**session['youtube_token'])

    
    # Get channel_id from the current user
    channel_id = current_user.channel_id
    #print("channel_id: ", channel_id); time.sleep(300)
    
    
    # Set up dates for the query
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days)
    
    # Convert dates to strings in YYYY-MM-DD format for the API
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    print("start_date_str: ", start_date_str, "\n", "end_date_str: ", end_date_str)

    # Calculate date range
    #end_date = datetime.now()
    #start_date = end_date - timedelta(days=days_back)
    #start_date_str = start_date.strftime('%Y-%m-%d')
    #end_date_str = end_date.strftime('%Y-%m-%d')

        

        
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
    #print("data_channel: ",data_channel); time.sleep(300)
    
    if response_channel.status_code != 200:
        raise Exception(f"API Error: {response_channel.status_code} - {data_channel.get('error', {}).get('message', '')}")
    
    if not data_channel.get("items"):
        raise Exception("No channel data returned.")
    
    content_details = data_channel['items'][0]['contentDetails']
    uploads_playlist_id = content_details['relatedPlaylists']['uploads']
    
    #print("uploads_playlist_id: ", uploads_playlist_id); time.sleep(300)

    # Fetch all video IDs from the uploads playlist
    video_ids = []
    next_page_token = None
    
    #if 1==1:
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

        #print("data_playlist: ", data_playlist); time.sleep(300)
        
        if response_playlist.status_code != 200:
            raise Exception(f"API Error: {response_playlist.status_code} - {data_playlist.get('error', {}).get('message', '')}")
        
        for item in data_playlist.get("items", []):
            video_id = item['snippet']['resourceId']['videoId']
            #print("video_id: ", video_id); time.sleep(30)
            video_ids.append(video_id)
        
        next_page_token = data_playlist.get('nextPageToken')
        print("next_page_token: ", next_page_token); #time.sleep(300)
        if not next_page_token:
            break
    
    print(f"Found {len(video_ids)} videos in the channel"); #time.sleep(300)
    
    # Process videos in batches to avoid API limits
    batch_size = 25
    video_batches = [video_ids[i:i + batch_size] for i in range(0, len(video_ids), batch_size)]
    
    all_video_data = []
    
    batch_size = 5
    video_batches = [video_ids[i:i + batch_size] for i in range(0, len(video_ids), batch_size)]
    
    #print("video_batches: ", video_batches); time.sleep(300)
    
    all_video_data = []
    
    """for batch_num, video_batch in enumerate(video_batches):
        print(f"Processing batch {batch_num + 1} of {len(video_batches)}")"""
    print("video_batches: ", video_batches)
    for batch in video_batches:
        #print("batch: ", batch); time.sleep(30)
        # Reduce batch size significantly
        #batch = batch[:3]  # Test with just 3 video IDs

        #print("batch: ", batch); time.sleep(30)
        # Use the simplest filter format
        video_filter = f"video=={';'.join(batch)}"

        print("video_filter: ", video_filter); #time.sleep(30)
        if 1==1:
        #try:
            # Step 1: Get basic video performance metrics
            print(f"Fetching video performance data from {start_date_str} to {end_date_str}")    
            video_performance = youtube_analytics.reports().query(
                    ids=f'channel=={channel_id}',
                    startDate=start_date_str,
                    endDate=end_date_str,
                    metrics='views,estimatedMinutesWatched,averageViewDuration,likes,comments,shares',
                    dimensions='channel,video',
                    sort='-views',  # Sort by views descending
                    maxResults=50   # Limit to top 50 videos
                ).execute()
            

            # Step 2: Get subscriber acquisition data
            print("Fetching subscriber data...")
            subscriber_data = youtube_analytics.reports().query(
                    ids=f'channel=={channel_id}',
                    startDate=start_date_str,
                    endDate=end_date_str,
                    metrics='subscribersGained,subscribersLost',
                    dimensions='video',
                    sort='-subscribersGained',
                    maxResults=50
                ).execute()
            
            try:
                # Step 3: Get traffic source data (if available)
                print("Fetching traffic source data...")   
                traffic_sources = youtube_analytics.reports().query(
                            ids=f'channel=={channel_id}',
                            startDate=start_date_str,
                            endDate=end_date_str,
                            metrics='views',
                            dimensions='insightTrafficSourceType',
                            sort='-views'
                        ).execute()
            except HttpError as e:
                print(f"Traffic source data not available: {e}")
                traffic_sources = None
        
            print("video_performance, subscriber_data, and 3 traffic_sources!"); #time.sleep(300)
            print("video_performance: ", video_performance);
            print("subscriber_data: ", subscriber_data);
            print("traffic_sources: ", traffic_sources); #time.sleep(300)
        
            # Step 4: Process and calculate CTR-like metrics
            ctr_results = process_ctr_data(video_performance, subscriber_data, traffic_sources)
            
            return ctr_results
            
        elif 1==2: ##except HttpError as error:
            #logging.error(f"YouTube Analytics API Error: {error}")
            #raise error
            pass 
        else: #except Exception as e:
            pass
            #logging.error(f"Unexpected error in CTR calculation: {e}")
            #raise e

def process_ctr_data(video_performance, subscriber_data, traffic_sources):
    """
    Process raw YouTube Analytics data to calculate CTR-like metrics.
    """
    
    # Extract video performance data
    video_rows = video_performance.get('rows', [])
    video_headers = video_performance.get('columnHeaders', [])
    
    # Extract subscriber data
    subscriber_rows = subscriber_data.get('rows', [])
    subscriber_headers = subscriber_data.get('columnHeaders', [])
    
    # Debug prints
    print("video_rows: ", video_rows, "video_headers: ", video_headers)
    print("subscriber_rows: ", subscriber_rows, "subscriber_headers: ", subscriber_headers)
    
    # Create lookup dictionaries
    video_metrics = {}
    subscriber_metrics = {}
    
    # Process video performance data
    for row in video_rows:
        video_id = row[0]  # First column is video ID
        video_metrics[video_id] = {
            'views': row[1] if len(row) > 1 else 0,
            'estimatedMinutesWatched': row[2] if len(row) > 2 else 0,
            'averageViewDuration': row[3] if len(row) > 3 else 0,
            'likes': row[4] if len(row) > 4 else 0,
            'comments': row[5] if len(row) > 5 else 0,
            'shares': row[6] if len(row) > 6 else 0
        }
    
    # Process subscriber data
    for row in subscriber_rows:
        video_id = row[0]
        subscriber_metrics[video_id] = {
            'subscribersGained': row[1] if len(row) > 1 else 0,
            'subscribersLost': row[2] if len(row) > 2 else 0
        }
    
    # Calculate CTR-like metrics for each video
    video_ctr_data = []
    all_video_data = []  # For ctr_details structure
    
    for video_id, metrics in video_metrics.items():
        subscriber_data_for_video = subscriber_metrics.get(video_id, {
            'subscribersGained': 0, 
            'subscribersLost': 0
        })
        
        # Calculate various CTR-like ratios
        views = metrics['views']
        likes = metrics['likes']
        comments = metrics['comments']
        shares = metrics['shares']
        subscribers_gained = subscriber_data_for_video['subscribersGained']
        estimated_minutes_watched = metrics['estimatedMinutesWatched']
        avg_duration = metrics['averageViewDuration']
        
        # Engagement CTR: (Total Engagements / Views) * 100
        total_engagements = likes + comments + shares
        engagement_ctr = (total_engagements / views * 100) if views > 0 else 0
        
        # Subscriber CTR: (Subscribers Gained / Views) * 100
        subscriber_ctr = (subscribers_gained / views * 100) if views > 0 else 0
        
        # Like CTR: (Likes / Views) * 100
        like_ctr = (likes / views * 100) if views > 0 else 0
        
        # Comment CTR: (Comments / Views) * 100
        comment_ctr = (comments / views * 100) if views > 0 else 0
        
        # Retention rate (using average view duration)
        # Since we don't have video duration, we'll use estimated duration from watch time
        estimated_total_duration = estimated_minutes_watched * 60 / views if views > 0 else 0
        retention_rate = (avg_duration / estimated_total_duration * 100) if estimated_total_duration > 0 else 0
        
        # For impressions, we'll use views as a proxy since real impressions aren't available
        impressions = views  # This is an approximation
        ctr = engagement_ctr  # Use engagement CTR as our main CTR metric
        
        video_entry = {
            'video_id': video_id,
            'views': views,
            'likes': likes,
            'comments': comments,
            'shares': shares,
            'subscribers_gained': subscribers_gained,
            'total_engagements': total_engagements,
            'engagement_ctr': round(engagement_ctr, 2),
            'subscriber_ctr': round(subscriber_ctr, 4),
            'like_ctr': round(like_ctr, 2),
            'comment_ctr': round(comment_ctr, 2),
            'retention_rate': round(retention_rate, 2),
            'avg_view_duration_seconds': avg_duration,
            'estimated_minutes_watched': estimated_minutes_watched,
            # Additional fields for ctr_details structure
            'impressions': impressions,
            'ctr': round(ctr, 2),
            'watchTime': estimated_minutes_watched,
            'retention': round(retention_rate, 2)
        }
        
        video_ctr_data.append(video_entry)
        all_video_data.append(video_entry)
    
    print("video_ctr_data: ", video_ctr_data)
    
    # Sort by engagement CTR
    video_ctr_data.sort(key=lambda x: x['engagement_ctr'], reverse=True)
    all_video_data.sort(key=lambda x: x['impressions'], reverse=True)
    
    # Calculate overall channel metrics
    total_views = sum(video['views'] for video in video_ctr_data)
    total_engagements = sum(video['total_engagements'] for video in video_ctr_data)
    total_subscribers_gained = sum(video['subscribers_gained'] for video in video_ctr_data)
    
    # Calculate metrics for ctr_details
    total_impressions = sum(video['impressions'] for video in all_video_data)
    total_watch_time = sum(video['watchTime'] for video in all_video_data)
    
    overall_engagement_ctr = (total_engagements / total_views * 100) if total_views > 0 else 0
    overall_subscriber_ctr = (total_subscribers_gained / total_views * 100) if total_views > 0 else 0
    overall_ctr = (total_views / total_impressions * 100) if total_impressions > 0 else 0
    avg_retention = sum(video['retention'] for video in all_video_data) / len(all_video_data) if all_video_data else 0
    
    # Find best performing videos
    best_ctr_video = max(all_video_data, key=lambda x: x['ctr']) if all_video_data else None
    best_retention_video = max(all_video_data, key=lambda x: x['retention']) if all_video_data else None
    most_impressions_video = max(all_video_data, key=lambda x: x['impressions']) if all_video_data else None
    
    # Create ctr_details structure as required
    ctr_details = {
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
    
    return {
        'video_data': video_ctr_data,
        'channel_summary': {
            'total_views': total_views,
            'total_engagements': total_engagements,
            'total_subscribers_gained': total_subscribers_gained,
            'overall_engagement_ctr': round(overall_engagement_ctr, 2),
            'overall_subscriber_ctr': round(overall_subscriber_ctr, 4),
            'top_performing_videos': video_ctr_data[:10]  # Top 10 by engagement CTR
        },
        'ctr_details': ctr_details  # Add the required ctr_details structure
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



# trends.py (Production-ready)
from googleapiclient.discovery import build
from collections import Counter
from datetime import datetime, timedelta
import random

from Creovue.app_secets import creo_api_key
#API_KEY = "YOUR_YOUTUBE_API_KEY"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def get_youtube_client():
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=creo_api_key)

def fetch_trending_keywords(region="US"):
    youtube = get_youtube_client()
    response = youtube.videos().list(
        part="snippet",
        chart="mostPopular",
        regionCode=region,
        maxResults=20
    ).execute()

    keywords = []
    for item in response['items']:
        title = item['snippet']['title']
        keywords.extend(title.lower().split())

    # Count and return top 10 keywords
    counter = Counter(keywords)
    common = counter.most_common(10)
    return [{"name": word, "volume": count * 100} for word, count in common]

def fetch_top_channels(region="US"):
    youtube = get_youtube_client()
    response = youtube.videos().list(
        part="snippet",
        chart="mostPopular",
        regionCode=region,
        maxResults=10
    ).execute()

    channel_ids = list(set(item['snippet']['channelId'] for item in response['items']))
    channels_data = []

    for cid in channel_ids[:5]:
        channel = youtube.channels().list(part="snippet,statistics", id=cid).execute()
        if channel['items']:
            info = channel['items'][0]
            channels_data.append({
                "name": info['snippet']['title'],
                "subscribers": f"{int(info['statistics'].get('subscriberCount', 0)) // 1000}K"
            })
    return channels_data

def get_trend_chart_data():
    # Simulate a trend chart over 7 days using top keyword frequency
    labels = [(datetime.now() - timedelta(days=i)).strftime("%a") for i in reversed(range(7))]
    values = [random.randint(10, 50) for _ in range(7)]  # Replace with analytics API or log data
    return {"labels": labels, "values": values}

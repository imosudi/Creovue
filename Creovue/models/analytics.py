

"""Module: analytics.py."""
# models/analytics.py
import time

from Creovue.utils.yt_api import fetch_youtube_analytics
from Creovue.ml.predictor import generate_plot, sudden_spike

def process_channel_analytics_(channel_id):
    # Fetch actual stats with simulated daily views
    full_data = fetch_youtube_analytics(channel_id, days=7)

    view_history = full_data["daily_views"]
    plot_url = generate_plot(list(range(len(view_history))), view_history)
    spike = sudden_spike(view_history)

    return {
        'subscribers': int(full_data.get('subscriber_count', 0)),
        'views': int(full_data.get('total_views', 0)),
        'videos': int(full_data.get('video_count', 0)),
        'spike_detected': spike,
        'plot_url': plot_url
    }

def process_channel_analytics(channel_id):
    full_data = fetch_youtube_analytics(channel_id, days=7)

    view_history = full_data["daily_views"][-7:]  # last 7 days
    spike = sudden_spike(view_history)
    plot_url = generate_plot(list(range(len(view_history))), view_history)

    avg_views_per_video = 0
    if full_data.get("video_count", 0) > 0:
        avg_views_per_video = round(full_data["total_views"] / full_data["video_count"], 2)

    # Prepare chart data for frontend Chart.js
    from datetime import datetime, timedelta
    labels = [(datetime.today() - timedelta(days=i)).strftime('%a') for i in reversed(range(7))]

    chart_data = {
        "labels": labels,
        "values": view_history,
        'plot_url': plot_url
    }

    return {
        'subscribers': int(full_data.get('subscriber_count', 0)),
        'views': int(full_data.get('total_views', 0)),
        'videos': int(full_data.get('video_count', 0)),
        'avg_watch_time': full_data.get('avg_watch_time', 0),
        'engagement_rate': full_data.get('engagement_rate', 0),
        'avg_views_per_video': avg_views_per_video,
        'spike_detected': spike,
        'chart_data': chart_data,
        'plot_url': plot_url
    }

def get_channel_stats(channel_id):
    raw_stats = fetch_youtube_analytics(channel_id)
    return {
        'subscribers': int(raw_stats.get('subscriberCount', 0)),
        'views': int(raw_stats.get('viewCount', 0)),
        'videos': int(raw_stats.get('videoCount', 0))
    }


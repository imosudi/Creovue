

"""Module: analytics.py."""
# models/analytics.py
import time

from app.utils.yt_api import fetch_youtube_analytics
from app.ml.predictor import generate_plot, sudden_spike

def process_channel_analytics(channel_id):
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


def get_channel_stats(channel_id):
    raw_stats = fetch_youtube_analytics(channel_id)
    return {
        'subscribers': int(raw_stats.get('subscriberCount', 0)),
        'views': int(raw_stats.get('viewCount', 0)),
        'videos': int(raw_stats.get('videoCount', 0))
    }


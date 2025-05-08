"""Module: analytics.py."""
# models/analytics.py
import time
from Creovue.utils.yt_api  import fetch_youtube_analytics

# models/analytics.py
from Creovue.ml.predictor import generate_plot, sudden_spike

def process_channel_analytics(channel_id, view_history):
    #print(channel_id, view_history); #time.sleep(300)
    stats = get_channel_stats(channel_id)
    plot_url = generate_plot(list(range(len(view_history))), view_history)
    #print(plot_url); #time.sleep(300)
    spike = sudden_spike(view_history)
    stats['spike_detected'] = spike
    stats['plot_url'] = plot_url

    return stats


def get_channel_stats(channel_id):
    raw_stats = fetch_youtube_analytics(channel_id)
    return {
        'subscribers': int(raw_stats.get('subscriberCount', 0)),
        'views': int(raw_stats.get('viewCount', 0)),
        'videos': int(raw_stats.get('videoCount', 0))
    }


'''def fetch_youtube_analytics(channel_id):
    return {
        "total_views": 125000,
        "avg_watch_time": 6.2,
        "engagement_rate": 8.3
    }'''

'''def generate_plot():
    # Simulated view counts for the past 7 days
    return {
        "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "values": [18000, 22000, 24000, 20000, 26000, 23000, 21000]
    }'''

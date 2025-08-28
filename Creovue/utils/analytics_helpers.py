# utils/analytics_helpers.py
import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

print("Inside Analytics helper 1")

#from Creovue.helper_funcrions import get_health_recommendations
from Creovue.helper_funcrions import get_health_recommendations

print("Inside Analytics helper 2")

from Creovue.models.analytics import get_channel_stats

print("Inside Analytics helper 3")
from Creovue.utils.youtube_client import get_recent_video_performance, calculate_subscriber_trend, calculate_view_trend, calculate_subscriber_growth_rate, calculate_view_growth_rate, calculate_avg_engagement_rate, calculate_upload_consistency

def get_channel_health_overview(channel_id):
    """Get comprehensive channel health data"""
    try:
        # Fetch basic channel stats
        channel_stats = get_channel_stats(channel_id)
        
        # Calculate health metrics
        health_score = calculate_channel_health_score(channel_id)
        
        # Get recent performance data
        recent_videos = get_recent_video_performance(channel_id, days=30)
        
        # Calculate trends
        subscriber_trend = calculate_subscriber_trend(channel_id)
        view_trend = calculate_view_trend(channel_id)
        
        return {
            'health_score': health_score,
            'subscriber_count': channel_stats.get('subscriber_count', 0),
            'total_views': channel_stats.get('total_views', 0),
            'video_count': channel_stats.get('video_count', 0),
            'subscriber_trend': subscriber_trend,
            'view_trend': view_trend,
            'recent_videos': recent_videos,
            'upload_consistency': calculate_upload_consistency(channel_id),
            'engagement_rate': calculate_avg_engagement_rate(channel_id),
            'recommendations': get_health_recommendations(channel_id)
        }
    except Exception as e:
        print(f"Error in get_channel_health_overview: {e}")
        return None

def calculate_channel_health_score(channel_id):
    """Calculate overall channel health score (0-100)"""
    try:
        score = 0
        max_score = 100
        
        # Subscriber growth (25 points)
        subscriber_growth = calculate_subscriber_growth_rate(channel_id)
        if subscriber_growth > 0.1:  # 10% monthly growth
            score += 25
        elif subscriber_growth > 0.05:  # 5% monthly growth
            score += 15
        elif subscriber_growth > 0:
            score += 10
        
        # View growth (25 points)
        view_growth = calculate_view_growth_rate(channel_id)
        if view_growth > 0.2:  # 20% monthly growth
            score += 25
        elif view_growth > 0.1:  # 10% monthly growth
            score += 15
        elif view_growth > 0:
            score += 10
        
        # Engagement rate (25 points)
        engagement_rate = calculate_avg_engagement_rate(channel_id)
        if engagement_rate > 0.05:  # 5% engagement
            score += 25
        elif engagement_rate > 0.03:  # 3% engagement
            score += 15
        elif engagement_rate > 0.01:  # 1% engagement
            score += 10
        
        # Upload consistency (25 points)
        consistency = calculate_upload_consistency(channel_id)
        if consistency > 0.8:  # Very consistent
            score += 25
        elif consistency > 0.6:  # Moderately consistent
            score += 15
        elif consistency > 0.4:  # Somewhat consistent
            score += 10
    except:
        pass

        return min(score, max_score)
    
def get_channel_health_overview(channel_id):
    """Get comprehensive channel health data"""
    try:
        # Fetch basic channel stats
        channel_stats = get_channel_stats(channel_id)
        
        # Calculate health metrics
        health_score = calculate_channel_health_score(channel_id)
        
        # Get recent performance data
        recent_videos = get_recent_video_performance(channel_id, days=30)
        
        # Calculate trends
        subscriber_trend = calculate_subscriber_trend(channel_id)
        view_trend = calculate_view_trend(channel_id)
        
        return {
            'health_score': health_score,
            'subscriber_count': channel_stats.get('subscriber_count', 0),
            'total_views': channel_stats.get('total_views', 0),
            'video_count': channel_stats.get('video_count', 0),
            'subscriber_trend': subscriber_trend,
            'view_trend': view_trend,
            'recent_videos': recent_videos,
            'upload_consistency': calculate_upload_consistency(channel_id),
            'engagement_rate': calculate_avg_engagement_rate(channel_id),
            'recommendations': get_health_recommendations(channel_id)
        }
    except Exception as e:
        print(f"Error in get_channel_health_overview: {e}")
        return None

def calculate_channel_health_score(channel_id):
    """Calculate overall channel health score (0-100)"""
    try:
        score = 0
        max_score = 100
        
        # Subscriber growth (25 points)
        subscriber_growth = calculate_subscriber_growth_rate(channel_id)
        if subscriber_growth > 0.1:  # 10% monthly growth
            score += 25
        elif subscriber_growth > 0.05:  # 5% monthly growth
            score += 15
        elif subscriber_growth > 0:
            score += 10
        
        # View growth (25 points)
        view_growth = calculate_view_growth_rate(channel_id)
        if view_growth > 0.2:  # 20% monthly growth
            score += 25
        elif view_growth > 0.1:  # 10% monthly growth
            score += 15
        elif view_growth > 0:
            score += 10
        
        # Engagement rate (25 points)
        engagement_rate = calculate_avg_engagement_rate(channel_id)
        if engagement_rate > 0.05:  # 5% engagement
            score += 25
        elif engagement_rate > 0.03:  # 3% engagement
            score += 15
        elif engagement_rate > 0.01:  # 1% engagement
            score += 10
        
        # Upload consistency (25 points)
        consistency = calculate_upload_consistency(channel_id)
        if consistency > 0.8:  # Very consistent
            score += 25
        elif consistency > 0.6:  # Moderately consistent
            score += 15
        elif consistency > 0.4:  # Somewhat consistent
            score += 10
    except:
        pass

        return min(score, max_score)    
    
def create_performance_alert(channel_id, alert_type, threshold):
    """Create a new performance alert"""
    try:
        # Stub: Save alert to database
        alert = {
            'channel_id': channel_id,
            'alert_type': alert_type,
            'threshold': threshold,
            'created_at': datetime.now().isoformat(),
            'active': True
        }
        # In real implementation, save to DB and return the saved object
        return alert
    except Exception as e:
        print(f"Error creating performance alert: {e}")
        return None 

def get_notification_preferences(user_id):
    """Get user notification preferences"""
    try:
        # Stub: Fetch from database
        preferences = {
            'email_alerts': True,
            'sms_alerts': False,
            'push_notifications': True
        }
        return preferences
    except Exception as e:
        print(f"Error fetching notification preferences: {e}")
        return None 

def update_user_notification_preferences(user_id, preferences):
    """Update user notification preferences"""
    try:
        # Stub: Update in database
        # In real implementation, save to DB and return updated preferences
        return preferences
    except Exception as e:
        print(f"Error updating notification preferences: {e}")
        return None         
    
def export_analytics_data(user_id, export_type, format_type='csv'):
    """Export analytics data in various formats"""
    try:
        # Stub: Generate export data
        data = {
            'user_id': user_id,
            'export_type': export_type,
            'format': format_type,
            'data': []  # Replace with actual data
        }
        # In real implementation, generate file and return download link
        return data
    except Exception as e:
        print(f"Error exporting analytics data: {e}")
        return None

print("Exiting Analytics helper ")
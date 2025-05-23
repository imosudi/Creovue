# utils/youtube_api_integrations.py
from flask_security import current_user
import requests
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from flask import session
import json

from Creovue import db
from Creovue.models.audience import Goal 
from Creovue.config import creo_api_key

def get_youtube_credentials():
    """Get YouTube API credentials from session"""
    if 'youtube_token' not in session:
        return None
    return Credentials(**session['youtube_token'])

def fetch_video_analytics_detailed(video_id):
    """Fetch detailed analytics for a specific video"""
    try:
        creds = get_youtube_credentials()
        if not creds:
            return None
        
        # Get video statistics
        stats_response = requests.get(
            'https://www.googleapis.com/youtube/v3/videos',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'part': 'statistics,snippet,contentDetails',
                'id': video_id
            }
        )
        
        stats_data = stats_response.json()
        if not stats_data.get('items'):
            return None
        
        video_data = stats_data['items'][0]
        
        return {
            'video_id': video_id,
            'title': video_data['snippet']['title'],
            'views': int(video_data['statistics'].get('viewCount', 0)),
            'likes': int(video_data['statistics'].get('likeCount', 0)),
            'dislikes': int(video_data['statistics'].get('dislikeCount', 0)),
            'comments': int(video_data['statistics'].get('commentCount', 0)),
            'duration': video_data['contentDetails']['duration'],
            'published_at': video_data['snippet']['publishedAt']
        }
    except Exception as e:
        print(f"Error fetching video analytics: {e}")
        return None

def get_video_retention_data(video_id):
    """Get audience retention data for a video"""
    try:
        creds = get_youtube_credentials()
        if not creds:
            return None
        
        # YouTube Analytics API call for retention data
        # Note: This requires YouTube Analytics API access
        analytics_response = requests.get(
            'https://youtubeanalytics.googleapis.com/v2/reports',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'ids': 'channel==MINE',
                'startDate': '2023-01-01',
                'endDate': datetime.now().strftime('%Y-%m-%d'),
                'metrics': 'audienceRetentionPercentage',
                'dimensions': 'elapsedVideoTimeRatio',
                'filters': f'video=={video_id}'
            }
        )
        
        if analytics_response.status_code == 200:
            data = analytics_response.json()
            return data.get('rows', [])
        return []
    except Exception as e:
        print(f"Error fetching retention data: {e}")
        return []

def get_video_traffic_sources(video_id):
    """Get traffic sources for a video"""
    try:
        creds = get_youtube_credentials()
        if not creds:
            return {}
        
        # YouTube Analytics API call for traffic sources
        analytics_response = requests.get(
            'https://youtubeanalytics.googleapis.com/v2/reports',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'ids': 'channel==MINE',
                'startDate': '2023-01-01',
                'endDate': datetime.now().strftime('%Y-%m-%d'),
                'metrics': 'views',
                'dimensions': 'trafficSourceType',
                'filters': f'video=={video_id}',
                'sort': '-views'
            }
        )
        
        if analytics_response.status_code == 200:
            data = analytics_response.json()
            traffic_sources = {}
            for row in data.get('rows', []):
                traffic_sources[row[0]] = row[1]
            return traffic_sources
        return {}
    except Exception as e:
        print(f"Error fetching traffic sources: {e}")
        return {}

def get_video_demographics(video_id):
    """Get demographic data for a video"""
    try:
        creds = get_youtube_credentials()
        if not creds:
            return {}
        
        # Age demographics
        age_response = requests.get(
            'https://youtubeanalytics.googleapis.com/v2/reports',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'ids': 'channel==MINE',
                'startDate': '2023-01-01',
                'endDate': datetime.now().strftime('%Y-%m-%d'),
                'metrics': 'viewerPercentage',
                'dimensions': 'ageGroup',
                'filters': f'video=={video_id}'
            }
        )
        
        # Gender demographics
        gender_response = requests.get(
            'https://youtubeanalytics.googleapis.com/v2/reports',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'ids': 'channel==MINE',
                'startDate': '2023-01-01',
                'endDate': datetime.now().strftime('%Y-%m-%d'),
                'metrics': 'viewerPercentage',
                'dimensions': 'gender',
                'filters': f'video=={video_id}'
            }
        )
        
        demographics = {}
        
        if age_response.status_code == 200:
            age_data = age_response.json()
            demographics['age_groups'] = {row[0]: row[1] for row in age_data.get('rows', [])}
        
        if gender_response.status_code == 200:
            gender_data = gender_response.json()
            demographics['gender'] = {row[0]: row[1] for row in gender_data.get('rows', [])}
        
        return demographics
    except Exception as e:
        print(f"Error fetching audience demographics: {e}")
        return {}

def get_audience_geography(channel_id):
    """Get geographic distribution of audience"""
    try:
        creds = get_youtube_credentials()
        if not creds:
            return {}
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        # Country-wise data
        country_response = requests.get(
            'https://youtubeanalytics.googleapis.com/v2/reports',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'ids': 'channel==MINE',
                'startDate': start_date,
                'endDate': end_date,
                'metrics': 'views,watchTimeMinutes',
                'dimensions': 'country',
                'sort': '-views',
                'maxResults': 20
            }
        )
        
        geography = {
            'countries': {},
            'top_countries': [],
            'last_updated': datetime.now().isoformat()
        }
        
        if country_response.status_code == 200:
            country_data = country_response.json()
            for row in country_data.get('rows', []):
                country_code = row[0]
                views = row[1]
                watch_time = row[2]
                geography['countries'][country_code] = {
                    'views': views,
                    'watch_time_minutes': watch_time
                }
            
            # Sort by views for top countries
            geography['top_countries'] = sorted(
                geography['countries'].items(),
                key=lambda x: x[1]['views'],
                reverse=True
            )[:10]
        
        return geography
    except Exception as e:
        print(f"Error fetching audience geography: {e}")
        return {}

def get_audience_devices(channel_id):
    """Get device usage data for audience"""
    try:
        creds = get_youtube_credentials()
        if not creds:
            return {}
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        # Device type data
        device_response = requests.get(
            'https://youtubeanalytics.googleapis.com/v2/reports',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'ids': 'channel==MINE',
                'startDate': start_date,
                'endDate': end_date,
                'metrics': 'views,watchTimeMinutes',
                'dimensions': 'deviceType'
            }
        )
        
        devices = {
            'device_types': {},
            'last_updated': datetime.now().isoformat()
        }
        
        if device_response.status_code == 200:
            device_data = device_response.json()
            total_views = sum(row[1] for row in device_data.get('rows', []))
            
            for row in device_data.get('rows', []):
                device_type = row[0]
                views = row[1]
                watch_time = row[2]
                percentage = (views / total_views * 100) if total_views > 0 else 0
                
                devices['device_types'][device_type] = {
                    'views': views,
                    'watch_time_minutes': watch_time,
                    'percentage': round(percentage, 2)
                }
        
        return devices
    except Exception as e:
        print(f"Error fetching device data: {e}")
        return {}

def analyze_viewing_patterns(channel_id):
    """Analyze when audience watches videos"""
    try:
        creds = get_youtube_credentials()
        if not creds:
            return {}
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        # Get hourly viewing data
        hourly_response = requests.get(
            'https://youtubeanalytics.googleapis.com/v2/reports',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'ids': 'channel==MINE',
                'startDate': start_date,
                'endDate': end_date,
                'metrics': 'views',
                'dimensions': 'hour'
            }
        )
        
        # Get daily viewing data
        daily_response = requests.get(
            'https://youtubeanalytics.googleapis.com/v2/reports',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'ids': 'channel==MINE',
                'startDate': start_date,
                'endDate': end_date,
                'metrics': 'views',
                'dimensions': 'day'
            }
        )
        
        patterns = {
            'hourly': {},
            'daily': {},
            'peak_hours': [],
            'peak_days': []
        }
        
        if hourly_response.status_code == 200:
            hourly_data = hourly_response.json()
            for row in hourly_data.get('rows', []):
                hour = row[0]
                views = row[1]
                patterns['hourly'][hour] = views
            
            # Find peak hours
            patterns['peak_hours'] = sorted(
                patterns['hourly'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        
        if daily_response.status_code == 200:
            daily_data = daily_response.json()
            for row in daily_data.get('rows', []):
                day = row[0]
                views = row[1]
                patterns['daily'][day] = views
            
            # Find peak days
            patterns['peak_days'] = sorted(
                patterns['daily'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
        
        return patterns
    except Exception as e:
        print(f"Error analyzing viewing patterns: {e}")
        return {}

def analyze_engagement_patterns(channel_id):
    """Analyze audience engagement patterns"""
    try:
        # Get recent videos with engagement data
        recent_videos = VideoPerformance.query.filter_by(
            user_id=current_user.id
        ).order_by(VideoPerformance.upload_date.desc()).limit(20).all()
        
        if not recent_videos:
            return {}
        
        # Analyze engagement by day of week
        day_engagement = defaultdict(list)
        hour_engagement = defaultdict(list)
        
        for video in recent_videos:
            if video.upload_date and video.engagement_rate:
                day = video.upload_date.strftime('%A')
                hour = video.upload_date.hour
                
                day_engagement[day].append(video.engagement_rate)
                hour_engagement[hour].append(video.engagement_rate)
        
        # Calculate averages
        avg_day_engagement = {}
        for day, rates in day_engagement.items():
            avg_day_engagement[day] = sum(rates) / len(rates) if rates else 0
        
        avg_hour_engagement = {}
        for hour, rates in hour_engagement.items():
            avg_hour_engagement[hour] = sum(rates) / len(rates) if rates else 0
        
        # Find best engagement times
        best_day = max(avg_day_engagement.items(), key=lambda x: x[1]) if avg_day_engagement else ('Monday', 0)
        best_hour = max(avg_hour_engagement.items(), key=lambda x: x[1]) if avg_hour_engagement else (12, 0)
        
        return {
            'day_patterns': avg_day_engagement,
            'hour_patterns': avg_hour_engagement,
            'best_day': {'day': best_day[0], 'engagement_rate': best_day[1]},
            'best_hour': {'hour': best_hour[0], 'engagement_rate': best_hour[1]},
            'analysis_based_on': len(recent_videos)
        }
    except Exception as e:
        print(f"Error analyzing engagement patterns: {e}")
        return {}

def get_trending_topics(category):
    """Get trending topics for a category"""
    try:
        # Use Google Trends API or YouTube Trends
        # This is a simplified version - you'd integrate with actual trends API
        trending_topics = [
            {'keyword': 'AI tutorial', 'search_volume': 50000, 'competition': 'medium'},
            {'keyword': 'productivity tips', 'search_volume': 30000, 'competition': 'high'},
            {'keyword': 'beginner guide', 'search_volume': 25000, 'competition': 'low'},
            {'keyword': 'best practices', 'search_volume': 20000, 'competition': 'medium'},
            {'keyword': 'how to start', 'search_volume': 15000, 'competition': 'low'}
        ]
        
        return trending_topics
    except Exception as e:
        print(f"Error getting trending topics: {e}")
        return []

def get_top_performing_videos(channel_id, limit=10):
    """Get top performing videos for the channel"""
    try:
        top_videos = VideoPerformance.query.filter_by(
            user_id=current_user.id
        ).order_by(VideoPerformance.views.desc()).limit(limit).all()
        
        return [{
            'video_id': video.video_id,
            'title': video.title,
            'views': video.views,
            'engagement_rate': video.engagement_rate,
            'upload_date': video.upload_date.isoformat() if video.upload_date else None
        } for video in top_videos]
    except Exception as e:
        print(f"Error getting top videos: {e}")
        return []

def get_content_keywords(category, target_audience):
    """Get keyword suggestions for content"""
    try:
        # This would integrate with keyword research tools
        # Simplified version for demonstration
        keywords = {
            'general': ['tutorial', 'guide', 'tips', 'how to', 'best'],
            'beginner': ['beginner', 'start', 'basics', 'introduction', 'learn'],
            'advanced': ['advanced', 'pro', 'expert', 'master', 'deep dive']
        }
        
        return keywords.get(target_audience, keywords['general'])
    except Exception as e:
        print(f"Error getting content keywords: {e}")
        return []

def get_keyword_search_volume(keyword):
    """Get search volume for a keyword"""
    try:
        # This would integrate with keyword research APIs
        # Simplified version returning random values
        import random
        return random.randint(1000, 50000)
    except Exception as e:
        print(f"Error getting search volume: {e}")
        return 0

def get_keyword_competition(keyword):
    """Get competition level for a keyword"""
    try:
        # This would integrate with keyword research APIs
        # Simplified version returning random values
        import random
        return random.choice(['low', 'medium', 'high'])
    except Exception as e:
        print(f"Error getting competition: {e}")
        return 'medium'

# Competitor Analysis Functions
def get_user_competitors(user_id):
    """Get list of competitors for a user"""
    try:
        competitors = CompetitorAnalysis.query.filter_by(
            user_id=user_id,
            is_active=True
        ).order_by(CompetitorAnalysis.last_analyzed.desc()).all()
        
        return [{
            'id': comp.id,
            'channel_id': comp.competitor_channel_id,
            'name': comp.competitor_name,
            'subscriber_count': comp.subscriber_count,
            'avg_views': comp.avg_views,
            'engagement_rate': comp.engagement_rate,
            'last_analyzed': comp.last_analyzed.isoformat() if comp.last_analyzed else None
        } for comp in competitors]
    except Exception as e:
        print(f"Error getting competitors: {e}")
        return []

def add_competitor_tracking(user_id, competitor_channel):
    """Add a competitor for tracking"""
    try:
        # Extract channel ID from URL if needed
        channel_id = extract_channel_id(competitor_channel)
        
        # Get competitor info
        competitor_info = get_channel_info(channel_id)
        
        # Check if already tracking
        existing = CompetitorAnalysis.query.filter_by(
            user_id=user_id,
            competitor_channel_id=channel_id
        ).first()
        
        if existing:
            existing.is_active = True
            db.session.commit()
            return existing
        
        # Create new competitor tracking
        competitor = CompetitorAnalysis(
            user_id=user_id,
            competitor_channel_id=channel_id,
            competitor_name=competitor_info.get('name', 'Unknown'),
            subscriber_count=competitor_info.get('subscriber_count', 0),
            avg_views=competitor_info.get('avg_views', 0),
            engagement_rate=competitor_info.get('engagement_rate', 0)
        )
        
        db.session.add(competitor)
        db.session.commit()
        
        return competitor
    except Exception as e:
        print(f"Error adding competitor: {e}")
        return None

def analyse_competitor(competitor_id, user_channel_id):
    """Analyze competitor performance"""
    try:
        competitor = CompetitorAnalysis.query.get(competitor_id)
        if not competitor:
            return None
        
        # Get competitor's recent videos
        competitor_videos = get_competitor_videos(competitor.competitor_channel_id)
        
        # Get user's recent videos for comparison
        user_videos = get_top_performing_videos(user_channel_id, limit=10)
        
        # Calculate comparison metrics
        comparison = {
            'subscriber_difference': competitor.subscriber_count - get_user_subscriber_count(user_channel_id),
            'avg_views_difference': competitor.avg_views - calculate_user_avg_views(user_channel_id),
            'engagement_difference': competitor.engagement_rate - calculate_user_avg_engagement(user_channel_id),
            'content_analysis': analyse_competitor_content(competitor_videos),
            'opportunity_keywords': find_competitor_keywords(competitor_videos)
        }
        
        return {
            'competitor': competitor,
            'recent_videos': competitor_videos,
            'comparison': comparison,
            'recommendations': generate_competitor_recommendations(comparison)
        }
    except Exception as e:
        print(f"Error analyzing competitor: {e}")
        return None

def get_competitor_benchmarks(user_id, timeframe='30d'):
    """Compare performance against all tracked competitors"""
    try:
        competitors = get_user_competitors(user_id)
        user_metrics = get_user_metrics(user_id, timeframe)
        
        benchmarks = {
            'user_metrics': user_metrics,
            'competitor_metrics': [],
            'rankings': {},
            'opportunities': []
        }
        
        for competitor in competitors:
            comp_metrics = get_competitor_metrics(competitor['channel_id'], timeframe)
            benchmarks['competitor_metrics'].append({
                'name': competitor['name'],
                'metrics': comp_metrics
            })
        
        # Calculate rankings
        all_channels = [user_metrics] + [comp['metrics'] for comp in benchmarks['competitor_metrics']]
        
        for metric in ['subscriber_count', 'avg_views', 'engagement_rate']:
            sorted_channels = sorted(all_channels, key=lambda x: x.get(metric, 0), reverse=True)
            user_rank = next((i+1 for i, ch in enumerate(sorted_channels) if ch == user_metrics), len(sorted_channels))
            benchmarks['rankings'][metric] = {
                'rank': user_rank,
                'total': len(sorted_channels),
                'percentile': round((1 - (user_rank-1)/len(sorted_channels)) * 100, 1)
            }
        
        return benchmarks
    except Exception as e:
        print(f"Error getting benchmarks: {e}")
        return {}

# Alert and Notification Functions
def get_user_alerts(user_id):
    """Get all alerts for a user"""
    try:
        alerts = Alert.query.filter_by(user_id=user_id).order_by(Alert.created_at.desc()).all()
        
        return [{
            'id': alert.id,
            'type': alert.alert_type,
            'condition': json.loads(alert.condition),
            'is_active': alert.is_active,
            'last_triggered': alert.last_triggered.isoformat() if alert.last_triggered else None,
            'created_at': alert.created_at.isoformat()
        } for alert in alerts]
    except Exception as e:
        print(f"Error getting alerts: {e}")
        return []

def create_performance_alert(user_id, alert_data):
    """Create a new performance alert"""
    try:
        alert = Alert(
            user_id=user_id,
            alert_type=alert_data['type'],
            condition=json.dumps(alert_data['condition'])
        )
        
        db.session.add(alert)
        db.session.commit()
        
        return alert
    except Exception as e:
        print(f"Error creating alert: {e}")
        return None

def toggle_alert_status(alert_id, user_id):
    """Toggle alert on/off"""
    try:
        alert = Alert.query.filter_by(id=alert_id, user_id=user_id).first()
        if alert:
            alert.is_active = not alert.is_active
            db.session.commit()
            return alert
        return None
    except Exception as e:
        print(f"Error toggling alert: {e}")
        return None

# Goal Tracking Functions
def get_user_goals(user_id):
    """Get all goals for a user"""
    try:
        goals = Goal.query.filter_by(user_id=user_id).order_by(Goal.created_at.desc()).all()
        
        return [{
            'id': goal.id,
            'type': goal.goal_type,
            'target_value': goal.target_value,
            'current_value': goal.current_value,
            'progress_percentage': round((goal.current_value / goal.target_value * 100), 2) if goal.target_value > 0 else 0,
            'target_date': goal.target_date.isoformat() if goal.target_date else None,
            'status': goal.status,
            'created_at': goal.created_at.isoformat()
        } for goal in goals]
    except Exception as e:
        print(f"Error getting goals: {e}")
        return []

def create_user_goal(user_id, goal_data):
    """Create a new goal"""
    try:
        goal = Goal(
            user_id=user_id,
            goal_type=goal_data['type'],
            target_value=goal_data['target_value'],
            target_date=datetime.fromisoformat(goal_data['target_date']) if goal_data.get('target_date') else None
        )
        
        db.session.add(goal)
        db.session.commit()
        
        return goal
    except Exception as e:
        print(f"Error creating goal: {e}")
        return None

def calculate_goal_progress(goal_id, user_id):
    """Calculate progress for a specific goal"""
    try:
        goal = Goal.query.filter_by(id=goal_id, user_id=user_id).first()
        if not goal:
            return None
        
        # Update current value based on goal type
        if goal.goal_type == 'subscribers':
            current_value = get_user_subscriber_count(current_user.channel_id)
        elif goal.goal_type == 'views':
            current_value = get_user_total_views(current_user.channel_id)
        elif goal.goal_type == 'videos':
            current_value = get_user_video_count(current_user.channel_id)
        else:
            current_value = goal.current_value
        
        # Update goal in database
        goal.current_value = current_value
        db.session.commit()
        
        progress_percentage = (current_value / goal.target_value * 100) if goal.target_value > 0 else 0
        
        return {
            'goal_id': goal_id,
            'current_value': current_value,
            'target_value': goal.target_value,
            'progress_percentage': round(progress_percentage, 2),
            'status': 'completed' if progress_percentage >= 100 else 'in_progress',
            'last_updated': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error calculating goal progress: {e}")
        return None

# Utility Functions
def extract_channel_id(channel_input):
    """Extract channel ID from URL or return as-is if already ID"""
    if 'youtube.com' in channel_input:
        # Extract from URL
        if '/channel/' in channel_input:
            return channel_input.split('/channel/')[-1].split('?')[0]
        elif '/c/' in channel_input or '/user/' in channel_input:
            # Would need to resolve custom URL to channel ID
            return resolve_custom_url_to_channel_id(channel_input)
    return channel_input

def get_channel_info(channel_id):
    """Get basic channel information"""
    try:
        # Use YouTube API to get channel info
        response = requests.get(
            'https://www.googleapis.com/youtube/v3/channels',
            params={
                'part': 'snippet,statistics',
                'id': channel_id,
                'key': creo_api_key
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('items'):
                channel = data['items'][0]
                return {
                    'name': channel['snippet']['title'],
                    'subscriber_count': int(channel['statistics'].get('subscriberCount', 0)),
                    'total_views': int(channel['statistics'].get('viewCount', 0)),
                    'video_count': int(channel['statistics'].get('videoCount', 0))
                }
        return {}
    except Exception as e:
        print(f"Error getting channel info: {e}")
        return {}
            
    except Exception as e:
        print(f"Error fetching demographics: {e}")
        return {}

def get_youtube_credentials():
    """Get YouTube API credentials from session"""
    if 'youtube_token' not in session:
        return None
    return Credentials(**session['youtube_token'])

def fetch_video_analytics_detailed(video_id):
    """Fetch detailed analytics for a specific video"""
    try:
        creds = get_youtube_credentials()
        if not creds:
            return None
        
        # Get video statistics
        stats_response = requests.get(
            'https://www.googleapis.com/youtube/v3/videos',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'part': 'statistics,snippet,contentDetails',
                'id': video_id
            }
        )
        
        stats_data = stats_response.json()
        if not stats_data.get('items'):
            return None
        
        video_data = stats_data['items'][0]
        
        return {
            'video_id': video_id,
            'title': video_data['snippet']['title'],
            'views': int(video_data['statistics'].get('viewCount', 0)),
            'likes': int(video_data['statistics'].get('likeCount', 0)),
            'dislikes': int(video_data['statistics'].get('dislikeCount', 0)),
            'comments': int(video_data['statistics'].get('commentCount', 0)),
            'duration': video_data['contentDetails']['duration'],
            'published_at': video_data['snippet']['publishedAt']
        }
    except Exception as e:
        print(f"Error fetching video analytics: {e}")
        return None

def get_video_retention_data(video_id):
    """Get audience retention data for a video"""
    try:
        creds = get_youtube_credentials()
        if not creds:
            return None
        
        # YouTube Analytics API call for retention data
        # Note: This requires YouTube Analytics API access
        analytics_response = requests.get(
            'https://youtubeanalytics.googleapis.com/v2/reports',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'ids': 'channel==MINE',
                'startDate': '2023-01-01',
                'endDate': datetime.now().strftime('%Y-%m-%d'),
                'metrics': 'audienceRetentionPercentage',
                'dimensions': 'elapsedVideoTimeRatio',
                'filters': f'video=={video_id}'
            }
        )
        
        if analytics_response.status_code == 200:
            data = analytics_response.json()
            return data.get('rows', [])
        return []
    except Exception as e:
        print(f"Error fetching retention data: {e}")
        return []



def get_video_traffic_sources(video_id):
    """Get traffic sources for a video"""
    try:
        creds = get_youtube_credentials()
        if not creds:
            return {}
        
        # YouTube Analytics API call for traffic sources
        analytics_response = requests.get(
            'https://youtubeanalytics.googleapis.com/v2/reports',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'ids': 'channel==MINE',
                'startDate': '2023-01-01',
                'endDate': datetime.now().strftime('%Y-%m-%d'),
                'metrics': 'views',
                'dimensions': 'trafficSourceType',
                'filters': f'video=={video_id}',
                'sort': '-views'
            }
        )
        
        if analytics_response.status_code == 200:
            data = analytics_response.json()
            traffic_sources = {}
            for row in data.get('rows', []):
                traffic_sources[row[0]] = row[1]
            return traffic_sources
        return {}
    except Exception as e:
        print(f"Error fetching traffic sources: {e}")
        return {}

def get_video_demographics(video_id):
    """Get demographic data for a video"""
    try:
        creds = get_youtube_credentials()
        if not creds:
            return {}
        
        # Age demographics
        age_response = requests.get(
            'https://youtubeanalytics.googleapis.com/v2/reports',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'ids': 'channel==MINE',
                'startDate': '2023-01-01',
                'endDate': datetime.now().strftime('%Y-%m-%d'),
                'metrics': 'viewerPercentage',
                'dimensions': 'ageGroup',
                'filters': f'video=={video_id}'
            }
        )
        
        # Gender demographics
        gender_response = requests.get(
            'https://youtubeanalytics.googleapis.com/v2/reports',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'ids': 'channel==MINE',
                'startDate': '2023-01-01',
                'endDate': datetime.now().strftime('%Y-%m-%d'),
                'metrics': 'viewerPercentage',
                'dimensions': 'gender',
                'filters': f'video=={video_id}'
            }
        )
        
        demographics = {}
        
        if age_response.status_code == 200:
            age_data = age_response.json()
            demographics['age'] = {row[0]: row[1] for row in age_data.get('rows', [])}
        
        if gender_response.status_code == 200:
            gender_data = gender_response.json()
            demographics['gender'] = {row[0]: row[1] for row in gender_data.get('rows', [])}
        
        return demographics
    except Exception as e:
        print(f"Error fetching demographics: {e}")
        return {}
    
def get_audience_demographics(channel_id):
    """Get overall channel audience demographics"""
    demographics = {
            'age_groups': {},
            'gender': {},
            'last_updated': datetime.now().isoformat()
        }
    try:
        creds = get_youtube_credentials()
        if not creds:
            return {}
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        # Age demographics
        age_response = requests.get(
            'https://youtubeanalytics.googleapis.com/v2/reports',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'ids': 'channel==MINE',
                'startDate': start_date,
                'endDate': end_date,
                'metrics': 'viewerPercentage',
                'dimensions': 'ageGroup'
            }
        )
        
        # Gender demographics
        gender_response = requests.get(
            'https://youtubeanalytics.googleapis.com/v2/reports',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'ids': 'channel==MINE',
                'startDate': start_date,
                'endDate': end_date,
                'metrics': 'viewerPercentage',
                'dimensions': 'gender'
            }
        )
        
        
        
        if age_response.status_code == 200:
            age_data = age_response.json()
            demographics['age'] = {row[0]: row[1] for row in age_data.get('rows', [])}
                    
            if gender_response.status_code == 200:
                gender_data = gender_response.json()
                demographics['gender'] = {row[0]: row[1] for row in gender_data.get('rows', [])}
    except:
        pass

    return demographics

# 1. VideoPerformance class stub
class VideoPerformance:
    def __init__(self, video_id=None, views=0, likes=0, comments=0, engagement_rate=0.0):
        self.video_id = video_id
        self.views = views
        self.likes = likes
        self.comments = comments
        self.engagement_rate = engagement_rate

    def to_dict(self):
        return {
            "video_id": self.video_id,
            "views": self.views,
            "likes": self.likes,
            "comments": self.comments,
            "engagement_rate": self.engagement_rate
        }

# 2. defaultdict (from collections)
from collections import defaultdict

# 3. CompetitorAnalysis class stub
class CompetitorAnalysis:
    def __init__(self, channel_id, metrics=None):
        self.channel_id = channel_id
        self.metrics = metrics or {}

    def add_metric(self, key, value):
        self.metrics[key] = value

    def to_dict(self):
        return {
            "channel_id": self.channel_id,
            "metrics": self.metrics
        }

# 4. get_competitor_videos
def get_competitor_videos(competitor_channel_id):
    # Stub: Return a list of video IDs for a competitor
    return [f"{competitor_channel_id}_vid_{i}" for i in range(1, 6)]

# 5. get_user_subscriber_count
def get_user_subscriber_count(user_id):
    # Stub: Return a dummy subscriber count
    return 1234

# 6. calculate_user_avg_views
def calculate_user_avg_views(user_id):
    # Stub: Return a dummy average views per video
    return 567

# 7. calculate_user_avg_engagement
def calculate_user_avg_engagement(user_id):
    # Stub: Return a dummy engagement rate
    return 0.075

# 8. analyse_competitor_content
def analyse_competitor_content(competitor_channel_id):
    # Stub: Return dummy content analysis
    return {
        "most_common_topics": ["python", "flask", "api"],
        "avg_views": 1200,
        "avg_engagement": 0.08
    }

# 9. find_competitor_keywords
def find_competitor_keywords(competitor_channel_id):
    # Stub: Return dummy keywords used by competitor
    return ["youtube growth", "seo", "tutorial"]

# 10. generate_competitor_recommendations
def generate_competitor_recommendations(user_id, competitor_channel_id):
    # Stub: Return dummy recommendations based on competitor
    return [
        "Post more tutorials on trending topics.",
        "Increase video upload frequency.",
        "Optimize thumbnails for higher CTR."
    ]

# 11. get_user_metrics
def get_user_metrics(user_id):
    # Stub: Return dummy user metrics
    return {
        "total_views": 100000,
        "subscribers": 2000,
        "videos": 50,
        "avg_watch_time": 5.2
    }

# 12. get_competitor_metrics
def get_competitor_metrics(competitor_channel_id):
    # Stub: Return dummy competitor metrics
    return {
        "total_views": 150000,
        "subscribers": 3500,
        "videos": 60,
        "avg_watch_time": 6.1
    }

# 13. Alert class stub
class Alert:
    def __init__(self, alert_id, user_id, message, active=True):
        self.alert_id = alert_id
        self.user_id = user_id
        self.message = message
        self.active = active

    def to_dict(self):
        return {
            "alert_id": self.alert_id,
            "user_id": self.user_id,
            "message": self.message,
            "active": self.active
        }

def get_user_total_views(channel_id):
    """
    Returns the total number of views for the given channel.
    Replace this stub with your database or YouTube API logic.
    """
    # Example: Query your VideoPerformance model or YouTube API
    # total_views = db.session.query(func.sum(VideoPerformance.views)).filter_by(channel_id=channel_id).scalar()
    # return total_views or 0
    return 123456  # Dummy value for demonstration

def get_user_video_count(channel_id):
    """
    Returns the total number of videos for the given channel.
    Replace this stub with your database or YouTube API logic.
    """
    # Example: Query your VideoPerformance model or YouTube API
    # video_count = db.session.query(VideoPerformance).filter_by(channel_id=channel_id).count()
    # return video_count
    return 42  # Dummy value for demonstration

def resolve_custom_url_to_channel_id(channel_input):
    """
    Resolves a YouTube custom URL or username to a channel ID.
    Replace this stub with a real API call to YouTube Data API.
    """
    # If the input is already a channel ID, return as is
    if channel_input.startswith("UC") and len(channel_input) >= 24:
        return channel_input

    # Otherwise, try to resolve using YouTube Data API
    # Example API call (requires API key):
    # url = f"https://www.googleapis.com/youtube/v3/channels?part=id&forUsername={channel_input}&key={creo_api_key}"
    # resp = requests.get(url)
    # data = resp.json()
    # if data.get("items"):
    #     return data["items"][0]["id"]
    # else:
    #     # Try resolving as a custom URL (not username)
    #     # You may need to scrape or use a different endpoint

    # For demonstration, return a dummy channel ID
    return "UCxxxxxxxxxxxxxxxxxxxxxx"

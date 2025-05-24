import time
import requests
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from flask import session
import json
from Creovue.config import creo_api_key

def get_comprehensive_audience_insights(channel_id, days):
    """Get comprehensive audience insights including demographics, behaviour, and growth patterns"""
    #print("channel_id: ", channel_id); time.sleep(30)

    creds = Credentials(**session['youtube_token'])
    #end_date = datetime.now().strftime('%Y-%m-%d')
    #start_date = (datetime.now() - timedelta(4000)).strftime('%Y-%m-%d')

    start_date = (datetime.now() - timedelta(days=4365)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    #print("age_response: ", age_response); time.sleep(3000)
    try:
        """creds = Credentials(**session['youtube_token'])
        if not creds:
            return {}
        """
        #end_date = datetime.now().strftime('%Y-%m-%d')
        #start_date = (datetime.now() - timedelta(days)).strftime('%Y-%m-%d')
        content_preferences = get_content_preferences(creds, start_date, end_date)
        print("content_preferences: ", content_preferences); time.sleep(300)
        traffic_sources = get_traffic_sources(creds, start_date, end_date)
        device_preferences = get_device_preferences(creds, start_date, end_date)
        engagement_overview = get_engagement_overview(creds, start_date, end_date)
        subscription_trends = get_subscription_trends(creds, start_date, end_date)
        viewing_behaviour_insights = get_viewing_behaviour_insights(creds, start_date, end_date)
        geographic_insights = get_geographic_insights(creds, start_date, end_date)
        age_response= get_audience_demographics(creds, start_date, end_date)
        insights = {
            'demographics': age_response, #get_audience_demographics(creds, start_date, end_date),
            'geographic_data': geographic_insights, #get_geographic_insights(creds, start_date, end_date),
            'viewing_behaviour': viewing_behaviour_insights, #get_viewing_behaviour_insights(creds, start_date, end_date),
            'subscription_trends': subscription_trends, #get_subscription_trends(creds, start_date, end_date),
            'engagement_overview': engagement_overview, #get_engagement_overview(creds, start_date, end_date),
            'device_preferences': device_preferences, #get_device_preferences(creds, start_date, end_date),
            'traffic_sources': traffic_sources, #get_traffic_sources(creds, start_date, end_date),
            'content_preferences': get_content_preferences(creds, start_date, end_date),
            'summary': {},
            'last_updated': datetime.now().isoformat()
        }

        
        # Generate summary insights
        insights['summary'] = generate_audience_summary(insights)
        print("insights: ", insights)
        
        return insights
        
    except Exception as e:
        print(f"Error getting comprehensive audience insights: {e}")
        return {'error': str(e)}


def get_audience_demographics(creds, start_date, end_date):
    """Get audience demographics (age, gender, country) with proper fallback handling."""
    try:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        youtube_analytics = build('youtubeAnalytics', 'v2', credentials=creds)

        demographics = {
            'age_groups': {},
            'gender': {},
            'countries': {},
            'last_updated': datetime.now().isoformat()
        }

        # Query Age Demographics
        age_response = youtube_analytics.reports().query(
            ids='channel==MINE',
            startDate=start_date,
            endDate=end_date,
            metrics='viewerPercentage',
            dimensions='ageGroup',
            sort='-viewerPercentage'
        ).execute()
        #print("Age rows:", age_response.get('rows'))

        if 'rows' in age_response:
            for row in age_response['rows']:
                age_group, percentage = row  # Only 2 values
                demographics['age_groups'][age_group] = {
                    'percentage': round(percentage, 2),
                    'label': format_age_group_label(age_group)
                }

        else:
            print("No age group data available.")

        # Query Gender Demographics
        gender_response = youtube_analytics.reports().query(
            ids='channel==MINE',
            startDate=start_date,
            endDate=end_date,
            metrics='viewerPercentage',
            dimensions='gender',
            sort='-viewerPercentage'
        ).execute()

        #print("Gender rows:", gender_response.get('rows'))


        if 'rows' in gender_response:
            for row in gender_response['rows']:
                gender, percentage = row
                demographics['gender'][gender] = {
                    'percentage': round(percentage, 2),
                    'label': gender.title()
                }

        else:
            print("No gender data available.")

        # Query Country Demographics
        geo_response = youtube_analytics.reports().query(
            ids='channel==MINE',
            startDate=start_date,
            endDate=end_date,
            metrics='views',
            dimensions='country',
            sort='-views',
            maxResults=20
        ).execute()
        #print("Country rows:", geo_response.get('rows'))



        if geo_response.get('rows'):
            total_views = sum(row[1] for row in geo_response['rows']) or 1  # Prevent division by zero

            for row in geo_response['rows']:
                country_code, view_count = row
                demographics['countries'][country_code] = {
                    'name': get_country_name(country_code),
                    'percentage': round((view_count / total_views) * 100, 2),
                    'views': view_count
                }
        else:
            print("No country data available.")


        return demographics

    except Exception as e:
        print(f"Error getting audience demographics: {e}")
        return {'error': str(e)}

def analyse_audience_retention(video_ids, channel_id):
    """Analyse audience retention patterns across multiple videos"""
    try:
        creds = Credentials(**session['youtube_token'])
        if not creds:
            return {}
        
        retention_data = {
            'video_analysis': {},
            'overall_patterns': {},
            'recommendations': [],
            'last_updated': datetime.now().isoformat()
        }
        
        total_retention_points = []
        video_durations = []
        drop_off_points = []
        
        for video_id in video_ids:
            # Get retention data for individual video
            retention_response = requests.get(
                'https://youtubeanalytics.googleapis.com/v2/reports',
                headers={'Authorization': f'Bearer {creds.token}'},
                params={
                    'ids': 'channel==MINE',
                    'filters': f'video=={video_id}',
                    'startDate': '2020-01-01',  # Use a wide date range
                    'endDate': datetime.now().strftime('%Y-%m-%d'),
                    'metrics': 'audienceRetentionForVideoPlayback',
                    'dimensions': 'elapsedVideoTimeRatio'
                }
            )
            
            # Get video details
            video_details = get_video_details(video_id, creds)
            
            if retention_response.status_code == 200:
                retention_json = retention_response.json()
                
                if 'rows' in retention_json and retention_json['rows']:
                    video_retention = {}
                    retention_points = []
                    
                    for row in retention_json['rows']:
                        time_ratio = row[0]
                        retention_percentage = row[1]
                        video_retention[time_ratio] = retention_percentage
                        retention_points.append(retention_percentage)
                        total_retention_points.append(retention_percentage)
                    
                    # Analyse drop-off points
                    drop_offs = find_significant_drop_offs(video_retention)
                    drop_off_points.extend(drop_offs)
                    
                    retention_data['video_analysis'][video_id] = {
                        'title': video_details.get('title', 'Unknown'),
                        'duration': video_details.get('duration', 0),
                        'retention_curve': video_retention,
                        'average_retention': round(statistics.mean(retention_points), 2) if retention_points else 0,
                        'retention_at_30s': video_retention.get(0.1, 0),  # Approximate 30s mark
                        'retention_at_50_percent': video_retention.get(0.5, 0),
                        'retention_at_end': retention_points[-1] if retention_points else 0,
                        'significant_drop_offs': drop_offs,
                        'engagement_score': calculate_engagement_score(retention_points)
                    }
                    
                    if video_details.get('duration'):
                        video_durations.append(video_details['duration'])
        
        # Calculate overall patterns
        if total_retention_points:
            retention_data['overall_patterns'] = {
                'average_retention': round(statistics.mean(total_retention_points), 2),
                'median_retention': round(statistics.median(total_retention_points), 2),
                'retention_std_dev': round(statistics.stdev(total_retention_points), 2) if len(total_retention_points) > 1 else 0,
                'common_drop_off_points': analyse_common_drop_offs(drop_off_points),
                'optimal_video_length': calculate_optimal_length(video_durations, retention_data['video_analysis']),
                'retention_trend': calculate_retention_trend(retention_data['video_analysis'])
            }
        
        # Generate recommendations
        retention_data['recommendations'] = generate_retention_recommendations(retention_data)
        
        return retention_data
        
    except Exception as e:
        print(f"Error analyzing audience retention: {e}")
        return {'error': str(e)}

def analyse_engagement_patterns(channel_id):
    """Analyse detailed audience engagement patterns and behaviours"""
    try:
        creds = Credentials(**session['youtube_token'])
        if not creds:
            return {}
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        patterns = {
            'temporal_patterns': get_temporal_engagement(creds, start_date, end_date),
            'content_type_performance': get_content_type_engagement(creds, start_date, end_date),
            'engagement_metrics': get_detailed_engagement_metrics(creds, start_date, end_date),
            'subscriber_vs_non_subscriber': get_subscriber_engagement_comparison(creds, start_date, end_date),
            'interaction_patterns': get_interaction_patterns(creds, start_date, end_date),
            'watch_time_patterns': get_watch_time_patterns(creds, start_date, end_date),
            'recommendations': [],
            'last_updated': datetime.now().isoformat()
        }
        
        # Generate engagement recommendations
        patterns['recommendations'] = generate_engagement_recommendations(patterns)
        
        return patterns
        
    except Exception as e:
        print(f"Error analyzing engagement patterns: {e}")
        return {'error': str(e)}

# Helper functions for comprehensive analysis
def get_geographic_insights(creds, start_date, end_date):
    """Get detailed geographic audience insights"""
    try:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        youtube_analytics = build('youtubeAnalytics', 'v2', credentials=creds)

        # Execute the correct query with valid metrics
        country_response = youtube_analytics.reports().query(
            ids='channel==MINE',
            startDate=start_date,
            endDate=end_date,
            metrics='views,estimatedMinutesWatched,subscribersGained',
            dimensions='country',
            sort='-views',
            maxResults=25
        ).execute()

        #print("country_response:", country_response); time.sleep(30)

        countries = {}

        if 'rows' in country_response:
            for row in country_response['rows']:
                country_code = row[0]
                views = row[1]
                estimated_minutes = row[2]
                subscribers_gained = row[3]

                countries[country_code] = {
                    'name': get_country_name(country_code),
                    'views': views,
                    'watch_time_minutes': estimated_minutes,
                    'subscribers_gained': subscribers_gained,
                    'avg_view_duration': round((estimated_minutes * 60) / views, 2) if views > 0 else 0
                }

        return countries

    except Exception as e:
        print(f"Error getting geographic insights: {e}")
        return {}

def get_viewing_behaviour_insights(creds, start_date, end_date):
    """
    Analyse viewing behaviour patterns across traffic sources and devices.
    """
    try:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        youtube_analytics = build('youtubeAnalytics', 'v2', credentials=creds)

        behaviour = {
            'traffic_sources': {},
            'device_preferences': {},
            'viewing_patterns': {}
        }

        # Traffic source insights
        traffic_response = youtube_analytics.reports().query(
            ids='channel==MINE',
            startDate=start_date,
            endDate=end_date,
            metrics='views,estimatedMinutesWatched',
            dimensions='insightTrafficSourceType',
            sort='-views'
        ).execute()

        #print("traffic_response: ", traffic_response); time.sleep(3)

        if 'rows' in traffic_response:
            traffic_rows = traffic_response['rows']
            total_views = sum(row[1] for row in traffic_rows)

            for row in traffic_rows:
                source = row[0]
                views = row[1]
                watch_time = row[2]
                behaviour['traffic_sources'][source] = {
                    'views': views,
                    'watch_time_minutes': round(watch_time, 2),
                    'percentage': round((views / total_views) * 100, 2) if total_views > 0 else 0,
                    'avg_duration_seconds': round((watch_time * 60 / views), 2) if views > 0 else 0
                }

        # Device usage insights
        device_response = youtube_analytics.reports().query(
            ids='channel==MINE',
            startDate=start_date,
            endDate=end_date,
            metrics='views,estimatedMinutesWatched',
            dimensions='deviceType',
            sort='-views'
        ).execute()

        if 'rows' in device_response:
            device_rows = device_response['rows']
            total_views = sum(row[1] for row in device_rows)

            for row in device_rows:
                device = row[0]
                views = row[1]
                watch_time = row[2]
                behaviour['device_preferences'][device] = {
                    'views': views,
                    'watch_time_minutes': round(watch_time, 2),
                    'percentage': round((views / total_views) * 100, 2) if total_views > 0 else 0,
                    'avg_duration_seconds': round((watch_time * 60 / views), 2) if views > 0 else 0
                }

        return behaviour

    except Exception as e:
        print(f"Error getting viewing behaviour insights: {e}")
        return {}

def get_subscription_trends(creds, start_date, end_date):
    """Analyse subscription growth patterns."""
    try:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        youtube_analytics = build('youtubeAnalytics', 'v2', credentials=creds)

        subscription_response = youtube_analytics.reports().query(
            ids='channel==MINE',
            startDate=start_date,
            endDate=end_date,
            metrics='subscribersGained,subscribersLost',
            dimensions='day',
            sort='day'
        ).execute()

        #print("subscription_response:", subscription_response ); time.sleep(300)
        trends = {
            'daily_data': [],
            'total_gained': 0,
            'total_lost': 0,
            'net_growth': 0,
            'growth_rate': 0,
            'best_day': None,
            'worst_day': None
        }

        if 'rows' in subscription_response:
            daily_net = []

            for row in subscription_response['rows']:
                date, gained, lost = row
                net = gained - lost

                trends['daily_data'].append({
                    'date': date,
                    'gained': gained,
                    'lost': lost,
                    'net': net
                })

                daily_net.append((date, net))
                trends['total_gained'] += gained
                trends['total_lost'] += lost

            trends['net_growth'] = trends['total_gained'] - trends['total_lost']

            if daily_net:
                trends['best_day'] = max(daily_net, key=lambda x: x[1])
                trends['worst_day'] = min(daily_net, key=lambda x: x[1])

        return trends

    except Exception as e:
        print(f"Error getting subscription trends: {e}")
        return {}

def get_engagement_overview(creds, start_date, end_date):
    """Get comprehensive engagement metrics overview."""
    try:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        youtube_analytics = build('youtubeAnalytics', 'v2', credentials=creds)

        engagement_response = youtube_analytics.reports().query(
            ids='channel==MINE',
            startDate=start_date,
            endDate=end_date,
            metrics='views,likes,comments,shares,estimatedMinutesWatched,averageViewDuration',
        ).execute()

        #print("engagement_response:", engagement_response ); time.sleep(300)

        if engagement_response.get('rows'):
            row = engagement_response['rows'][0]
            views = row[0]
            likes = row[1]
            comments = row[2]
            shares = row[3]
            watch_time = row[4]
            avg_duration = row[5]

            return {
                'total_views': views,
                'total_likes': likes,
                'total_comments': comments,
                'total_shares': shares,
                'total_watch_time_minutes': watch_time,
                'average_view_duration_seconds': avg_duration,
                'engagement_rate': round(((likes + comments + shares) / views) * 100, 2) if views > 0 else 0,
                'like_ratio': round((likes / views) * 100, 2) if views > 0 else 0,
                'comment_ratio': round((comments / views) * 100, 2) if views > 0 else 0
            }
        else:
            print("No engagement data available.")
            return {}

    except Exception as e:
        print(f"Error getting engagement overview: {e}")
        return {}

def get_device_preferences(creds, start_date, end_date):
    """Get detailed device usage preferences and performance metrics"""
    try:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

        youtube_analytics = build('youtubeAnalytics', 'v2', credentials=creds)

        preferences = {
            'device_types': {},
            'operating_systems': {},
            'device_insights': {},
            'recommendations': []
        }

        # ✅ Device data (without subscribersGained)
        device_data = youtube_analytics.reports().query(
            ids='channel==MINE',
            startDate=start_date,
            endDate=end_date,
            metrics='views,estimatedMinutesWatched,averageViewDuration',
            dimensions='deviceType',
            sort='-views'
        ).execute()

        # Optional: Subscribers by device fallback (if supported)
        subscriber_data = {}  # e.g., if you find a supported alternative dimension

        if 'rows' in device_data:
            total_views = sum(row[1] for row in device_data['rows'])

            for row in device_data['rows']:
                device_type = row[0]
                views = row[1]
                minutes_watched = row[2]
                avg_duration = row[3]
                subscribers = subscriber_data.get(device_type, 0)

                preferences['device_types'][device_type] = {
                    'views': views,
                    'watch_time_minutes': minutes_watched,
                    'average_view_duration': avg_duration,
                    'subscribers_gained': subscribers,
                    'percentage_of_views': round((views / total_views) * 100, 2) if total_views else 0,
                    'engagement_quality': calculate_device_engagement_quality(views, minutes_watched, avg_duration)
                }

        # ✅ OS data (ensure metrics are valid)
        os_data = youtube_analytics.reports().query(
            ids='channel==MINE',
            startDate=start_date,
            endDate=end_date,
            metrics='views,estimatedMinutesWatched',
            dimensions='operatingSystem',
            sort='-views',
            maxResults=10
        ).execute()

        if 'rows' in os_data:
            total_views = sum(row[1] for row in os_data['rows'])
            for row in os_data['rows']:
                os_name = row[0]
                views = row[1]
                minutes_watched = row[2]

                preferences['operating_systems'][os_name] = {
                    'views': views,
                    'watch_time_minutes': minutes_watched,
                    'percentage_of_views': round((views / total_views) * 100, 2) if total_views else 0,
                    'avg_session_duration': round(minutes_watched * 60 / views, 2) if views else 0
                }

        preferences['device_insights'] = analyse_device_performance(preferences['device_types'])
        preferences['recommendations'] = generate_device_recommendations(preferences)

        return preferences

    except Exception as e:
        print(f"Error getting device preferences: {e}")
        return {}


def get_traffic_sources(creds, start_date, end_date):
    """Get comprehensive traffic source analysis and performance metrics"""
    try:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

        youtube_analytics = build('youtubeAnalytics', 'v2', credentials=creds)

        sources = {
            'traffic_types': {},
            'traffic_details': {},
            'performance_metrics': {},
            'growth_sources': {},
            'recommendations': []
        }

        # ✅ Traffic Type: Remove unsupported metric
        traffic_data = youtube_analytics.reports().query(
            ids='channel==MINE',
            startDate=start_date,
            endDate=end_date,
            metrics='views,estimatedMinutesWatched,averageViewDuration',
            dimensions='insightTrafficSourceType',
            sort='-views'
        ).execute()

        #print("traffic_data: ", traffic_data); time.sleep(30)
        
        if 'rows' in traffic_data:
            total_views = sum(row[1] for row in traffic_data['rows'])

            for row in traffic_data['rows']:
                source_type = row[0]
                views = row[1]
                minutes_watched = row[2]
                avg_duration = row[3]
                subscribers = row[4] if len(row) > 4 else 0

                sources['traffic_types'][source_type] = {
                    'views': views,
                    'watch_time_minutes': minutes_watched,
                    'average_view_duration': avg_duration,
                    'subscribers_gained': subscribers,
                    'percentage_of_views': round((views / total_views) * 100, 2) if total_views else 0,
                    'quality_score': calculate_traffic_quality_score(views, minutes_watched, subscribers, avg_duration),
                    'label': format_traffic_source_label(source_type)
                }

        # Detailed Sources (fixed)
        detail_data = youtube_analytics.reports().query(
            ids='channel==MINE',
            startDate=start_date,
            endDate=end_date,
            metrics='views',
            dimensions='insightTrafficSourceDetail',
            filters='insightTrafficSourceType==RELATED_VIDEO',  # ✅ Required for this dimension
            sort='-views',
            maxResults=20
        ).execute()


        #print("detail_data: ", detail_data); time.sleep(30)
        TRAFFIC_TYPES = ['RELATED_VIDEO', 'YT_SEARCH', 'EXT_URL', 'YT_CHANNEL', 'PLAYLIST']

        traffic_details = {}
                                                          
        if 'rows' in detail_data:
            for row in detail_data['rows']:
                detail_source = row[0]
                views = row[1]

                sources['traffic_details'][detail_source] = {
                    'views': views
                }


        sources['performance_metrics'] = calculate_traffic_performance_metrics(sources['traffic_types'])
        sources['growth_sources'] = identify_growth_traffic_sources(sources['traffic_types'])
        sources['recommendations'] = generate_traffic_recommendations(sources)

        return sources

    except Exception as e:
        print(f"Error getting traffic sources: {e}")
        return {}


def get_content_preferences(creds, start_date, end_date):
    """Analyse content preferences and performance patterns"""
    try:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        youtube_analytics = build('youtubeAnalytics', 'v2', credentials=creds)

        # ⚠️ Only allowed metrics for dimension=video (as per docs)
        performance_response = youtube_analytics.reports().query(
            ids='channel==MINE',
            startDate=start_date,
            endDate=end_date,
            metrics='views,likes,comments,shares,averageViewDuration',
            dimensions='video',
            sort='-views',
            maxResults=50
        ).execute()

        print("performance_response: ", performance_response); time.sleep(30)
        preferences = {
            'content_performance': {},
            'content_categories': {},
            'engagement_patterns': {},
            'optimal_content_features': {},
            'trending_topics': [],
            'recommendations': []
        }

        if 'rows' in performance_response:
            video_performances = []

            for row in performance_response['rows']:
                video_id = row[0]
                views = row[1]
                likes = row[2]
                comments = row[3]
                shares = row[4]
                avg_duration = row[5]

                # ✅ Fetch video metadata using YouTube Data API v3
                video_details = get_video_details(video_id, creds)
                print("avg_duration: ", avg_duration)
                duration_sec = video_details.get('duration', 0)
                performance_data = {
                    'video_id': video_id,
                    'title': video_details.get('title', 'Unknown'),
                    'duration': duration_sec,
                    'tags': video_details.get('tags', []),
                    'category': video_details.get('category', 'Unknown'),
                    'views': views,
                    'likes': likes,
                    'comments': comments,
                    'shares': shares,
                    'average_view_duration': avg_duration,
                    'engagement_rate': round(((likes + comments + shares) / views) * 100, 2) if views > 0 else 0,
                    'retention_rate': round((avg_duration / duration_sec) * 100, 2) if duration_sec > 0 else 0,
                    'performance_score': calculate_content_performance_score(
                        views, likes, comments, shares, avg_duration
                    )
                }

                print("avg_duration: ", avg_duration)
                video_performances.append(performance_data)

            # 🚀 Analyse
            preferences['content_performance'] = analyse_content_patterns(video_performances)
            preferences['content_categories'] = analyse_content_categories(video_performances)
            preferences['engagement_patterns'] = analyse_content_engagement_patterns(video_performances)
            preferences['optimal_content_features'] = identify_optimal_content_features(video_performances)
            preferences['trending_topics'] = identify_trending_topics(video_performances)
            preferences['recommendations'] = generate_content_recommendations(preferences)

        return preferences

    except Exception as e:
        print(f"Error getting content preferences: {e}")
        return {}


def get_temporal_engagement(creds, start_date, end_date):
    """Analyse engagement patterns by time"""
    try:
        # Daily patterns
        daily_response = requests.get(
            'https://youtubeanalytics.googleapis.com/v2/reports',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'ids': 'channel==MINE',
                'startDate': start_date,
                'endDate': end_date,
                'metrics': 'views,likes,comments,watchTimeMinutes',
                'dimensions': 'day',
                'sort': 'day'
            }
        )
        
        patterns = {
            'daily_trends': [],
            'weekly_patterns': {},
            'peak_engagement_times': []
        }
        
        if daily_response.status_code == 200:
            data = daily_response.json()
            if 'rows' in data:
                for row in data['rows']:
                    date = datetime.strptime(row[0], '%Y-%m-%d')
                    day_of_week = date.strftime('%A')
                    
                    daily_data = {
                        'date': row[0],
                        'day_of_week': day_of_week,
                        'views': row[1],
                        'likes': row[2],
                        'comments': row[3],
                        'watch_time': row[4],
                        'engagement_rate': round(((row[2] + row[3]) / row[1]) * 100, 2) if row[1] > 0 else 0
                    }
                    
                    patterns['daily_trends'].append(daily_data)
                    
                    # Aggregate by day of week
                    if day_of_week not in patterns['weekly_patterns']:
                        patterns['weekly_patterns'][day_of_week] = {
                            'total_views': 0,
                            'total_engagement': 0,
                            'days_count': 0
                        }
                    
                    patterns['weekly_patterns'][day_of_week]['total_views'] += row[1]
                    patterns['weekly_patterns'][day_of_week]['total_engagement'] += (row[2] + row[3])
                    patterns['weekly_patterns'][day_of_week]['days_count'] += 1
                
                # Calculate averages for weekly patterns
                for day in patterns['weekly_patterns']:
                    data = patterns['weekly_patterns'][day]
                    data['avg_views'] = round(data['total_views'] / data['days_count'], 2)
                    data['avg_engagement_rate'] = round((data['total_engagement'] / data['total_views']) * 100, 2) if data['total_views'] > 0 else 0
        
        return patterns
        
    except Exception as e:
        print(f"Error getting temporal engagement: {e}")
        return {}

# Additional helper functions

def format_age_group_label(age_group):
    """Format age group codes into readable labels"""
    age_labels = {
        'age13-17': '13-17 years',
        'age18-24': '18-24 years',
        'age25-34': '25-34 years',
        'age35-44': '35-44 years',
        'age45-54': '45-54 years',
        'age55-64': '55-64 years',
        'age65-': '65+ years'
    }
    return age_labels.get(age_group, age_group)

def get_country_name(country_code):
    """Convert country code to country name"""
    # This would typically use a comprehensive country code mapping
    country_names = {
        'US': 'United States',
        'GB': 'United Kingdom',
        'CA': 'Canada',
        'AU': 'Australia',
        'DE': 'Germany',
        'FR': 'France',
        'JP': 'Japan',
        'IN': 'India',
        'BR': 'Brazil',
        'MX': 'Mexico'
        # Add more as needed
    }
    return country_names.get(country_code, country_code)

def find_significant_drop_offs(retention_data):
    """Find significant drop-off points in retention data"""
    drop_offs = []
    retention_points = list(retention_data.items())
    
    for i in range(1, len(retention_points)):
        prev_retention = retention_points[i-1][1]
        curr_retention = retention_points[i][1]
        
        # Consider a drop of more than 10% as significant
        if prev_retention - curr_retention > 10:
            drop_offs.append({
                'time_ratio': retention_points[i][0],
                'drop_percentage': prev_retention - curr_retention
            })
    
    return drop_offs

def calculate_engagement_score(retention_points):
    """Calculate an engagement score based on retention curve"""
    if not retention_points:
        return 0
    
    # Weight later retention points more heavily
    weighted_score = 0
    total_weight = 0
    
    for i, retention in enumerate(retention_points):
        weight = i + 1
        weighted_score += retention * weight
        total_weight += weight
    
    return round(weighted_score / total_weight, 2) if total_weight > 0 else 0

def generate_audience_summary(insights):
    """Generate summary insights from comprehensive audience data"""
    summary = {
        'key_demographics': {},
        'top_insights': [],
        'growth_indicators': {},
        'recommendations': []
    }
    
    # Analyse demographics
    if 'demographics' in insights and insights['demographics']:
        demo = insights['demographics']
        
        if 'age_groups' in demo:
            top_age_group = max(demo['age_groups'].items(), 
                              key=lambda x: x[1]['percentage'], default=(None, None))
            if top_age_group[0]:
                summary['key_demographics']['primary_age_group'] = {
                    'group': top_age_group[1]['label'],
                    'percentage': top_age_group[1]['percentage']
                }
        
        if 'gender' in demo:
            gender_split = demo['gender']
            summary['key_demographics']['gender_split'] = gender_split
        
        if 'countries' in demo:
            top_country = max(demo['countries'].items(), 
                            key=lambda x: x[1]['percentage'], default=(None, None))
            if top_country[0]:
                summary['key_demographics']['top_country'] = {
                    'name': top_country[1]['name'],
                    'percentage': top_country[1]['percentage']
                }
    
    return summary

def generate_retention_recommendations(retention_data):
    """Generate actionable recommendations based on retention analysis"""
    recommendations = []
    
    if 'overall_patterns' in retention_data:
        patterns = retention_data['overall_patterns']
        
        if patterns.get('average_retention', 0) < 40:
            recommendations.append({
                'type': 'retention_improvement',
                'priority': 'high',
                'title': 'Improve Video Hooks',
                'description': 'Your average retention is below 40%. Focus on creating stronger opening hooks in the first 15 seconds.'
            })
        
        if patterns.get('common_drop_off_points'):
            recommendations.append({
                'type': 'content_structure',
                'priority': 'medium',
                'title': 'Optimize Content Structure',
                'description': 'Analyse common drop-off points and restructure content to maintain engagement at these critical moments.'
            })
    
    return recommendations

def generate_engagement_recommendations(patterns):
    """Generate recommendations based on engagement patterns"""
    recommendations = []
    
    if 'temporal_patterns' in patterns and patterns['temporal_patterns'].get('weekly_patterns'):
        weekly = patterns['temporal_patterns']['weekly_patterns']
        
        # Find best performing day
        best_day = max(weekly.items(), key=lambda x: x[1].get('avg_engagement_rate', 0))
        
        recommendations.append({
            'type': 'posting_schedule',
            'priority': 'medium',
            'title': f'Optimize Posting Schedule',
            'description': f'{best_day[0]} shows the highest engagement rate. Consider posting more content on this day.'
        })
    
    return recommendations




# Helper functions for comprehensive analysis

def get_geographic_insights_test(creds, start_date, end_date):
    """Get detailed geographic audience insights"""
    try:
        response = requests.get(
            'https://youtubeanalytics.googleapis.com/v2/reports',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'ids': 'channel==MINE',
                'startDate': start_date,
                'endDate': end_date,
                'metrics': 'views,watchTimeMinutes,subscribersGained',
                'dimensions': 'country',
                'sort': '-views',
                'maxResults': 25
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            countries = {}
            
            if 'rows' in data:
                for row in data['rows']:
                    country_code = row[0]
                    countries[country_code] = {
                        'name': get_country_name(country_code),
                        'views': row[1],
                        'watch_time_minutes': row[2],
                        'subscribers_gained': row[3],
                        'avg_view_duration': round(row[2] * 60 / row[1], 2) if row[1] > 0 else 0
                    }
            
            return countries
        
        return {}
        
    except Exception as e:
        print(f"Error getting geographic insights: {e}")
        return {}

def get_viewing_behaviour_insights_test(creds, start_date, end_date):
    """Analyse viewing behaviour patterns"""
    try:
        # Get traffic sources
        traffic_response = requests.get(
            'https://youtubeanalytics.googleapis.com/v2/reports',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'ids': 'channel==MINE',
                'startDate': start_date,
                'endDate': end_date,
                'metrics': 'views,watchTimeMinutes',
                'dimensions': 'insightTrafficSourceType',
                'sort': '-views'
            }
        )
        
        # Get device types
        device_response = requests.get(
            'https://youtubeanalytics.googleapis.com/v2/reports',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'ids': 'channel==MINE',
                'startDate': start_date,
                'endDate': end_date,
                'metrics': 'views,watchTimeMinutes',
                'dimensions': 'deviceType',
                'sort': '-views'
            }
        )
        
        behaviour = {
            'traffic_sources': {},
            'device_preferences': {},
            'viewing_patterns': {}
        }
        
        if traffic_response.status_code == 200:
            traffic_data = traffic_response.json()
            if 'rows' in traffic_data:
                total_views = sum(row[1] for row in traffic_data['rows'])
                for row in traffic_data['rows']:
                    source = row[0]
                    views = row[1]
                    watch_time = row[2]
                    behaviour['traffic_sources'][source] = {
                        'views': views,
                        'watch_time_minutes': watch_time,
                        'percentage': round((views / total_views) * 100, 2) if total_views > 0 else 0,
                        'avg_duration': round(watch_time * 60 / views, 2) if views > 0 else 0
                    }
        
        if device_response.status_code == 200:
            device_data = device_response.json()
            if 'rows' in device_data:
                total_views = sum(row[1] for row in device_data['rows'])
                for row in device_data['rows']:
                    device = row[0]
                    views = row[1]
                    watch_time = row[2]
                    behaviour['device_preferences'][device] = {
                        'views': views,
                        'watch_time_minutes': watch_time,
                        'percentage': round((views / total_views) * 100, 2) if total_views > 0 else 0,
                        'avg_duration': round(watch_time * 60 / views, 2) if views > 0 else 0
                    }
        
        return behaviour
        
    except Exception as e:
        print(f"Error getting viewing behaviour insights: {e}")
        return {}

def get_subscription_trends_test(creds, start_date, end_date):
    """Analyse subscription growth patterns"""
    try:
        response = requests.get(
            'https://youtubeanalytics.googleapis.com/v2/reports',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'ids': 'channel==MINE',
                'startDate': start_date,
                'endDate': end_date,
                'metrics': 'subscribersGained,subscribersLost',
                'dimensions': 'day',
                'sort': 'day'
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            trends = {
                'daily_data': [],
                'total_gained': 0,
                'total_lost': 0,
                'net_growth': 0,
                'growth_rate': 0,
                'best_day': None,
                'worst_day': None
            }
            
            if 'rows' in data:
                daily_net = []
                for row in data['rows']:
                    date = row[0]
                    gained = row[1]
                    lost = row[2]
                    net = gained - lost
                    
                    trends['daily_data'].append({
                        'date': date,
                        'gained': gained,
                        'lost': lost,
                        'net': net
                    })
                    
                    daily_net.append((date, net))
                    trends['total_gained'] += gained
                    trends['total_lost'] += lost
                
                trends['net_growth'] = trends['total_gained'] - trends['total_lost']
                
                if daily_net:
                    trends['best_day'] = max(daily_net, key=lambda x: x[1])
                    trends['worst_day'] = min(daily_net, key=lambda x: x[1])
            
            return trends
        
        return {}
        
    except Exception as e:
        print(f"Error getting subscription trends: {e}")
        return {}

def get_engagement_overview_test(creds, start_date, end_date):
    """Get comprehensive engagement metrics overview"""
    try:
        response = requests.get(
            'https://youtubeanalytics.googleapis.com/v2/reports',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'ids': 'channel==MINE',
                'startDate': start_date,
                'endDate': end_date,
                'metrics': 'views,likes,dislikes,comments,shares,watchTimeMinutes,averageViewDuration'
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'rows' in data and data['rows']:
                row = data['rows'][0]
                
                views = row[0]
                likes = row[1]
                dislikes = row[2] if len(row) > 2 else 0
                comments = row[3] if len(row) > 3 else 0
                shares = row[4] if len(row) > 4 else 0
                watch_time = row[5] if len(row) > 5 else 0
                avg_duration = row[6] if len(row) > 6 else 0
                
                return {
                    'total_views': views,
                    'total_likes': likes,
                    'total_dislikes': dislikes,
                    'total_comments': comments,
                    'total_shares': shares,
                    'total_watch_time_minutes': watch_time,
                    'average_view_duration': avg_duration,
                    'engagement_rate': round(((likes + comments + shares) / views) * 100, 2) if views > 0 else 0,
                    'like_ratio': round((likes / views) * 100, 2) if views > 0 else 0,
                    'comment_ratio': round((comments / views) * 100, 2) if views > 0 else 0
                }
        
        return {}
        
    except Exception as e:
        print(f"Error getting engagement overview: {e}")
        return {}

def get_temporal_engagement(creds, start_date, end_date):
    """Analyse engagement patterns by time"""
    try:
        # Daily patterns
        daily_response = requests.get(
            'https://youtubeanalytics.googleapis.com/v2/reports',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'ids': 'channel==MINE',
                'startDate': start_date,
                'endDate': end_date,
                'metrics': 'views,likes,comments,watchTimeMinutes',
                'dimensions': 'day',
                'sort': 'day'
            }
        )
        
        patterns = {
            'daily_trends': [],
            'weekly_patterns': {},
            'peak_engagement_times': []
        }
        
        if daily_response.status_code == 200:
            data = daily_response.json()
            if 'rows' in data:
                for row in data['rows']:
                    date = datetime.strptime(row[0], '%Y-%m-%d')
                    day_of_week = date.strftime('%A')
                    
                    daily_data = {
                        'date': row[0],
                        'day_of_week': day_of_week,
                        'views': row[1],
                        'likes': row[2],
                        'comments': row[3],
                        'watch_time': row[4],
                        'engagement_rate': round(((row[2] + row[3]) / row[1]) * 100, 2) if row[1] > 0 else 0
                    }
                    
                    patterns['daily_trends'].append(daily_data)
                    
                    # Aggregate by day of week
                    if day_of_week not in patterns['weekly_patterns']:
                        patterns['weekly_patterns'][day_of_week] = {
                            'total_views': 0,
                            'total_engagement': 0,
                            'days_count': 0
                        }
                    
                    patterns['weekly_patterns'][day_of_week]['total_views'] += row[1]
                    patterns['weekly_patterns'][day_of_week]['total_engagement'] += (row[2] + row[3])
                    patterns['weekly_patterns'][day_of_week]['days_count'] += 1
                
                # Calculate averages for weekly patterns
                for day in patterns['weekly_patterns']:
                    data = patterns['weekly_patterns'][day]
                    data['avg_views'] = round(data['total_views'] / data['days_count'], 2)
                    data['avg_engagement_rate'] = round((data['total_engagement'] / data['total_views']) * 100, 2) if data['total_views'] > 0 else 0
        
        return patterns
        
    except Exception as e:
        print(f"Error getting temporal engagement: {e}")
        return {}


# Helper functions for device preferences

def calculate_device_engagement_quality(views, watch_time, avg_duration):
    """Calculate engagement quality score for device types"""
    if views == 0:
        return 0
    
    watch_time_per_view = watch_time / views
    engagement_score = (watch_time_per_view * 0.6) + (avg_duration * 0.4)
    
    # Normalize to 0-100 scale
    return min(round(engagement_score, 2), 100)

def analyse_device_performance(device_types):
    """Analyse performance differences across device types"""
    insights = {
        'best_performing_device': None,
        'mobile_vs_desktop': {},
        'engagement_differences': {}
    }
    
    if device_types:
        # Find best performing device
        best_device = max(device_types.items(), 
                         key=lambda x: x[1]['engagement_quality'], 
                         default=(None, None))
        
        if best_device[0]:
            insights['best_performing_device'] = {
                'device': best_device[0],
                'engagement_quality': best_device[1]['engagement_quality']
            }
        
        # Compare mobile vs desktop if both exist
        mobile_devices = ['MOBILE', 'TABLET']
        desktop_devices = ['DESKTOP', 'TV']
        
        mobile_stats = {'views': 0, 'watch_time': 0}
        desktop_stats = {'views': 0, 'watch_time': 0}
        
        for device, stats in device_types.items():
            if device in mobile_devices:
                mobile_stats['views'] += stats['views']
                mobile_stats['watch_time'] += stats['watch_time_minutes']
            elif device in desktop_devices:
                desktop_stats['views'] += stats['views']
                desktop_stats['watch_time'] += stats['watch_time_minutes']
        
        total_views = mobile_stats['views'] + desktop_stats['views']
        if total_views > 0:
            insights['mobile_vs_desktop'] = {
                'mobile_percentage': round((mobile_stats['views'] / total_views) * 100, 2),
                'desktop_percentage': round((desktop_stats['views'] / total_views) * 100, 2),
                'mobile_avg_duration': round(mobile_stats['watch_time'] * 60 / mobile_stats['views'], 2) if mobile_stats['views'] > 0 else 0,
                'desktop_avg_duration': round(desktop_stats['watch_time'] * 60 / desktop_stats['views'], 2) if desktop_stats['views'] > 0 else 0
            }
    
    return insights

def generate_device_recommendations(preferences):
    """Generate recommendations based on device usage patterns"""
    recommendations = []
    
    if 'device_types' in preferences:
        device_types = preferences['device_types']
        
        # Check mobile optimization
        mobile_percentage = 0
        for device, stats in device_types.items():
            if device in ['MOBILE', 'TABLET']:
                mobile_percentage += stats['percentage_of_views']
        
        if mobile_percentage > 60:
            recommendations.append({
                'type': 'mobile_optimization',
                'priority': 'high',
                'title': 'Optimize for Mobile Viewing',
                'description': f'{mobile_percentage:.1f}% of your views come from mobile devices. Ensure your content is optimized for smaller screens and shorter attention spans.'
            })
        
        # TV viewing recommendations
        if 'TV' in device_types and device_types['TV']['percentage_of_views'] > 15:
            recommendations.append({
                'type': 'tv_optimization',
                'priority': 'medium',
                'title': 'Leverage TV Viewing',
                'description': 'Significant TV viewership detected. Consider creating longer-form content that works well on larger screens.'
            })
    
    return recommendations

# Helper functions for traffic sources

def format_traffic_source_label(source_type):
    """Format traffic source types into readable labels"""
    source_labels = {
        'YT_SEARCH': 'YouTube Search',
        'SUGGESTED_VIDEO': 'Suggested Videos',
        'CHANNEL_PAGE': 'Channel Page',
        'DIRECT_OR_UNKNOWN': 'Direct/Unknown',
        'EXTERNAL_WEBSITE': 'External Websites',
        'NOTIFICATION': 'Notifications',
        'PLAYLIST': 'Playlists',
        'RELATED_VIDEO': 'Related Videos',
        'SOCIAL': 'Social Media',
        'ADVERTISING': 'Advertising'
    }
    return source_labels.get(source_type, source_type.replace('_', ' ').title())

def calculate_traffic_quality_score(views, watch_time, subscribers, avg_duration):
    """Calculate quality score for traffic sources"""
    if views == 0:
        return 0
    
    # Weight different metrics
    view_quality = min(views / 1000, 10)  # Cap at 10 points
    watch_time_quality = (watch_time / views) * 2  # Watch time per view
    subscriber_quality = (subscribers / views) * 100  # Subscription rate
    duration_quality = min(avg_duration / 60, 10)  # Average duration in minutes, capped at 10
    
    total_score = (view_quality * 0.3) + (watch_time_quality * 0.3) + (subscriber_quality * 0.2) + (duration_quality * 0.2)
    
    return round(min(total_score, 100), 2)

def calculate_traffic_performance_metrics(traffic_types):
    """Calculate overall performance metrics for traffic sources"""
    metrics = {
        'total_sources': len(traffic_types),
        'primary_source': None,
        'diversification_score': 0,
        'quality_sources': []
    }
    
    if traffic_types:
        # Find primary source
        primary = max(traffic_types.items(), key=lambda x: x[1]['views'])
        metrics['primary_source'] = {
            'type': primary[0],
            'label': primary[1]['label'],
            'percentage': primary[1]['percentage_of_views']
        }
        
        # Calculate diversification (lower is more diversified)
        percentages = [data['percentage_of_views'] for data in traffic_types.values()]
        metrics['diversification_score'] = round(max(percentages) - min(percentages), 2)
        
        # Identify high-quality sources
        for source, data in traffic_types.items():
            if data['quality_score'] > 70:
                metrics['quality_sources'].append({
                    'type': source,
                    'label': data['label'],
                    'quality_score': data['quality_score']
                })
    
    return metrics

def identify_growth_traffic_sources(traffic_types):
    """Identify traffic sources with growth potential"""
    growth_sources = []
    
    for source, data in traffic_types.items():
        # High subscriber conversion rate indicates growth potential
        if data['views'] > 0:
            conversion_rate = (data['subscribers_gained'] / data['views']) * 100
            
            if conversion_rate > 0.5:  # 0.5% conversion rate threshold
                growth_sources.append({
                    'type': source,
                    'label': data['label'],
                    'conversion_rate': round(conversion_rate, 3),
                    'potential': 'High' if conversion_rate > 1.0 else 'Medium'
                })
    
    return sorted(growth_sources, key=lambda x: x['conversion_rate'], reverse=True)

def generate_traffic_recommendations(sources):
    """Generate recommendations based on traffic source analysis"""
    recommendations = []
    
    if 'performance_metrics' in sources:
        metrics = sources['performance_metrics']
        
        # Check source diversification
        if metrics.get('primary_source', {}).get('percentage', 0) > 60:
            recommendations.append({
                'type': 'diversification',
                'priority': 'high',
                'title': 'Diversify Traffic Sources',
                'description': f'Over 60% of traffic comes from {metrics["primary_source"]["label"]}. Work on developing other traffic sources for stability.'
            })
        
        # YouTube Search optimization
        if 'traffic_types' in sources:
            search_percentage = 0
            for source, data in sources['traffic_types'].items():
                if source == 'YT_SEARCH':
                    search_percentage = data['percentage_of_views']
                    break
            
            if search_percentage < 20:
                recommendations.append({
                    'type': 'seo_optimization',
                    'priority': 'medium',
                    'title': 'Improve YouTube SEO',
                    'description': 'Only {:.1f}% of traffic comes from YouTube search. Optimize titles, descriptions, and tags for better discoverability.'.format(search_percentage)
                })
    
    return recommendations

# Helper functions for content preferences

def get_video_details(video_id, creds):
    """Get detailed video information"""
    try:
        # This would typically call YouTube Data API v3 to get video details
        # For now, return mock data structure
        return {
            'title': f'Video {video_id}',
            'duration': 300,  # 5 minutes in seconds
            'tags': ['example', 'content'],
            'category': 'Entertainment',
            'description': 'Sample video description'
        }
    except Exception as e:
        return {
            'title': 'Unknown',
            'duration': 0,
            'tags': [],
            'category': 'Unknown',
            'description': ''
        }

def calculate_content_performance_score(views, likes, comments, shares, watch_time, avg_duration):
    """Calculate overall performance score for content"""
    if views == 0:
        return 0
    
    # Normalize metrics
    engagement_rate = ((likes + comments + shares) / views) * 100
    watch_time_quality = (watch_time / views) * 10  # Minutes per view * 10
    duration_retention = min(avg_duration / 60, 10)  # Cap at 10 minutes
    
    # Weighted score
    score = (engagement_rate * 0.4) + (watch_time_quality * 0.4) + (duration_retention * 0.2)
    
    return round(min(score, 100), 2)

def analyse_content_patterns(video_performances):
    """Analyse patterns in content performance"""
    if not video_performances:
        return {}
    
    patterns = {
        'top_performers': [],
        'average_metrics': {},
        'performance_distribution': {}
    }
    
    # Get top 10 performers
    patterns['top_performers'] = sorted(video_performances, 
                                      key=lambda x: x['performance_score'], 
                                      reverse=True)[:10]
    
    # Calculate averages
    total_videos = len(video_performances)
    if total_videos > 0:
        patterns['average_metrics'] = {
            'avg_views': round(sum(v['views'] for v in video_performances) / total_videos, 2),
            'avg_engagement_rate': round(sum(v['engagement_rate'] for v in video_performances) / total_videos, 2),
            'avg_retention_rate': round(sum(v['retention_rate'] for v in video_performances) / total_videos, 2),
            'avg_duration': round(sum(v['duration'] for v in video_performances) / total_videos, 2)
        }
    
    return patterns

def analyse_content_categories(video_performances):
    """Analyse performance by content categories"""
    categories = {}
    
    for video in video_performances:
        category = video['category']
        if category not in categories:
            categories[category] = {
                'video_count': 0,
                'total_views': 0,
                'total_engagement': 0,
                'performance_scores': []
            }
        
        categories[category]['video_count'] += 1
        categories[category]['total_views'] += video['views']
        categories[category]['total_engagement'] += video['engagement_rate']
        categories[category]['performance_scores'].append(video['performance_score'])
    
    # Calculate averages
    for category, data in categories.items():
        if data['video_count'] > 0:
            data['avg_views'] = round(data['total_views'] / data['video_count'], 2)
            data['avg_engagement_rate'] = round(data['total_engagement'] / data['video_count'], 2)
            data['avg_performance_score'] = round(sum(data['performance_scores']) / len(data['performance_scores']), 2)
    
    return categories

def analyse_content_engagement_patterns(video_performances):
    """Analyse engagement patterns across content"""
    patterns = {
        'high_engagement_factors': [],
        'optimal_video_length': None,
        'engagement_trends': {}
    }
    
    # Analyse by duration ranges
    duration_ranges = {
        'short': (0, 180),      # 0-3 minutes
        'medium': (180, 600),   # 3-10 minutes
        'long': (600, 1800),    # 10-30 minutes
        'very_long': (1800, float('inf'))  # 30+ minutes
    }
    
    range_performance = {}
    
    for range_name, (min_dur, max_dur) in duration_ranges.items():
        videos_in_range = [v for v in video_performances 
                          if min_dur <= v['duration'] < max_dur]
        
        if videos_in_range:
            range_performance[range_name] = {
                'count': len(videos_in_range),
                'avg_engagement': round(sum(v['engagement_rate'] for v in videos_in_range) / len(videos_in_range), 2),
                'avg_views': round(sum(v['views'] for v in videos_in_range) / len(videos_in_range), 2)
            }
    
    # Find optimal length
    if range_performance:
        optimal_range = max(range_performance.items(), 
                           key=lambda x: x[1]['avg_engagement'])
        patterns['optimal_video_length'] = {
            'range': optimal_range[0],
            'avg_engagement': optimal_range[1]['avg_engagement']
        }
    
    patterns['engagement_trends'] = range_performance
    
    return patterns

def identify_optimal_content_features(video_performances):
    """Identify features that correlate with high performance"""
    features = {
        'optimal_title_length': None,
        'effective_tags': [],
        'performance_indicators': {}
    }
    
    if video_performances:
        # Analyse title lengths
        high_performers = [v for v in video_performances if v['performance_score'] > 70]
        if high_performers:
            avg_title_length = sum(len(v['title']) for v in high_performers) / len(high_performers)
            features['optimal_title_length'] = round(avg_title_length, 0)
        
        # Analyse common tags in high performers
        tag_performance = {}
        for video in high_performers:
            for tag in video['tags']:
                if tag not in tag_performance:
                    tag_performance[tag] = []
                tag_performance[tag].append(video['performance_score'])
        
        # Get tags with consistently high performance
        effective_tags = []
        for tag, scores in tag_performance.items():
            if len(scores) >= 2 and sum(scores) / len(scores) > 75:
                effective_tags.append({
                    'tag': tag,
                    'avg_score': round(sum(scores) / len(scores), 2),
                    'usage_count': len(scores)
                })
        
        features['effective_tags'] = sorted(effective_tags, 
                                          key=lambda x: x['avg_score'], 
                                          reverse=True)[:10]
    
    return features

def identify_trending_topics(video_performances):
    """Identify trending topics based on recent performance"""
    # This would typically analyse recent videos and their performance
    # For now, return a simplified analysis
    trending = []
    
    recent_videos = sorted(video_performances, 
                          key=lambda x: x['views'], 
                          reverse=True)[:10]
    
    for video in recent_videos:
        if video['performance_score'] > 60:
            trending.append({
                'title': video['title'],
                'performance_score': video['performance_score'],
                'views': video['views'],
                'tags': video['tags'][:3]  # Top 3 tags
            })
    
    return trending

def generate_content_recommendations(preferences):
    """Generate content strategy recommendations"""
    recommendations = []
    
    if 'content_categories' in preferences:
        categories = preferences['content_categories']
        
        # Find best performing category
        if categories:
            best_category = max(categories.items(), 
                              key=lambda x: x[1].get('avg_performance_score', 0))
            
            recommendations.append({
                'type': 'content_focus',
                'priority': 'high',
                'title': f'Focus on {best_category[0]} Content',
                'description': f'{best_category[0]} content shows the highest average performance score of {best_category[1].get("avg_performance_score", 0):.1f}.'
            })
    
    if 'engagement_patterns' in preferences:
        patterns = preferences['engagement_patterns']
        
        if patterns.get('optimal_video_length'):
            optimal = patterns['optimal_video_length']
            recommendations.append({
                'type': 'video_length',
                'priority': 'medium',
                'title': f'Optimize Video Length',
                'description': f'{optimal["range"].title()} videos show the best engagement rates at {optimal["avg_engagement"]:.1f}%.'
            })
    
    return recommendations

# Additional helper functions

def format_age_group_label(age_group):
    """Format age group codes into readable labels"""
    age_labels = {
        'age13-17': '13-17 years',
        'age18-24': '18-24 years',
        'age25-34': '25-34 years',
        'age35-44': '35-44 years',
        'age45-54': '45-54 years',
        'age55-64': '55-64 years',
        'age65-': '65+ years'
    }
    return age_labels.get(age_group, age_group)

def get_country_name(country_code):
    """Convert country code to country name"""
    # This would typically use a comprehensive country code mapping
    country_names = {
        'US': 'United States',
        'GB': 'United Kingdom',
        'CA': 'Canada',
        'AU': 'Australia',
        'DE': 'Germany',
        'FR': 'France',
        'JP': 'Japan',
        'IN': 'India',
        'BR': 'Brazil',
        'MX': 'Mexico'
        # Add more as needed
    }
    return country_names.get(country_code, country_code)

def find_significant_drop_offs(retention_data):
    """Find significant drop-off points in retention data"""
    drop_offs = []
    retention_points = list(retention_data.items())
    
    for i in range(1, len(retention_points)):
        prev_retention = retention_points[i-1][1]
        curr_retention = retention_points[i][1]
        
        # Consider a drop of more than 10% as significant
        if prev_retention - curr_retention > 10:
            drop_offs.append({
                'time_ratio': retention_points[i][0],
                'drop_percentage': prev_retention - curr_retention
            })
    
    return drop_offs

def calculate_engagement_score(retention_points):
    """Calculate an engagement score based on retention curve"""
    if not retention_points:
        return 0
    
    # Weight later retention points more heavily
    weighted_score = 0
    total_weight = 0
    
    for i, retention in enumerate(retention_points):
        weight = i + 1
        weighted_score += retention * weight
        total_weight += weight
    
    return round(weighted_score / total_weight, 2) if total_weight > 0 else 0

def generate_audience_summary(insights):
    """Generate summary insights from comprehensive audience data"""
    summary = {
        'key_demographics': {},
        'top_insights': [],
        'growth_indicators': {},
        'recommendations': []
    }
    
    # Analyse demographics
    if 'demographics' in insights and insights['demographics']:
        demo = insights['demographics']
        
        if 'age_groups' in demo:
            top_age_group = max(demo['age_groups'].items(), 
                              key=lambda x: x[1]['percentage'], default=(None, None))
            if top_age_group[0]:
                summary['key_demographics']['primary_age_group'] = {
                    'group': top_age_group[1]['label'],
                    'percentage': top_age_group[1]['percentage']
                }
        
        if 'gender' in demo:
            gender_split = demo['gender']
            summary['key_demographics']['gender_split'] = gender_split
        
        if 'countries' in demo:
            top_country = max(demo['countries'].items(), 
                            key=lambda x: x[1]['percentage'], default=(None, None))
            if top_country[0]:
                summary['key_demographics']['top_country'] = {
                    'name': top_country[1]['name'],
                    'percentage': top_country[1]['percentage']
                }
    
    return summary

def generate_retention_recommendations(retention_data):
    """Generate actionable recommendations based on retention analysis"""
    recommendations = []
    
    if 'overall_patterns' in retention_data:
        patterns = retention_data['overall_patterns']
        
        if patterns.get('average_retention', 0) < 40:
            recommendations.append({
                'type': 'retention_improvement',
                'priority': 'high',
                'title': 'Improve Video Hooks',
                'description': 'Your average retention is below 40%. Focus on creating stronger opening hooks in the first 15 seconds.'
            })
        
        if patterns.get('common_drop_off_points'):
            recommendations.append({
                'type': 'content_structure',
                'priority': 'medium',
                'title': 'Optimize Content Structure',
                'description': 'Analyse common drop-off points and restructure content to maintain engagement at these critical moments.'
            })
    
    return recommendations

def generate_engagement_recommendations(patterns):
    """Generate recommendations based on engagement patterns"""
    recommendations = []
    
    if 'temporal_patterns' in patterns and patterns['temporal_patterns'].get('weekly_patterns'):
        weekly = patterns['temporal_patterns']['weekly_patterns']
        
        # Find best performing day
        best_day = max(weekly.items(), key=lambda x: x[1].get('avg_engagement_rate', 0))
        
        recommendations.append({
            'type': 'posting_schedule',
            'priority': 'medium',
            'title': f'Optimize Posting Schedule',
            'description': f'{best_day[0]} shows the highest engagement rate. Consider posting more content on this day.'
        })
    
    return recommendations


import requests
import statistics
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import json

def analyse_common_drop_offs(drop_off_points):
    """Analyse common drop-off points across videos to identify patterns"""
    if not drop_off_points:
        return {}
    
    # Group drop-offs by time ranges (10% intervals)
    time_buckets = defaultdict(list)
    
    for drop_off in drop_off_points:
        # Convert to 10% buckets (0-10%, 10-20%, etc.)
        bucket = int(drop_off['time_ratio'] * 10) * 10
        time_buckets[f"{bucket}-{bucket+10}%"].append(drop_off['severity'])
    
    # Find most common drop-off periods
    common_patterns = {}
    for bucket, severities in time_buckets.items():
        if len(severities) >= 2:  # At least 2 videos show this pattern
            common_patterns[bucket] = {
                'frequency': len(severities),
                'average_severity': round(statistics.mean(severities), 2),
                'max_severity': max(severities)
            }
    
    # Sort by frequency and severity
    sorted_patterns = dict(sorted(
        common_patterns.items(), 
        key=lambda x: (x[1]['frequency'], x[1]['average_severity']), 
        reverse=True
    ))
    
    return {
        'most_common_drop_offs': sorted_patterns,
        'total_drop_off_events': len(drop_off_points),
        'critical_periods': [k for k, v in sorted_patterns.items() 
                           if v['average_severity'] > 15]  # >15% drop
    }

def calculate_optimal_length(video_durations, video_analysis):
    """Calculate optimal video length based on retention performance"""
    if not video_durations or not video_analysis:
        return {}
    
    # Group videos by duration ranges
    duration_performance = defaultdict(list)
    
    for video_id, analysis in video_analysis.items():
        duration = analysis.get('duration', 0)
        avg_retention = analysis.get('average_retention', 0)
        engagement_score = analysis.get('engagement_score', 0)
        
        if duration > 0:
            # Categorize by duration
            if duration <= 60:
                category = "0-1 min"
            elif duration <= 180:
                category = "1-3 min"
            elif duration <= 300:
                category = "3-5 min"
            elif duration <= 600:
                category = "5-10 min"
            elif duration <= 1200:
                category = "10-20 min"
            else:
                category = "20+ min"
            
            duration_performance[category].append({
                'retention': avg_retention,
                'engagement': engagement_score,
                'duration': duration
            })
    
    # Calculate performance metrics for each category
    category_stats = {}
    for category, videos in duration_performance.items():
        if videos:
            retentions = [v['retention'] for v in videos]
            engagements = [v['engagement'] for v in videos]
            durations = [v['duration'] for v in videos]
            
            category_stats[category] = {
                'video_count': len(videos),
                'avg_retention': round(statistics.mean(retentions), 2),
                'avg_engagement': round(statistics.mean(engagements), 2),
                'avg_duration': round(statistics.mean(durations), 1),
                'performance_score': round(
                    (statistics.mean(retentions) + statistics.mean(engagements)) / 2, 2
                )
            }
    
    # Find optimal range
    best_category = max(category_stats.items(), 
                       key=lambda x: x[1]['performance_score']) if category_stats else None
    
    return {
        'duration_analysis': category_stats,
        'optimal_range': best_category[0] if best_category else "Insufficient data",
        'optimal_performance_score': best_category[1]['performance_score'] if best_category else 0,
        'recommendation': generate_length_recommendation(category_stats)
    }

def calculate_retention_trend(video_analysis):
    """Calculate retention trends over time"""
    if not video_analysis:
        return {}
    
    # Sort videos by some identifier (assuming video_id contains timestamp info)
    # In real implementation, you'd sort by publish date
    video_list = list(video_analysis.items())
    
    # Calculate trend metrics
    retentions = [analysis['average_retention'] for _, analysis in video_list]
    engagement_scores = [analysis['engagement_score'] for _, analysis in video_list]
    
    if len(retentions) < 2:
        return {'trend': 'insufficient_data'}
    
    # Simple trend calculation
    retention_trend = calculate_trend_direction(retentions)
    engagement_trend = calculate_trend_direction(engagement_scores)
    
    # Identify improvement patterns
    recent_performance = statistics.mean(retentions[-5:]) if len(retentions) >= 5 else statistics.mean(retentions)
    early_performance = statistics.mean(retentions[:5]) if len(retentions) >= 5 else statistics.mean(retentions)
    
    return {
        'retention_trend': retention_trend,
        'engagement_trend': engagement_trend,
        'improvement_rate': round(((recent_performance - early_performance) / early_performance) * 100, 2) if early_performance > 0 else 0,
        'consistency_score': round(100 - (statistics.stdev(retentions) / statistics.mean(retentions)) * 100, 2) if retentions else 0,
        'recent_avg_retention': round(recent_performance, 2),
        'overall_avg_retention': round(statistics.mean(retentions), 2)
    }

def get_content_type_engagement(creds, start_date, end_date):
    """Analyse engagement by content type (inferred from titles/descriptions)"""
    try:
        # Get video list with details
        videos_response = requests.get(
            'https://youtubeanalytics.googleapis.com/v2/reports',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'ids': 'channel==MINE',
                'startDate': start_date,
                'endDate': end_date,
                'metrics': 'views,likes,comments,shares,subscribersGained,averageViewDuration',
                'dimensions': 'video',
                'maxResults': 50
            }
        )
        
        if videos_response.status_code != 200:
            return {'error': 'Failed to fetch video data'}
        
        data = videos_response.json()
        content_types = defaultdict(list)
        
        # Analyse each video
        for row in data.get('rows', []):
            video_id = row[0]
            metrics = {
                'views': row[1],
                'likes': row[2],
                'comments': row[3],
                'shares': row[4],
                'subscribers_gained': row[5],
                'avg_view_duration': row[6]
            }
            
            # Get video details for content type classification
            video_details = get_video_details(video_id, creds)
            content_type = classify_content_type(video_details)
            
            # Calculate engagement rate
            engagement_rate = ((metrics['likes'] + metrics['comments'] + metrics['shares']) / metrics['views'] * 100) if metrics['views'] > 0 else 0
            
            content_types[content_type].append({
                'video_id': video_id,
                'metrics': metrics,
                'engagement_rate': engagement_rate
            })
        
        # Aggregate by content type
        type_performance = {}
        for content_type, videos in content_types.items():
            if videos:
                type_performance[content_type] = {
                    'video_count': len(videos),
                    'avg_views': round(statistics.mean([v['metrics']['views'] for v in videos])),
                    'avg_engagement_rate': round(statistics.mean([v['engagement_rate'] for v in videos]), 2),
                    'avg_watch_time': round(statistics.mean([v['metrics']['avg_view_duration'] for v in videos]), 1),
                    'total_subscribers_gained': sum([v['metrics']['subscribers_gained'] for v in videos])
                }
        
        return {
            'content_type_performance': type_performance,
            'top_performing_type': max(type_performance.items(), key=lambda x: x[1]['avg_engagement_rate'])[0] if type_performance else None
        }
        
    except Exception as e:
        return {'error': str(e)}

def get_detailed_engagement_metrics(creds, start_date, end_date):
    """Get comprehensive engagement metrics"""
    try:
        # Fetch comprehensive metrics
        response = requests.get(
            'https://youtubeanalytics.googleapis.com/v2/reports',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'ids': 'channel==MINE',
                'startDate': start_date,
                'endDate': end_date,
                'metrics': 'views,likes,dislikes,comments,shares,subscribersGained,subscribersLost,estimatedMinutesWatched,averageViewDuration,annotationClickThroughRate',
                'dimensions': 'day'
            }
        )
        
        if response.status_code != 200:
            return {'error': 'Failed to fetch engagement data'}
        
        data = response.json()
        daily_metrics = []
        
        for row in data.get('rows', []):
            date = row[0]
            metrics = {
                'date': date,
                'views': row[1],
                'likes': row[2],
                'dislikes': row[3] if len(row) > 3 else 0,
                'comments': row[4] if len(row) > 4 else row[3],
                'shares': row[5] if len(row) > 5 else row[4],
                'subscribers_gained': row[6] if len(row) > 6 else row[5],
                'subscribers_lost': row[7] if len(row) > 7 else 0,
                'watch_time_minutes': row[8] if len(row) > 8 else row[6],
                'avg_view_duration': row[9] if len(row) > 9 else row[7]
            }
            
            # Calculate derived metrics
            metrics['engagement_rate'] = ((metrics['likes'] + metrics['comments'] + metrics['shares']) / metrics['views'] * 100) if metrics['views'] > 0 else 0
            metrics['like_ratio'] = (metrics['likes'] / (metrics['likes'] + metrics['dislikes']) * 100) if (metrics['likes'] + metrics['dislikes']) > 0 else 0
            metrics['net_subscribers'] = metrics['subscribers_gained'] - metrics['subscribers_lost']
            
            daily_metrics.append(metrics)
        
        # Calculate aggregated insights
        if daily_metrics:
            total_views = sum([m['views'] for m in daily_metrics])
            total_engagement = sum([m['likes'] + m['comments'] + m['shares'] for m in daily_metrics])
            
            return {
                'daily_metrics': daily_metrics,
                'summary': {
                    'total_views': total_views,
                    'total_engagement_actions': total_engagement,
                    'overall_engagement_rate': round((total_engagement / total_views * 100), 2) if total_views > 0 else 0,
                    'avg_daily_views': round(statistics.mean([m['views'] for m in daily_metrics])),
                    'peak_engagement_day': max(daily_metrics, key=lambda x: x['engagement_rate'])['date'],
                    'total_net_subscribers': sum([m['net_subscribers'] for m in daily_metrics])
                }
            }
        
        return {'error': 'No data available'}
        
    except Exception as e:
        return {'error': str(e)}

def get_subscriber_engagement_comparison(creds, start_date, end_date):
    """Compare engagement between subscribers and non-subscribers"""
    try:
        # Get subscriber engagement data
        subscriber_response = requests.get(
            'https://youtubeanalytics.googleapis.com/v2/reports',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'ids': 'channel==MINE',
                'startDate': start_date,
                'endDate': end_date,
                'metrics': 'views,likes,comments,shares,averageViewDuration',
                'filters': 'subscribedStatus==SUBSCRIBED'
            }
        )
        
        # Get non-subscriber engagement data
        non_subscriber_response = requests.get(
            'https://youtubeanalytics.googleapis.com/v2/reports',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'ids': 'channel==MINE',
                'startDate': start_date,
                'endDate': end_date,
                'metrics': 'views,likes,comments,shares,averageViewDuration',
                'filters': 'subscribedStatus==UNSUBSCRIBED'
            }
        )
        
        def process_response(response):
            if response.status_code == 200:
                data = response.json()
                if data.get('rows'):
                    row = data['rows'][0]
                    return {
                        'views': row[0],
                        'likes': row[1],
                        'comments': row[2],
                        'shares': row[3],
                        'avg_view_duration': row[4]
                    }
            return None
        
        subscriber_data = process_response(subscriber_response)
        non_subscriber_data = process_response(non_subscriber_response)
        
        if not subscriber_data or not non_subscriber_data:
            return {'error': 'Insufficient data for comparison'}
        
        # Calculate engagement rates
        def calc_engagement_rate(data):
            total_engagements = data['likes'] + data['comments'] + data['shares']
            return (total_engagements / data['views'] * 100) if data['views'] > 0 else 0
        
        subscriber_engagement_rate = calc_engagement_rate(subscriber_data)
        non_subscriber_engagement_rate = calc_engagement_rate(non_subscriber_data)
        
        return {
            'subscriber_metrics': {
                **subscriber_data,
                'engagement_rate': round(subscriber_engagement_rate, 2)
            },
            'non_subscriber_metrics': {
                **non_subscriber_data,
                'engagement_rate': round(non_subscriber_engagement_rate, 2)
            },
            'comparison': {
                'engagement_rate_difference': round(subscriber_engagement_rate - non_subscriber_engagement_rate, 2),
                'view_duration_difference': round(subscriber_data['avg_view_duration'] - non_subscriber_data['avg_view_duration'], 1),
                'subscriber_loyalty_score': round((subscriber_engagement_rate / non_subscriber_engagement_rate), 2) if non_subscriber_engagement_rate > 0 else 0
            }
        }
        
    except Exception as e:
        return {'error': str(e)}

def get_interaction_patterns(creds, start_date, end_date):
    """Analyse interaction timing and patterns"""
    try:
        # Get hourly engagement data
        response = requests.get(
            'https://youtubeanalytics.googleapis.com/v2/reports',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'ids': 'channel==MINE',
                'startDate': start_date,
                'endDate': end_date,
                'metrics': 'views,likes,comments,shares',
                'dimensions': 'day,hour'
            }
        )
        
        if response.status_code != 200:
            return {'error': 'Failed to fetch interaction data'}
        
        data = response.json()
        hourly_patterns = defaultdict(lambda: {'views': 0, 'likes': 0, 'comments': 0, 'shares': 0})
        daily_patterns = defaultdict(lambda: {'views': 0, 'likes': 0, 'comments': 0, 'shares': 0})
        
        for row in data.get('rows', []):
            day = row[0]
            hour = row[1] if len(row) > 1 else 0
            views = row[2] if len(row) > 2 else row[1]
            likes = row[3] if len(row) > 3 else row[2]
            comments = row[4] if len(row) > 4 else row[3]
            shares = row[5] if len(row) > 5 else row[4]
            
            # Group by hour (0-23)
            hourly_patterns[hour]['views'] += views
            hourly_patterns[hour]['likes'] += likes
            hourly_patterns[hour]['comments'] += comments
            hourly_patterns[hour]['shares'] += shares
            
            # Group by day of week
            day_of_week = datetime.strptime(day, '%Y-%m-%d').strftime('%A')
            daily_patterns[day_of_week]['views'] += views
            daily_patterns[day_of_week]['likes'] += likes
            daily_patterns[day_of_week]['comments'] += comments
            daily_patterns[day_of_week]['shares'] += shares
        
        # Find peak interaction times
        peak_hour = max(hourly_patterns.items(), key=lambda x: x[1]['views'])[0] if hourly_patterns else 0
        peak_day = max(daily_patterns.items(), key=lambda x: x[1]['views'])[0] if daily_patterns else 'Unknown'
        
        return {
            'hourly_patterns': dict(hourly_patterns),
            'daily_patterns': dict(daily_patterns),
            'peak_interaction_time': {
                'hour': peak_hour,
                'day': peak_day
            },
            'engagement_distribution': {
                'morning_hours': sum([v['views'] for h, v in hourly_patterns.items() if 6 <= h <= 11]),
                'afternoon_hours': sum([v['views'] for h, v in hourly_patterns.items() if 12 <= h <= 17]),
                'evening_hours': sum([v['views'] for h, v in hourly_patterns.items() if 18 <= h <= 23]),
                'night_hours': sum([v['views'] for h, v in hourly_patterns.items() if h < 6 or h > 23])
            }
        }
        
    except Exception as e:
        return {'error': str(e)}

def get_watch_time_patterns(creds, start_date, end_date):
    """Analyse watch time patterns and behaviours"""
    try:
        # Get watch time metrics
        response = requests.get(
            'https://youtubeanalytics.googleapis.com/v2/reports',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'ids': 'channel==MINE',
                'startDate': start_date,
                'endDate': end_date,
                'metrics': 'estimatedMinutesWatched,averageViewDuration,views',
                'dimensions': 'video'
            }
        )
        
        if response.status_code != 200:
            return {'error': 'Failed to fetch watch time data'}
        
        data = response.json()
        video_watch_patterns = []
        
        for row in data.get('rows', []):
            video_id = row[0]
            watch_time = row[1]  # in minutes
            avg_duration = row[2]  # in seconds
            views = row[3]
            
            # Get video details for duration
            video_details = get_video_details(video_id, creds)
            video_duration = video_details.get('duration', 0)
            
            # Calculate watch time metrics
            if video_duration > 0:
                retention_rate = (avg_duration / video_duration) * 100
                watch_time_per_view = watch_time / views if views > 0 else 0
                
                video_watch_patterns.append({
                    'video_id': video_id,
                    'title': video_details.get('title', 'Unknown'),
                    'total_watch_time': watch_time,
                    'avg_view_duration': avg_duration,
                    'video_duration': video_duration,
                    'retention_rate': round(retention_rate, 2),
                    'views': views,
                    'watch_time_per_view': round(watch_time_per_view, 2)
                })
        
        if not video_watch_patterns:
            return {'error': 'No watch time data available'}
        
        # Calculate overall patterns
        total_watch_time = sum([v['total_watch_time'] for v in video_watch_patterns])
        avg_retention = statistics.mean([v['retention_rate'] for v in video_watch_patterns])
        
        # Identify patterns
        high_retention_videos = [v for v in video_watch_patterns if v['retention_rate'] > avg_retention]
        low_retention_videos = [v for v in video_watch_patterns if v['retention_rate'] < avg_retention * 0.7]
        
        return {
            'total_watch_time_minutes': total_watch_time,
            'average_retention_rate': round(avg_retention, 2),
            'video_performance': video_watch_patterns,
            'high_retention_videos': len(high_retention_videos),
            'low_retention_videos': len(low_retention_videos),
            'watch_time_distribution': {
                'top_10_percent': sum([v['total_watch_time'] for v in sorted(video_watch_patterns, key=lambda x: x['total_watch_time'], reverse=True)[:max(1, len(video_watch_patterns)//10)]]),
                'bottom_50_percent': sum([v['total_watch_time'] for v in sorted(video_watch_patterns, key=lambda x: x['total_watch_time'])[len(video_watch_patterns)//2:]])
            }
        }
        
    except Exception as e:
        return {'error': str(e)}

# Helper functions
def find_significant_drop_offs(retention_curve):
    """Find significant drop-offs in retention curve"""
    drop_offs = []
    retention_points = list(retention_curve.items())
    
    for i in range(1, len(retention_points)):
        current_time, current_retention = retention_points[i]
        prev_time, prev_retention = retention_points[i-1]
        
        # Check for significant drop (>10% decrease)
        if prev_retention - current_retention > 10:
            drop_offs.append({
                'time_ratio': current_time,
                'retention_before': prev_retention,
                'retention_after': current_retention,
                'severity': prev_retention - current_retention
            })
    
    return drop_offs

def calculate_engagement_score(retention_points):
    """Calculate engagement score based on retention curve"""
    if not retention_points:
        return 0
    
    # Weighted score: early retention more important
    weights = [1.0 - (i / len(retention_points)) * 0.5 for i in range(len(retention_points))]
    weighted_score = sum(r * w for r, w in zip(retention_points, weights)) / sum(weights)
    
    return round(weighted_score, 2)

def get_video_details(video_id, creds):
    """Get video details from YouTube API"""
    try:
        response = requests.get(
            f'https://www.googleapis.com/youtube/v3/videos',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'part': 'snippet,contentDetails',
                'id': video_id
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('items'):
                item = data['items'][0]
                duration_str = item['contentDetails']['duration']
                duration_seconds = parse_duration(duration_str)
                
                return {
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'duration': duration_seconds
                }
    except Exception:
        pass
    
    return {'title': 'Unknown', 'description': '', 'duration': 0}

def parse_duration(duration_str):
    """Parse YouTube duration format (PT1H2M3S) to seconds"""
    import re
    
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, duration_str)
    
    if match:
        hours = int(match.group(1)) if match.group(1) else 0
        minutes = int(match.group(2)) if match.group(2) else 0
        seconds = int(match.group(3)) if match.group(3) else 0
        return hours * 3600 + minutes * 60 + seconds
    
    return 0

def classify_content_type(video_details):
    """Classify content type based on title and description"""
    title = video_details.get('title', '').lower()
    description = video_details.get('description', '').lower()
    
    keywords = {
        'tutorial': ['tutorial', 'how to', 'guide', 'learn', 'lesson'],
        'review': ['review', 'unboxing', 'test', 'comparison'],
        'entertainment': ['funny', 'comedy', 'entertainment', 'fun'],
        'vlog': ['vlog', 'daily', 'life', 'day in'],
        'gaming': ['gaming', 'gameplay', 'game', 'play'],
        'educational': ['education', 'explain', 'science', 'facts']
    }
    
    for content_type, words in keywords.items():
        if any(word in title or word in description for word in words):
            return content_type
    
    return 'other'

def calculate_trend_direction(values):
    """Calculate trend direction from a list of values"""
    if len(values) < 2:
        return 'stable'
    
    # Simple linear trend
    n = len(values)
    x_values = list(range(n))
    
    # Calculate slope
    x_mean = statistics.mean(x_values)
    y_mean = statistics.mean(values)
    
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
    denominator = sum((x - x_mean) ** 2 for x in x_values)
    
    if denominator == 0:
        return 'stable'
    
    slope = numerator / denominator
    
    if slope > 0.1:
        return 'improving'
    elif slope < -0.1:
        return 'declining'
    else:
        return 'stable'

def generate_length_recommendation(category_stats):
    """Generate video length recommendation based on performance"""
    if not category_stats:
        return "Insufficient data for recommendation"
    
    best_performing = max(category_stats.items(), key=lambda x: x[1]['performance_score'])
    
    return f"Based on your content performance, {best_performing[0]} videos show the best engagement rates. Consider focusing on this duration range for optimal audience retention."

def generate_retention_recommendations(retention_data):
    """Generate recommendations based on retention analysis"""
    recommendations = []
    
    patterns = retention_data.get('overall_patterns', {})
    avg_retention = patterns.get('average_retention', 0)
    
    if avg_retention < 30:
        recommendations.append("Focus on stronger video openings - your average retention suggests viewers drop off early")
    
    if patterns.get('common_drop_off_points'):
        recommendations.append("Address common drop-off points around the identified time ranges")
    
    optimal_length = patterns.get('optimal_video_length', {})
    if optimal_length.get('recommendation'):
        recommendations.append(optimal_length['recommendation'])
    
    return recommendations

def generate_engagement_recommendations(patterns):
    """Generate engagement recommendations based on pattern analysis"""
    recommendations = []
    
    # Analyse peak times
    interaction_patterns = patterns.get('interaction_patterns', {})
    if interaction_patterns.get('peak_interaction_time'):
        peak = interaction_patterns['peak_interaction_time']
        recommendations.append(f"Consider posting content on {peak['day']}s around {peak['hour']}:00 for maximum engagement")
    
    # Analyse subscriber engagement
    subscriber_comparison = patterns.get('subscriber_vs_non_subscriber', {})
    if subscriber_comparison.get('comparison', {}).get('engagement_rate_difference', 0) < 0:
        recommendations.append("Focus on content that better engages your existing subscriber base")
    
    return recommendations



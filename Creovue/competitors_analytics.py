# =============================================================================
# COMPETITOR ANALYSIS
# =============================================================================


from Creovue.models.trends import get_all_regions
from .models.channel_health import CompetitorAnalysis

from flask import render_template, request, jsonify
from flask_security import login_required, current_user
from . import app
#from .competitors_analytics import ( add_competitor_tracking, analyse_competitor, get_competitor_benchmarks, get_user_competitors)

@app.route('/competitors')
@login_required
def competitor_dashboard():
    """Competitor analysis dashboard"""
    competitors = get_user_competitors(current_user.id)
    return render_template('competitor_dashboard.html', competitors=competitors)

@app.route('/api/competitors/add', methods=['POST'])
@login_required
def add_competitor():
    """Add a competitor for tracking"""
    data = request.json
    competitor_channel = data.get('channel_id') or data.get('channel_url')
    
    if not competitor_channel:
        return jsonify({"error": "Channel ID or URL required"}), 400
    
    try:
        competitor = add_competitor_tracking(current_user.id, competitor_channel)
        return jsonify({"success": True, "competitor": competitor})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/competitors/<competitor_id>/analysis')
@login_required
def competitor_analysis(competitor_id):
    """Get detailed competitor analysis"""
    try:
        analysis = analyse_competitor(competitor_id, current_user.channel_id)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/competitors/benchmarking')
@login_required
def competitor_benchmarking():
    """Compare performance against competitors"""
    timeframe = request.args.get('timeframe', '30d')
    
    try:
        benchmarks = get_competitor_benchmarks(current_user.id, timeframe)
        return render_template('competitor_benchmarking.html', benchmarks=benchmarks)
    except Exception as e:
        return render_template('competitor_benchmarking.html', error=str(e))



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


def  analyse_competitor_content(competitor_videos):
    pass

def get_user_subscriber_count(user_channel_id):
    pass

def calculate_user_avg_views(user_channel_id):
    pass

def  calculate_user_avg_engagement(user_channel_id):
    pass

def find_competitor_keywords(competitor_videos):
    pass

def generate_competitor_recommendations(comparison):
    pass

def get_top_performing_videos(user_channel_id, limit=10):
    pass

def get_competitor_videos(): #(competitor.competitor_channel_id):
    pass


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

def ensure_channel_id():
    pass

def get_recent_video_performance(channel_id, days=30):
    pass

def get_user_metrics(user_id, timeframe):
    pass
def get_competitor_metrics(competitor_channel_id, timeframe):
    pass
def add_competitor_tracking(user_id, competitor_channel):
    pass
def create_performance_alert():
    pass
def toggle_alert_status():
    pass
def get_notification_preferences():
    pass
def update_user_notification_preferences():
    pass
def analyse_thumbnail_effectiveness():
    pass
def calculate_goal_progress():
    pass
def create_new_ab_test():
    pass
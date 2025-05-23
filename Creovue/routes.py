#Review the routes and update the relevant url_for() in the dashboard.html: 
# Standard library imports
import os
import time
from datetime import datetime, timedelta, date

# Additional imports needed
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import json
import statistics

# Third-party imports
import requests
from flask import flash, redirect, render_template, request, jsonify, session, url_for
from flask_security import (
    Security, 
    SQLAlchemyUserDatastore, 
    login_required, 
    roles_required, 
    login_user, 
    current_user
)
from flask_security.utils import login_user
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from werkzeug.security import generate_password_hash



from flask import abort
from sqlalchemy import desc, func

# Add these model imports (you'll need to create these models)
from .models.channel_health import ChannelHealth, VideoPerformance, CompetitorAnalysis
from .models.audience import AudienceInsight, ContentPlan, Alert, Goal
from .models.notifications import NotificationPreference


from Creovue.utils.youtube_client import ensure_channel_id
from Creovue.utils.yt_api import calculate_ctr_metrics

# Local application imports
from . import app, google, oauth
from .models import db, User, Role
from .models.analytics import (
    get_channel_stats, 
    process_channel_analytics, 
    fetch_youtube_analytics, 
    generate_plot
)
from .models.seo import get_seo_recommendations
from .logic import extract_keywords
from .config import (
    creo_oauth_client_id,
    creo_oauth_client_secret,
    creo_google_redirect_uri,
    creo_google_auth_scope,
    creo_google_auth_uri,
    creo_google_token_uri,
    creo_channel_id,
    creo_api_key,
    creo_mock_view_history
)
from Creovue.models.trends import (
    clear_trend_cache,
    fetch_top_channels,
    fetch_trending_keywords,
    get_all_regions,
    get_available_categories,
    get_category_age_distribution,
    get_category_distribution,
    get_default_region,
    get_related_keywords,
    get_safe_region_code,
    get_top_channels,
    get_trend_chart_data,
    get_trending_keywords,
    get_trending_regions,
    visualise_category_age_distribution_base64
)

# Commented out import
# from .app_secets import creo_channel_id, creo_api_key, creo_mock_view_history

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # For localhost testing

# Setup Flask-Security
## Set up user datastore
user_datastore = SQLAlchemyUserDatastore(db, User, Role)

## Attach Security
security = Security(app, user_datastore)

from Creovue.thumbnail import thumbnail_eval_bp
app.register_blueprint(thumbnail_eval_bp)
"""
from Creovue.thumbnail_eval.face_detect import face_bp
app.register_blueprint(face_bp)"""

from Creovue.thumbnail import register_thumbnail_eval,  register_thumbnail_routes
register_thumbnail_routes(app)

register_thumbnail_eval(app)


@app.route("/admin")
@roles_required("Admin")
def admin_panel():
    return render_template("admin.html")

@app.route("/")
def home():
    return render_template("index.html")

# Dashboard route – personalised analytics

# Dashboard route – personalised analytics
@app.route("/dashboard")
@login_required
def dashboard():
    # ✅ Ensure channel_id is up to date
    ensure_channel_id()

    if not current_user.channel_id:
        return render_template("dashboard.html", stats=None)  # No data yet

    try:
        analytics = process_channel_analytics(current_user.channel_id)
        return render_template("dashboard.html", stats=analytics)
    except Exception as e:
        # Log error and show dashboard without stats
        print(f"[Dashboard Error] {e}")
        return render_template("dashboard.html", stats=None)




"""@app.route("/dashboard")
@login_required
def dashboard():
    # ✅ Ensure channel_id is up to date
    ensure_channel_id()

   

    if 1==1:
        analytics = process_channel_analytics(current_user.channel_id)
        return render_template("dashboard.html", stats=analytics)"""
   


@app.route('/seo', methods=['GET', 'POST'])
@login_required
def seo():
    keyword = None
    recommendations = None
    error = None
    if request.method == 'POST':
        keyword = request.form.get('keyword', '').strip()
        if keyword:
            try:
                recommendations = get_seo_recommendations(keyword)
            except Exception as e:
                error = f"Error fetching SEO data: {str(e)}"
        else:
            error = "Please enter a valid keyword."
    return render_template('seo.html', keyword=keyword, recommendations=recommendations, error=error)


"""@app.route('/trends')
def trends():
    trending_keywords = fetch_trending_keywords()
    top_channels = fetch_top_channels()
    trend_data = get_trend_chart_data()
    return render_template('trends.html', trending_keywords=trending_keywords, top_channels=top_channels, trend_data=trend_data)"""

@app.route("/trends")
@login_required
def trends():
    client_ip = None
    try:
        client_ip = request.remote_addr
    except :
        pass
    regions = get_all_regions()
    default_region = get_default_region(client_ip)
    #print("default_region: ", default_region); #time.sleep(300)
    categories = get_available_categories(creo_api_key, default_region)

    # Initial display uses default_region
    trending_keywords, keyword_age = get_trending_keywords(default_region, categories); 
    trending_keywords = fetch_trending_keywords(default_region)
    #print("trending_keywords: ", trending_keywords, "keyword_age: ",  keyword_age); time.sleep(300)
    category_distribution = get_category_distribution(default_region)
    category_age_distribution = get_category_age_distribution(default_region)
    #print("category_distribution: ", category_distribution, "category_age_distribution: ", category_age_distribution); time.sleep(300)
    top_channels, channel_data_age = get_top_channels(default_region)
    #print("top_channels", top_channels, "channel_age: ", channel_data_age); time.sleep(300)

    return render_template(
        "trends.html",
        page_title="Trending Insights",
        regions=regions,
        categories=categories,
        default_region=default_region,
        trending_keywords=trending_keywords,
        keyword_age=keyword_age,
        category_distribution=category_distribution,
        category_age=category_age_distribution,
        top_channels=top_channels,
        #channel_age=channel_age
    )

@app.route('/api/trend_data')
@login_required
def trend_data():
    client_ip = None
    try:
        client_ip = request.remote_addr
    except :
        pass
    default_region = get_default_region(client_ip)
    region = request.args.get("region", default_region)
    region = get_safe_region_code(region)

    category = request.args.get("category", None)

    
    categories = get_available_categories(creo_api_key, default_region)

    #trending_keywords, keyword_age = get_trending_keywords(region, category)
    #category_distribution, category_age = get_category_distribution(region)
    #top_channels, channel_age = get_top_channels(region)

    trending_keywords, keyword_age = get_trending_keywords(region, categories); 
    trending_keywords = fetch_trending_keywords(region)
    category_distribution = get_category_distribution(region)
    category_age_distribution = get_category_age_distribution(region)
    #top_channels, channel_data_age = get_top_channels(region)

    result = get_top_channels(region)
    if not result or len(result) != 2:
        top_channels, channel_data_age = [], None
    else:
        top_channels, channel_data_age = result

    
    return jsonify({
        "trending_keywords": trending_keywords,
        "keyword_age": keyword_age,
        "category_distribution": category_distribution,
        "category_age": category_age_distribution,
        "top_channels": top_channels,
        #"channel_age": channel_age
    })

@app.route("/category/age-visual")
@login_required
def category_age_visual():
    client_ip = None
    try:
        client_ip = request.remote_addr
    except :
        pass
    regions = get_all_regions()
    default_region = get_default_region(client_ip)
    #print("default_region: ", default_region); #time.sleep(300)
    categories = get_available_categories(creo_api_key, default_region)

    region = request.args.get("region", default_region)
    plot_img = visualise_category_age_distribution_base64(default_region)
    return render_template("age_visual.html", plot_img=plot_img, region=default_region)



@app.route('/analytics')
@login_required
def analytics():
    ensure_channel_id()

    if not current_user.channel_id:
        return render_template("dashboard.html", stats=None)  # No data yet

    # Fetch analytics data for the current user channel
    try:
        analytics_data = fetch_youtube_analytics(current_user.channel_id)
    except Exception as e:
        # Log error and fallback to default or empty data
        print(f"Error fetching analytics: {e}")
        analytics_data = {
            "total_views": 0,
            "subscriber_count": 0,
            "video_count": 0,
            "avg_watch_time": 0,
            "engagement_rate": 0,
            "daily_views": [0]*7
        }

    # Prepare last 7 days labels and values for chart
    x_labels = [(datetime.today() - timedelta(days=i)).strftime('%a') for i in reversed(range(7))]
    # Use only last 7 days of daily_views for chart
    y_values = analytics_data.get("daily_views", [0]*7)[-7:]

    # Calculate additional metrics
    avg_views_per_video = 0
    if analytics_data.get("video_count", 0) > 0:
        avg_views_per_video = round(analytics_data["total_views"] / analytics_data["video_count"], 2)

    chart_data = {
        "labels": x_labels,
        "values": y_values
    }

    ctr_metrics = calculate_ctr_metrics(current_user.channel_id, 700)
    #print("ctr_metrics: ", ctr_metrics)
    return render_template('analytics.html',
                           ctr_metrics=ctr_metrics,
                           analytics=analytics_data,
                           avg_views_per_video=avg_views_per_video,
                           chart_data=chart_data)





#@app.route("/analytics/overview")
#def video_analytics():
    #data = fetch_youtube_analytics(creo_channel_id)
    #chart = generate_plot(data)
    #return jsonify({"metrics": data, "chart_url": chart})


@app.route("/seo/keywords", methods=["POST"])
@login_required
def keyword_research():
    content = request.json['text']
    keywords = extract_keywords([content])
    return jsonify({"keywords": keywords})


# Initiate Google OAuth
@app.route('/google-login')
def google_login():
    next_url = request.args.get('next', url_for('dashboard'))
    session['next_url'] = next_url

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": creo_oauth_client_id,
                "client_secret": creo_oauth_client_secret,
                "auth_uri": creo_google_auth_uri,
                "token_uri": creo_google_token_uri,
                "redirect_uris": creo_google_redirect_uri,
            }
        },
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/youtube.readonly",
        ],
    )
    flow.redirect_uri = creo_google_redirect_uri
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt="consent"
    )
    session['oauth_state'] = state
    return redirect(auth_url)

# OAuth Callback Handler
@app.route('/oauth2callback')
def oauth2callback():
    state = session.get('oauth_state')
    if not state:
        return redirect(url_for('home'))

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": creo_oauth_client_id,
                "client_secret": creo_oauth_client_secret,
                "auth_uri": creo_google_auth_uri,
                "token_uri": creo_google_token_uri,
                "redirect_uris": creo_google_redirect_uri,
            }
        },
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/youtube.readonly",
            #"https://www.googleapis.com/auth/yt-analytics.readonly"
        ],
        state=state
    )
    flow.redirect_uri = creo_google_redirect_uri
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials

    # Fetch basic user info
    userinfo_resp = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={"Authorization": f"Bearer {credentials.token}"}
    )
    user_info = userinfo_resp.json()
    email = user_info.get("email")

    # Check or create user
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            email=email,
            username=email.split('@')[0],
            password=generate_password_hash(os.urandom(12).hex()),
            fs_uniquifier=os.urandom(16).hex(),
            active=True
        )
        db.session.add(user)
        db.session.commit()

    # Fetch and save channel ID to user (first time)
    if not user.channel_id:
        # After login_user(user)
        channel_resp = requests.get(
            'https://www.googleapis.com/youtube/v3/channels',
            headers={'Authorization': f'Bearer {credentials.token}'},
            params={'part': 'id', 'mine': 'true'}
        )
        channel_data = channel_resp.json()
        if channel_data.get('items'):
            user.channel_id = channel_data['items'][0]['id']
            db.session.commit()


    login_user(user)

    # Save token to session
    session['youtube_token'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    # ✅ Ensure channel_id is up to date
    ensure_channel_id()

    return redirect(session.pop('next_url', url_for('dashboard')))

# Personalised YouTube dashboard
@app.route('/youtube-dashboard')
@login_required
def youtube_dashboard():
    if 'youtube_token' not in session:
        return redirect(url_for('google_login', next=request.path))

    creds = Credentials(**session['youtube_token'])

    # --- 1. Fetch channel metadata ---
    channel_resp = requests.get(
        'https://www.googleapis.com/youtube/v3/channels',
        headers={'Authorization': f'Bearer {creds.token}'},
        params={'part': 'snippet,statistics', 'mine': 'true'}
    )
    channel_data = channel_resp.json()

    # 🔒 Check if 'items' exist
    items = channel_data.get('items', [])
    if not items:
        flash("No YouTube channel found or access denied. Please check your permissions.", "danger")
        return redirect(url_for("dashboard"))

    channel = items[0]

    # --- 2. Fetch top videos ---
    uploads_resp = requests.get(
        'https://www.googleapis.com/youtube/v3/search',
        headers={'Authorization': f'Bearer {creds.token}'},
        params={
            'part': 'snippet',
            'maxResults': 10,
            'order': 'viewCount',
            'type': 'video',
            'mine': 'true'
        }
    )
    uploads_data = uploads_resp.json()
    top_video_ids = [item['id']['videoId'] for item in uploads_data.get('items', []) if 'videoId' in item['id']]

    # --- 3. Fetch stats for top videos ---
    stats_data = []
    if top_video_ids:
        stats_resp = requests.get(
            'https://www.googleapis.com/youtube/v3/videos',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={
                'part': 'snippet,statistics',
                'id': ','.join(top_video_ids)
            }
        )
        stats_json = stats_resp.json()
        stats_data = [{
            'title': v['snippet']['title'],
            'views': int(v['statistics'].get('viewCount', 0))
        } for v in stats_json.get('items', [])]

    # --- 4. Simulate 7-day subscriber growth ---
    base_subs = int(channel['statistics'].get('subscriberCount', 1000))
    sub_growth = [base_subs - i * 20 for i in reversed(range(7))]

    return render_template('youtube_dashboard.html',
        data=channel_data,
        top_videos=stats_data,
        subscriber_trend=sub_growth,
        subscriber_labels=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    )




# =============================================================================
# CHANNEL OVERVIEW & HEALTH
# =============================================================================

@app.route('/channel/overview')
@login_required
def channel_overview():
    """Comprehensive channel health overview"""
    ensure_channel_id()
    
    if not current_user.channel_id:
        return render_template('channel_overview.html', error="No channel connected")
    
    try:
        # Get comprehensive channel health data
        health_data = get_channel_health_overview(current_user.channel_id)
        return render_template('channel_overview.html', health=health_data)
    except Exception as e:
        print(f"[Channel Overview Error] {e}")
        return render_template('channel_overview.html', error=str(e))

@app.route('/api/channel/health')
@login_required
def api_channel_health():
    """API endpoint for channel health metrics"""
    ensure_channel_id()
    
    if not current_user.channel_id:
        return jsonify({"error": "No channel connected"}), 400
    
    try:
        health_score = calculate_channel_health_score(current_user.channel_id)
        recommendations = get_health_recommendations(current_user.channel_id)
        
        return jsonify({
            "health_score": health_score,
            "recommendations": recommendations,
            "last_updated": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/channel/growth-analysis')
@login_required
def channel_growth_analysis():
    """Detailed growth analysis with predictions"""
    ensure_channel_id()
    
    if not current_user.channel_id:
        return render_template('growth_analysis.html', error="No channel connected")
    
    try:
        growth_data = analyse_channel_growth(current_user.channel_id)
        predictions = predict_channel_growth(current_user.channel_id)
        
        return render_template('growth_analysis.html', 
                             growth=growth_data, 
                             predictions=predictions)
    except Exception as e:
        return render_template('growth_analysis.html', error=str(e))

# =============================================================================
# VIDEO ANALYTICS & PERFORMANCE
# =============================================================================

@app.route('/videos/performance')
@login_required
def video_performance():
    """Individual video performance analysis"""
    ensure_channel_id()
    
    if not current_user.channel_id:
        return render_template('video_performance.html', error="No channel connected")
    
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'upload_date')
    
    try:
        videos = get_video_performance_data(current_user.channel_id, page, sort_by)
        return render_template('video_performance.html', videos=videos)
    except Exception as e:
        return render_template('video_performance.html', error=str(e))

@app.route('/api/video/<video_id>/analytics')
@login_required
def api_video_analytics(video_id):
    """Detailed analytics for a specific video"""
    try:
        analytics = get_detailed_video_analytics(video_id, current_user.channel_id)
        return jsonify(analytics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/videos/batch-analysis', methods=['POST'])
@login_required
def batch_video_analysis():
    """Analyse multiple videos at once"""
    video_ids = request.json.get('video_ids', [])
    
    if not video_ids:
        return jsonify({"error": "No video IDs provided"}), 400
    
    try:
        analysis = analyse_videos_batch(video_ids, current_user.channel_id)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/videos/performance-trends')
@login_required
def video_performance_trends():
    """Video performance trends over time"""
    ensure_channel_id()
    
    timeframe = request.args.get('timeframe', '30d')
    metric = request.args.get('metric', 'views')
    
    try:
        trends = get_video_performance_trends(current_user.channel_id, timeframe, metric)
        return render_template('performance_trends.html', trends=trends)
    except Exception as e:
        return render_template('performance_trends.html', error=str(e))

# =============================================================================
# SEO & DISCOVERY TOOLS (Enhanced)
# =============================================================================

@app.route('/seo/optimisation')
@login_required
def seo_optimisation():
    """SEO optimisation dashboard"""
    return render_template('seo_optimisation.html')

@app.route('/api/seo/video-optimisation', methods=['POST'])
@login_required
def api_video_seo_optimisation():
    """Optimise SEO for a specific video"""
    data = request.json
    video_id = data.get('video_id')
    target_keywords = data.get('keywords', [])
    
    try:
        optimisation = optimise_video_seo(video_id, target_keywords, current_user.channel_id)
        return jsonify(optimisation)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/seo/tag-generator', methods=['POST'])
@login_required
def tag_generator():
    """Generate optimised tags for video content"""
    data = request.json
    title = data.get('title', '')
    description = data.get('description', '')
    category = data.get('category', '')
    
    try:
        tags = generate_optimised_tags(title, description, category)
        return jsonify({"tags": tags})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/seo/title-optimiser', methods=['POST'])
@login_required
def title_optimiser():
    """Optimise video titles for better discovery"""
    data = request.json
    original_title = data.get('title', '')
    target_audience = data.get('audience', 'general')
    
    try:
        optimised_titles = optimise_video_title(original_title, target_audience)
        return jsonify({"optimised_titles": optimised_titles})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============================================================================
# COMPETITOR ANALYSIS
# =============================================================================

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

# =============================================================================
# AUDIENCE INSIGHTS
# =============================================================================

@app.route('/audience/insights')
@login_required
def audience_insights():
    """Comprehensive audience analysis"""
    ensure_channel_id()
    
    if not current_user.channel_id:
        return render_template('audience_insights.html', error="No channel connected")
    
    try:
        insights = get_comprehensive_audience_insights(current_user.channel_id)
        return render_template('audience_insights.html', insights=insights)
    except Exception as e:
        return render_template('audience_insights.html', error=str(e))

@app.route('/api/audience/demographics')
@login_required
def api_audience_demographics():
    """Get detailed audience demographics"""
    ensure_channel_id()
    
    try:
        demographics = get_audience_demographics(current_user.channel_id)
        return jsonify(demographics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/audience/engagement-patterns')
@login_required
def audience_engagement_patterns():
    """Analyse audience engagement patterns"""
    ensure_channel_id()
    
    try:
        patterns = analyse_engagement_patterns(current_user.channel_id)
        return render_template('engagement_patterns.html', patterns=patterns)
    except Exception as e:
        return render_template('engagement_patterns.html', error=str(e))

@app.route('/api/audience/retention-analysis')
@login_required
def api_audience_retention():
    """Analyse audience retention across videos"""
    video_ids = request.args.getlist('video_ids')
    
    try:
        retention = analyse_audience_retention(video_ids, current_user.channel_id)
        return jsonify(retention)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============================================================================
# CONTENT PLANNING & OPTIMISATION
# =============================================================================

@app.route('/content/planner')
@login_required
def content_planner():
    """Content planning dashboard"""
    plans = get_user_content_plans(current_user.id)
    return render_template('content_planner.html', plans=plans)

@app.route('/api/content/ideas', methods=['POST'])
@login_required
def generate_content_ideas():
    """Generate content ideas based on trends and performance"""
    data = request.json
    category = data.get('category', '')
    target_audience = data.get('audience', 'general')
    
    try:
        ideas = generate_content_suggestions(
            current_user.channel_id, 
            category, 
            target_audience
        )
        return jsonify({"ideas": ideas})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/content/optimal-timing')
@login_required
def optimal_timing():
    """Find optimal posting times"""
    ensure_channel_id()
    
    try:
        timing_data = analyse_optimal_posting_times(current_user.channel_id)
        return render_template('optimal_timing.html', timing=timing_data)
    except Exception as e:
        return render_template('optimal_timing.html', error=str(e))

@app.route('/api/content/schedule', methods=['POST'])
@login_required
def schedule_content():
    """Schedule content posting"""
    data = request.json
    
    try:
        schedule = create_content_schedule(current_user.id, data)
        return jsonify({"success": True, "schedule": schedule})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============================================================================
# ALERTS & NOTIFICATIONS
# =============================================================================

@app.route('/alerts')
@login_required
def alerts_dashboard():
    """Alerts and notifications dashboard"""
    alerts = get_user_alerts(current_user.id)
    return render_template('alerts_dashboard.html', alerts=alerts)

@app.route('/api/alerts/create', methods=['POST'])
@login_required
def create_alert():
    """Create a new alert"""
    data = request.json
    
    try:
        alert = create_performance_alert(current_user.id, data)
        return jsonify({"success": True, "alert": alert})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/alerts/<alert_id>/toggle', methods=['PUT'])
@login_required
def toggle_alert(alert_id):
    """Toggle alert on/off"""
    try:
        alert = toggle_alert_status(alert_id, current_user.id)
        return jsonify({"success": True, "alert": alert})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/notifications/preferences')
@login_required
def notification_preferences():
    """Notification preferences page"""
    preferences = get_notification_preferences(current_user.id)
    return render_template('notification_preferences.html', preferences=preferences)

@app.route('/api/notifications/preferences', methods=['PUT'])
@login_required
def update_notification_preferences():
    """Update notification preferences"""
    data = request.json
    
    try:
        preferences = update_user_notification_preferences(current_user.id, data)
        return jsonify({"success": True, "preferences": preferences})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============================================================================
# TOOLS & UTILITIES
# =============================================================================

@app.route('/tools')
@login_required
def tools_dashboard():
    """Tools and utilities dashboard"""
    return render_template('tools_dashboard.html')

@app.route('/tools/thumbnail-analyser')
@login_required
def thumbnail_analyser():
    """Thumbnail analysis tool"""
    return render_template('thumbnail_analyser.html')

@app.route('/api/tools/thumbnail/analyse', methods=['POST'])
@login_required
def analyse_thumbnail():
    """Analyse thumbnail effectiveness"""
    if 'thumbnail' not in request.files:
        return jsonify({"error": "No thumbnail uploaded"}), 400
    
    thumbnail = request.files['thumbnail']
    
    try:
        analysis = analyse_thumbnail_effectiveness(thumbnail)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tools/a-b-test')
@login_required
def ab_test_manager():
    """A/B test manager"""
    tests = get_user_ab_tests(current_user.id)
    return render_template('ab_test_manager.html', tests=tests)

@app.route('/api/tools/ab-test/create', methods=['POST'])
@login_required
def create_ab_test():
    """Create a new A/B test"""
    data = request.json
    
    try:
        test = create_new_ab_test(current_user.id, data)
        return jsonify({"success": True, "test": test})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tools/keyword-tracker')
@login_required
def keyword_tracker():
    """Keyword ranking tracker"""
    keywords = get_tracked_keywords(current_user.id)
    return render_template('keyword_tracker.html', keywords=keywords)

@app.route('/api/tools/keywords/track', methods=['POST'])
@login_required
def track_keyword():
    """Start tracking a keyword"""
    data = request.json
    keyword = data.get('keyword', '').strip()
    
    if not keyword:
        return jsonify({"error": "Keyword required"}), 400
    
    try:
        tracking = start_keyword_tracking(current_user.id, keyword)
        return jsonify({"success": True, "tracking": tracking})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============================================================================
# GOALS & PROGRESS TRACKING
# =============================================================================

@app.route('/goals')
@login_required
def goals_dashboard():
    """Goals and progress tracking dashboard"""
    goals = get_user_goals(current_user.id)
    return render_template('goals_dashboard.html', goals=goals)

@app.route('/api/goals/create', methods=['POST'])
@login_required
def create_goal():
    """Create a new goal"""
    data = request.json
    
    try:
        goal = create_user_goal(current_user.id, data)
        return jsonify({"success": True, "goal": goal})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/goals/<goal_id>/progress')
@login_required
def goal_progress(goal_id):
    """Get goal progress"""
    try:
        progress = calculate_goal_progress(goal_id, current_user.id)
        return jsonify(progress)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/goals/milestones')
@login_required
def milestones():
    """View achieved milestones"""
    milestones = get_user_milestones(current_user.id)
    return render_template('milestones.html', milestones=milestones)

# =============================================================================
# REPORTING & EXPORTS
# =============================================================================

@app.route('/reports')
@login_required
def reports_dashboard():
    """Reports dashboard"""
    reports = get_user_reports(current_user.id)
    return render_template('reports_dashboard.html', reports=reports)

@app.route('/api/reports/generate', methods=['POST'])
@login_required
def generate_report():
    """Generate a custom report"""
    data = request.json
    
    try:
        report = generate_analytics_report(current_user.id, data)
        return jsonify({"success": True, "report": report})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/export/<export_type>')
@login_required
def export_data(export_type):
    """Export data in various formats"""
    format_type = request.args.get('format', 'csv')
    
    try:
        export_data = export_analytics_data(
            current_user.id, 
            export_type, 
            format_type
        )
        return jsonify(export_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============================================================================
# HELPER FUNCTIONS (You'll need to implement these)
# =============================================================================

def get_channel_health_overview(channel_id):
    """Get comprehensive channel health data"""
    # Implementation needed
    pass

def calculate_channel_health_score(channel_id):
    """Calculate overall channel health score"""
    # Implementation needed
    pass

def get_health_recommendations(channel_id):
    """Get health improvement recommendations"""
    # Implementation needed
    pass

def analyse_channel_growth(channel_id):
    """Analyse historical growth patterns"""
    # Implementation needed
    pass

def predict_channel_growth(channel_id):
    """Predict future growth based on current trends"""
    # Implementation needed
    pass

def get_video_performance_data(channel_id, page, sort_by):
    """Get paginated video performance data"""
    # Implementation needed
    pass

def get_detailed_video_analytics(video_id, channel_id):
    """Get detailed analytics for a specific video"""
    # Implementation needed
    pass

def analyse_videos_batch(video_ids, channel_id):
    """Analyse multiple videos at once"""
    # Implementation needed
    pass

def get_video_performance_trends(channel_id, timeframe, metric):
    """Get video performance trends over time"""
    # Implementation needed
    pass

def optimise_video_seo(video_id, keywords, channel_id):
    """Optimise video SEO"""
    # Implementation needed
    pass

def generate_optimised_tags(title, description, category):
    """Generate optimised tags"""
    # Implementation needed
    pass

def optimise_video_title(title, audience):
    """Optimise video title"""
    # Implementation needed
    pass

# Additional helper functions would continue here...
# Each function would contain the specific logic for that feature


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

def get_user_metrics(user_id, timeframe):
    pass

def get_competitor_metrics(): #(competitor['channel_id'], timeframe):
    pass

def  get_comprehensive_audience_insights(): #(current_user.channel_id):
    pass


   
def get_audience_demographics(channel_id):
    """Get overall channel audience demographics"""
    try:
        creds = Credentials(**session['youtube_token'])
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
        
        demographics = {
            'age_groups': {},
            'gender': {},
            'last_updated': datetime.now().isoformat()
        }
        
        if age_response.status_code == 200:
            pass

    except:
        pass


def analyse_engagement_patterns(): #(current_user.channel_id):
    pass


def analyse_audience_retention(): #(video_ids, current_user.channel_id):
    pass

def get_user_content_plans(): #(current_user.id):
    pass

def  generate_content_suggestions(
            current_user, #.channel_id, 
            category, 
            target_audience
        ):
    pass

def process_channel_analytics_test(channel_id):
    # Stub: Replace with real analytics processing logic
    return {
        "total_views": 123456,
        "subscriber_count": 7890,
        "video_count": 42,
        "avg_watch_time": 5.5,
        "engagement_rate": 0.12,
        "daily_views": [100, 200, 150, 300, 250, 400, 350]
    }

def fetch_youtube_analytics_test(channel_id):
    # Stub: Replace with real YouTube Analytics API call
    return {
        "total_views": 123456,
        "subscriber_count": 7890,
        "video_count": 42,
        "avg_watch_time": 5.5,
        "engagement_rate": 0.12,
        "daily_views": [100, 200, 150, 300, 250, 400, 350]
    }

def calculate_ctr_metrics_test(channel_id, days):
    # Stub: Replace with real CTR calculation
    return {
        "avg_ctr": 0.045,
        "impressions": 100000,
        "clicks": 4500,
        "period_days": days
    }

def get_seo_recommendations_test(keyword):
    # Stub: Replace with real SEO recommendation logic
    return [
        {"keyword": f"{keyword} tutorial", "score": 85},
        {"keyword": f"{keyword} 2025", "score": 78},
        {"keyword": f"best {keyword} tips", "score": 80}
    ]

def extract_keywords(texts):
    # Stub: Replace with real keyword extraction logic
    content = " ".join(texts)
    words = set(content.lower().split())
    # Return top 5 unique words as 'keywords'
    return list(words)[:5]

def ensure_channel_id():
    # Stub: In real app, update current_user.channel_id if needed
    from flask_security import current_user
    if not hasattr(current_user, 'channel_id') or not current_user.channel_id:
        # For testing, assign a dummy channel ID
        current_user.channel_id = "UC1234567890abcdef"

def fetch_trending_keywords_test(region):
    # Stub: Replace with real trending keywords fetch
    return [f"trend_{region}_1", f"trend_{region}_2", f"trend_{region}_3"]

def get_trending_keywords_test(region, categories):
    # Stub: Returns trending keywords and their "age"
    keywords = [f"{region}_cat_{cat}_trend" for cat in categories[:3]]
    keyword_age = 2  # hours
    return keywords, keyword_age

def get_category_distribution_test(region):
    # Stub: Replace with real category distribution logic
    return {"Music": 25, "Gaming": 15, "Education": 10}

def get_category_age_distribution_test(region):
    # Stub: Replace with real category age distribution logic
    return {"Music": 2.5, "Gaming": 1.8, "Education": 3.0}

def get_top_channels_test(region):
    # Stub: Replace with real top channels fetch
    channels = [
        {"channel_id": "UC1", "name": "TopChannel1", "subs": 1000000},
        {"channel_id": "UC2", "name": "TopChannel2", "subs": 800000}
    ]
    channel_data_age = 1  # hours
    return channels, channel_data_age

def get_all_regions_test():
    # Stub: Replace with real region list
    return ["US", "GB", "IN", "NG"]

def get_default_region_test(client_ip):
    # Stub: Use IP to guess region (always returns 'US' here)
    return "US"

def get_available_categories_test(api_key, region):
    # Stub: Replace with real category fetch
    return ["Music", "Gaming", "Education"]

def get_safe_region_code(region):
    # Stub: Validate region code
    return region if region in get_all_regions() else "US"

def visualise_category_age_distribution_base64(region):
    # Stub: Return a placeholder base64 image string
    import base64
    dummy_image = b"fakeimagebytes"
    return base64.b64encode(dummy_image).decode("utf-8")


def add_competitor_tracking(user_id, competitor_channel_id):
    # Stub: Add a competitor channel to tracking list for a user
    return {"status": "success", "message": f"Competitor {competitor_channel_id} added for user {user_id}"}

def analyse_optimal_posting_times(channel_id):
    # Stub: Return best times to post based on dummy data
    return {
        "best_days": ["Wednesday", "Saturday"],
        "best_hours": [15, 18]  # 3pm, 6pm
    }

def create_content_schedule(user_id, schedule_details):
    # Stub: Save a content schedule for a user
    return {"status": "success", "schedule": schedule_details}

def get_user_alerts(user_id):
    # Stub: Return a list of alerts for the user
    return [
        {"id": 1, "type": "performance", "message": "Views dropped by 20%", "active": True},
        {"id": 2, "type": "goal", "message": "Goal reached!", "active": False}
    ]

def create_performance_alert(user_id, alert_config):
    # Stub: Create a new performance alert
    return {"status": "success", "alert": alert_config}

def toggle_alert_status(user_id, alert_id):
    # Stub: Toggle alert status (activate/deactivate)
    return {"status": "success", "alert_id": alert_id, "new_status": "toggled"}

def get_notification_preferences(user_id):
    # Stub: Return notification preferences for the user
    return {
        "email_notifications": True,
        "push_notifications": False,
        "sms_notifications": False
    }

def update_user_notification_preferences(user_id, new_prefs):
    # Stub: Update notification preferences for the user
    return {"status": "success", "updated_preferences": new_prefs}

def analyse_thumbnail_effectiveness(video_id):
    # Stub: Return dummy thumbnail analysis
    return {
        "score": 78,
        "faces_detected": 1,
        "text_coverage": "low",
        "contrast": "high",
        "suggestions": ["Add more vibrant colors", "Increase text size"]
    }

def get_user_ab_tests(user_id):
    # Stub: Return a list of A/B tests for the user
    return [
        {"id": 1, "name": "Thumbnail Test", "status": "running"},
        {"id": 2, "name": "Title Test", "status": "completed"}
    ]

def create_new_ab_test(user_id, test_details):
    # Stub: Create a new A/B test
    return {"status": "success", "test": test_details}

def get_tracked_keywords(user_id):
    # Stub: Return a list of tracked keywords for the user
    return ["python tutorial", "flask web app", "seo tips"]

def start_keyword_tracking(user_id, keyword):
    # Stub: Start tracking a new keyword for the user
    return {"status": "success", "keyword": keyword}

def get_user_goals(user_id):
    # Stub: Return a list of user goals
    return [
        {"id": 1, "description": "Reach 10,000 subscribers", "progress": 70},
        {"id": 2, "description": "Publish 50 videos", "progress": 40}
    ]

def create_user_goal(user_id, goal_details):
    # Stub: Create a new user goal
    return {"status": "success", "goal": goal_details}

def calculate_goal_progress(user_id, goal_id):
    # Stub: Calculate progress for a specific goal
    return {"goal_id": goal_id, "progress": 78}

def get_user_milestones(user_id):
    # Stub: Return a list of milestones achieved by the user
    return [
        {"id": 1, "description": "First 1,000 views", "date": "2024-01-15"},
        {"id": 2, "description": "First 100 subscribers", "date": "2024-03-10"}
    ]

def get_user_reports(user_id):
    # Stub: Return a list of analytics reports for the user
    return [
        {"id": 1, "name": "Monthly Report", "created_at": "2025-05-01"},
        {"id": 2, "name": "Q1 Performance", "created_at": "2025-04-01"}
    ]

def generate_analytics_report(user_id, report_type):
    # Stub: Generate a new analytics report
    return {"status": "success", "report_type": report_type, "report_url": f"/reports/{user_id}/{report_type}"}

def export_analytics_data(user_id, format="csv"):
    # Stub: Export analytics data in the requested format
    return {"status": "success", "download_url": f"/exports/{user_id}/analytics.{format}"}


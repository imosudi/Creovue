# Standard library imports
import os
import time
from datetime import datetime, timedelta, date

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
    print("default_region: ", default_region); #time.sleep(300)
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
    print("ctr_metrics: ", ctr_metrics)
    return render_template('analytics.html',
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
            'https://www.googleapis.com/auth/yt-analytics.readonly'
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






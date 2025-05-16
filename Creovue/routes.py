
import datetime
import os
import time
from flask import Flask, redirect, render_template, request, jsonify, session, url_for
import requests
from flask_security import Security, SQLAlchemyUserDatastore, login_required, roles_required
from flask_security.utils import login_user

from .models.analytics import get_channel_stats, process_channel_analytics, fetch_youtube_analytics, generate_plot
from .logic import extract_keywords
from .models import db, User, Role
from .models.seo import get_seo_recommendations
#from .app_secets import creo_channel_id, creo_api_key, creo_mock_view_history
from . import app, google, oauth


from datetime import datetime, timedelta, date

from Creovue.models.trends  import (
    clear_trend_cache,
    fetch_top_channels,
    fetch_trending_keywords,
    get_all_regions,
    get_available_categories,
    get_category_age_distribution,
    get_category_distribution,
    get_default_region,
    get_related_keywords,
    get_top_channels,
    get_trend_chart_data,
    get_trending_keywords,
    get_trending_regions,
    visualise_category_age_distribution_base64
    )

from .config            import (
     creo_oauth_client_id, creo_oauth_client_secret,creo_google_redirect_uri, creo_google_auth_scope,
     creo_google_auth_uri, creo_google_token_uri,
     creo_channel_id, creo_api_key, creo_mock_view_history
)
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # For localhost testing

# Setup Flask-Security
## Set up user datastore
user_datastore = SQLAlchemyUserDatastore(db, User, Role)

## Attach Security
security = Security(app, user_datastore)

# Register the blueprint in main route
#from .route_trends import trends_bp
#app.register_blueprint(trends_bp)

@app.route("/admin")
@roles_required("Admin")
def admin_panel():
    return render_template("admin.html")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
@login_required
def dashboard():
    # Use fetch_youtube_analytics to get real stats with simulated daily views
    analytics = process_channel_analytics(creo_channel_id)
    return render_template("dashboard.html", stats=analytics)


@app.route('/seo', methods=['GET', 'POST'])
def seo():
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
    return render_template('seo.html', recommendations=recommendations, error=error)


"""@app.route('/trends')
def trends():
    trending_keywords = fetch_trending_keywords()
    top_channels = fetch_top_channels()
    trend_data = get_trend_chart_data()
    return render_template('trends.html', trending_keywords=trending_keywords, top_channels=top_channels, trend_data=trend_data)"""

@app.route("/trends")
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
def trend_data():
    client_ip = None
    try:
        client_ip = request.remote_addr
    except :
        pass
    default_region = get_default_region(client_ip)
    region = request.args.get("region", default_region)
    category = request.args.get("category", None)

    
    categories = get_available_categories(creo_api_key, default_region)

    #trending_keywords, keyword_age = get_trending_keywords(region, category)
    #category_distribution, category_age = get_category_distribution(region)
    #top_channels, channel_age = get_top_channels(region)

    trending_keywords, keyword_age = get_trending_keywords(region, categories); 
    trending_keywords = fetch_trending_keywords(region)
    category_distribution = get_category_distribution(region)
    category_age_distribution = get_category_age_distribution(region)
    top_channels, channel_data_age = get_top_channels(region)
    
    return jsonify({
        "trending_keywords": trending_keywords,
        "keyword_age": keyword_age,
        "category_distribution": category_distribution,
        "category_age": category_age_distribution,
        "top_channels": top_channels,
        #"channel_age": channel_age
    })

@app.route("/category/age-visual")
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
def analytics():
    analytics_data = fetch_youtube_analytics(creo_channel_id)

    def generate_plot(x, y):
        return {
            "labels": x,
            "values": y
        }

    x_labels = [(datetime.today() - timedelta(days=i)).strftime('%a') for i in reversed(range(7))]
    y_values = analytics_data["daily_views"]

    chart_data = generate_plot(x_labels, y_values)

    return render_template('analytics.html',
                           analytics=analytics_data,
                           chart_data=chart_data)



#@app.route("/analytics/overview")
#def video_analytics():
    #data = fetch_youtube_analytics(creo_channel_id)
    #chart = generate_plot(data)
    #return jsonify({"metrics": data, "chart_url": chart})


@app.route("/seo/keywords", methods=["POST"])
def keyword_research():
    content = request.json['text']
    keywords = extract_keywords([content])
    return jsonify({"keywords": keywords})



@app.route('/google-login')
def google_login():
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
        scopes=creo_google_auth_scope,
    )
    flow.redirect_uri = creo_google_redirect_uri

    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    session['oauth_state'] = state
    return redirect(auth_url)


@app.route('/oauth2callback')
def oauth2callback():
    state = session['oauth_state']
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
        scopes=creo_google_auth_scope,
        state=state
    )
    flow.redirect_uri = creo_google_redirect_uri

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    session['youtube_token'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    return redirect(url_for('youtube_dashboard'))



@app.route('/youtube-dashboard')
def youtube_dashboard():
    if 'youtube_token' not in session:
        return redirect(url_for('google_login'))

    creds = Credentials(**session['youtube_token'])

    # --- 1. Fetch channel metadata ---
    channel_resp = requests.get(
        'https://www.googleapis.com/youtube/v3/channels',
        headers={'Authorization': f'Bearer {creds.token}'},
        params={'part': 'snippet,statistics', 'mine': 'true'}
    )
    channel_data = channel_resp.json()

    # --- 2. Fetch top videos (last 10 uploads) ---
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

    # --- 3. Fetch view stats for those videos ---
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

    # --- 4. Simulate 7-day subscriber growth trend ---
    base_subs = int(channel_data['items'][0]['statistics'].get('subscriberCount', 1000))
    sub_growth = [base_subs - i * 20 for i in reversed(range(7))]  # mock growth

    return render_template('youtube_dashboard.html', 
        data=channel_data,
        top_videos=stats_data,
        subscriber_trend=sub_growth,
        subscriber_labels=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    )



"""
@app.route("/login/google")
def google_user_login():
    redirect_uri = url_for("google_authorise", _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route("/login_oauth2callback")
def google_authorise():
    token = google.authorize_access_token()
    resp = google.get("userinfo")
    user_info = resp.json()
    
    email = user_info["email"]
    user = User.query.filter_by(email=email).first()

    # First-time user: register
    if not user:
        user = User(
            email=email,
            username=email.split("@")[0],
            active=True,
            fs_uniquifier=os.urandom(16).hex()
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect(url_for("dashboard"))"""
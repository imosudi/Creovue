
import datetime
import time
from .logic import extract_keywords

from flask import Flask, render_template, request, jsonify
from .models.analytics import get_channel_stats, process_channel_analytics, fetch_youtube_analytics, generate_plot

from Creovue.models.trends import fetch_trending_keywords, fetch_top_channels, get_all_regions, get_available_categories, get_category_age_distribution, get_default_region, get_top_channels, get_trend_chart_data, get_trending_keywords, visualise_category_age_distribution_base64
from .models.seo import get_seo_recommendations

from .app_secets import creo_channel_id, creo_api_key, creo_mock_view_history

from . import app
from Creovue.models.trends  import (
    fetch_trending_keywords, 
    fetch_top_channels,
    get_trend_chart_data,
    get_category_distribution,
    get_related_keywords,
    get_trending_regions,
    clear_trend_cache,
    get_trending_keywords,
    get_category_distribution,
    get_top_channels,
    get_default_region
)



# Register the blueprint in main route
#from .route_trends import trends_bp
#app.register_blueprint(trends_bp)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
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
    regions = get_all_regions()
    default_region = get_default_region()
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
def trend_data():
    region = request.args.get("region", get_default_region())
    category = request.args.get("category", None)

    default_region = get_default_region()
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
    regions = get_all_regions()
    default_region = get_default_region()
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

    x_labels = [(datetime.date.today() - datetime.timedelta(days=i)).strftime('%a') for i in reversed(range(7))]
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
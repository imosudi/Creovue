
import datetime
from .logic import extract_keywords

from flask import Flask, render_template, request, jsonify
from .models.analytics import get_channel_stats, process_channel_analytics, fetch_youtube_analytics, generate_plot

from Creovue.models.trends import fetch_trending_keywords, fetch_top_channels, get_trend_chart_data
from .models.seo import get_seo_recommendations

from .app_secets import creo_channel_id, creo_mock_view_history

from . import app

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


@app.route('/trends')
def trends():
    return render_template('trends.html')

@app.route('/api/trend_data')
def trend_data():
    trending_keywords = fetch_trending_keywords()
    top_channels = fetch_top_channels()
    trend_data = get_trend_chart_data()
    return jsonify({
        "trending_keywords": trending_keywords,
        "top_channels": top_channels,
        "chart_data": trend_data
    })


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
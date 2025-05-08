#!/usr/bin/env python3

import time
from flask import Flask, jsonify, render_template, request

from .logic import extract_keywords

from flask import Flask, render_template
from .models.analytics import get_channel_stats, process_channel_analytics, fetch_youtube_analytics, generate_plot

from Creovue.utils.yt_api import fetch_trending_keywords, fetch_top_channels
from .models.seo import get_seo_recommendations
from .models.trends import get_trend_chart_data


#API_KEY = 'AIzaSyD2CDKx69jQkQ_ZdpV47zpATny7s9lb33M'  # Note: This appears to be truncated
#BASE_URL = 'https://www.googleapis.com/youtube/v3'

# Example: Hardcoded YouTube channel ID and mock data for now
#channel_id ='UCGuicwccZSZE0Jcyuy074zw'
#mock_view_history = [120, 150, 130, 170, 400, 180, 190]
from .app_secets import creo_channel_id, creo_mock_view_history

app = Flask(__name__)

@app.route("/")
def dashboard():
    
    #channel_id = 'UCGuicwccZSZE0Jcyuy074zw'  # Google Developers
    #mock_view_history = [120, 150, 130, 170, 400, 180, 190]  # Replace with real API values
    #print(creo_channel_id, creo_mock_view_history); #time.sleep(300)
    analytics = process_channel_analytics(creo_channel_id, creo_mock_view_history)

    return render_template("dashboard.html", stats=analytics)

@app.route('/seo', methods=['GET', 'POST'])
def seo():
    recommendations = None
    if request.method == 'POST':
        keyword = request.form['keyword']
        recommendations = get_seo_recommendations(keyword)
    return render_template('seo.html', recommendations=recommendations)

@app.route('/trends')
def trends():
    trending_keywords = fetch_trending_keywords()
    top_channels = fetch_top_channels()
    trend_data = get_trend_chart_data()
    return render_template('trends.html', trending_keywords=trending_keywords, top_channels=top_channels, trend_data=trend_data)


@app.route('/analytics')
def analytics():
    analytics_data = fetch_youtube_analytics(creo_channel_id)
    #chart_data = generate_plot(list(range(len(mock_view_history))), channel_id)
    mock_view_history = [18000, 22000, 24000, 20000, 26000, 23000, 21000]
    def generate_plot(x, y):
        return {
        "labels": x,
        "values": y
    }

    analytics_data = fetch_youtube_analytics(creo_channel_id)
    chart_data = generate_plot(list(range(len(mock_view_history))), mock_view_history)

    return render_template('analytics.html',
                           analytics=analytics_data,
                           chart_data={
                               "labels": list(range(len(mock_view_history))),
                               "values": mock_view_history
                           })


@app.route("/seo/keywords", methods=["POST"])
def keyword_research():
    content = request.json['text']
    keywords = extract_keywords([content])
    return jsonify({"keywords": keywords})

#@app.route("/analytics/overview")
#def video_analytics():
    #data = fetch_youtube_analytics(creo_channel_id)
    #chart = generate_plot(data)
    #return jsonify({"metrics": data, "chart_url": chart})



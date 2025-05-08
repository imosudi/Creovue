#!/usr/bin/env python3

import time
from flask import Flask, jsonify, render_template, request


app = Flask(__name__)


#@app.route("/analytics/overview")
#def video_analytics():
    #data = fetch_youtube_analytics(creo_channel_id)
    #chart = generate_plot(data)
    #return jsonify({"metrics": data, "chart_url": chart})


import Creovue.routes
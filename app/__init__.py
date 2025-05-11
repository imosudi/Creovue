from flask import Flask,redirect,url_for,render_template,request

app=Flask(__name__)
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
#@login_required
def dashboard():
    # Use fetch_youtube_analytics to get real stats with simulated daily views
    #analytics = process_channel_analytics(creo_channel_id)
    return render_template("dashboard.html")#, stats=analytics)

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

@app.route("/trends")
def trends():
    return render_template()


@app.route("/analytics")
def analytics():
    return render_template()

if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run(port=5000,debug=True)
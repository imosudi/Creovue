# =============================================================================
# AUDIENCE INSIGHTS
# =============================================================================
from flask import render_template, request, jsonify
from flask_security import login_required, current_user
from . import app
from .helper_funcrions import ensure_channel_id, get_audience_demographics, get_comprehensive_audience_insights, analyse_engagement_patterns, analyse_audience_retention


@app.route('/audience/insights')
@login_required
def audience_insights():
    """Comprehensive audience analysis"""
    ensure_channel_id()
    
    if not current_user.channel_id:
        return render_template('audience_insights.html', error="No channel connected")
    channel_id = current_user.channel_id
    days = 100
    #print("channel_id: ", channel_id); time.sleep(30)
    insights = get_comprehensive_audience_insights(channel_id, days)
    return render_template('insights.html', insights=insights)
    try:
        #insights = get_comprehensive_audience_insights(channel_id, days)
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


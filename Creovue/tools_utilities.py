

# =============================================================================
# TOOLS & UTILITIES
# =============================================================================
#from .competitors_analytics import analyse_thumbnail_effectiveness, calculate_goal_progress, create_new_ab_test, create_performance_alert, create_user_goal, export_analytics_data, generate_analytics_report, get_notification_preferences, get_tracked_keywords, get_user_ab_tests, get_user_alerts, get_user_goals, get_user_milestones, get_user_reports, start_keyword_tracking, toggle_alert_status, update_user_notification_preferences
from flask_security import (login_required, current_user)
from flask import  request, jsonify, render_template

from Creovue.helper_funcrions import analyse_thumbnail_effectiveness, create_new_ab_test, get_tracked_keywords, get_user_ab_tests, start_keyword_tracking
from . import app

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






# =============================================================================
# CONTENT PLANNING & OPTIMISATION
# =============================================================================
from flask import render_template, request, jsonify
from flask_security import login_required, current_user

from Creovue.helper_funcrions import analyse_optimal_posting_times, create_content_schedule, generate_content_suggestions, get_user_content_plans         
from . import app
#from .competitors_analytics import analyse_optimal_posting_times, analyse_thumbnail_effectiveness, calculate_goal_progress, create_content_schedule, create_new_ab_test, create_performance_alert, create_user_goal, export_analytics_data, generate_analytics_report, generate_content_suggestions, get_notification_preferences, get_tracked_keywords, get_user_ab_tests, get_user_alerts, get_user_content_plans, get_user_goals, get_user_milestones, get_user_reports, start_keyword_tracking, toggle_alert_status, update_user_notification_preferences
from Creovue.utils.youtube_client import ensure_channel_id



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



# Additional helper functions would continue here...
# Each function would contain the specific logic for that feature


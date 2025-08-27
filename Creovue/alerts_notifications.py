# =============================================================================
# ALERTS & NOTIFICATIONS
# =============================================================================
from flask_security import (login_required, current_user)
from flask import  request, jsonify, render_template

from Creovue.helper_funcrions import get_user_alerts, toggle_alert_status, create_performance_alert, get_notification_preferences, update_user_notification_preferences
from . import app
#from .competitors_analytics import analyse_thumbnail_effectiveness, calculate_goal_progress, create_new_ab_test, create_performance_alert, create_user_goal, export_analytics_data, generate_analytics_report, get_notification_preferences, get_tracked_keywords, get_user_ab_tests, get_user_alerts, get_user_goals, get_user_milestones, get_user_reports, start_keyword_tracking, toggle_alert_status, update_user_notification_preferences

@app.route('/alerts')
@login_required
def alerts_dashboard():
    """Alerts and notifications dashboard"""
    alerts = get_user_alerts(current_user.id)
    return render_template('alerts_dashboard.html', alerts=alerts)

@app.route('/api/alerts/create', methods=['POST'])
@login_required
def create_alert():
    """Create a new alert"""
    data = request.json
    
    try:
        alert = create_performance_alert(current_user.id, data)
        return jsonify({"success": True, "alert": alert})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/alerts/<alert_id>/toggle', methods=['PUT'])
@login_required
def toggle_alert(alert_id):
    """Toggle alert on/off"""
    try:
        alert = toggle_alert_status(alert_id, current_user.id)
        return jsonify({"success": True, "alert": alert})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/notifications/preferences')
@login_required
def notification_preferences():
    """Notification preferences page"""
    preferences = get_notification_preferences(current_user.id)
    return render_template('notification_preferences.html', preferences=preferences)

@app.route('/api/notifications/preferences', methods=['PUT'])
@login_required
def update_notification_preferences():
    """Update notification preferences"""
    data = request.json
    
    try:
        preferences = update_user_notification_preferences(current_user.id, data)
        return jsonify({"success": True, "preferences": preferences})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


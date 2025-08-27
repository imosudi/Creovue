# =============================================================================
# REPORTING & EXPORTS
# =============================================================================
from .competitors_analytics import analyse_thumbnail_effectiveness, calculate_goal_progress, create_new_ab_test, create_performance_alert, create_user_goal, export_analytics_data, generate_analytics_report, get_notification_preferences, get_tracked_keywords, get_user_ab_tests, get_user_alerts, get_user_goals, get_user_milestones, get_user_reports, start_keyword_tracking, toggle_alert_status, update_user_notification_preferences
from flask_security import (login_required, current_user)
from flask import  request, jsonify, render_template
from . import app

@app.route('/reports')
@login_required
def reports_dashboard():
    """Reports dashboard"""
    reports = get_user_reports(current_user.id)
    return render_template('reports_dashboard.html', reports=reports)

@app.route('/api/reports/generate', methods=['POST'])
@login_required
def generate_report():
    """Generate a custom report"""
    data = request.json
    
    try:
        report = generate_analytics_report(current_user.id, data)
        return jsonify({"success": True, "report": report})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/export/<export_type>')
@login_required
def export_data(export_type):
    """Export data in various formats"""
    format_type = request.args.get('format', 'csv')
    
    try:
        export_data = export_analytics_data(
            current_user.id, 
            export_type, 
            format_type
        )
        return jsonify(export_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


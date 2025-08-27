
# =============================================================================
# GOALS & PROGRESS TRACKING
# =============================================================================
from flask import render_template, request, jsonify
from flask_security import login_required, current_user

from Creovue.helper_funcrions import calculate_goal_progress, create_user_goal, get_user_goals, get_user_milestones

#from Creovue.competitors_analytics import calculate_goal_progress, create_user_goal, get_user_goals, get_user_milestones
from . import app


@app.route('/goals')
@login_required
def goals_dashboard():
    """Goals and progress tracking dashboard"""
    goals = get_user_goals(current_user.id)
    return render_template('goals_dashboard.html', goals=goals)

@app.route('/api/goals/create', methods=['POST'])
@login_required
def create_goal():
    """Create a new goal"""
    data = request.json
    
    try:
        goal = create_user_goal(current_user.id, data)
        return jsonify({"success": True, "goal": goal})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/goals/<goal_id>/progress')
@login_required
def goal_progress(goal_id):
    """Get goal progress"""
    try:
        progress = calculate_goal_progress(goal_id, current_user.id)
        return jsonify(progress)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/goals/milestones')
@login_required
def milestones():
    """View achieved milestones"""
    milestones = get_user_milestones(current_user.id)
    return render_template('milestones.html', milestones=milestones)



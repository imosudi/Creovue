
# =============================================================================
# CHANNEL OVERVIEW & HEALTH
# =============================================================================
from flask import render_template, request, jsonify
from flask_security import login_required, current_user
from datetime import datetime
from . import app
from .helper_funcrions import ensure_channel_id, get_channel_health_overview, calculate_channel_health_score, get_health_recommendations, analyse_channel_growth, predict_channel_growth

@app.route('/channel/overview')
@login_required
def channel_overview():
    """Comprehensive channel health overview"""
    ensure_channel_id()
    
    if not current_user.channel_id:
        return render_template('channel_overview.html', error="No channel connected")
    
    try:
        # Get comprehensive channel health data
        health_data = get_channel_health_overview(current_user.channel_id)
        return render_template('channel_overview.html', health=health_data)
    except Exception as e:
        print(f"[Channel Overview Error] {e}")
        return render_template('channel_overview.html', error=str(e))

@app.route('/api/channel/health')
@login_required
def api_channel_health():
    """API endpoint for channel health metrics"""
    ensure_channel_id()
    
    if not current_user.channel_id:
        return jsonify({"error": "No channel connected"}), 400
    
    try:
        health_score = calculate_channel_health_score(current_user.channel_id)
        recommendations = get_health_recommendations(current_user.channel_id)
        
        return jsonify({
            "health_score": health_score,
            "recommendations": recommendations,
            "last_updated": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/channel/growth-analysis')
@login_required
def channel_growth_analysis():
    """Detailed growth analysis with predictions"""
    ensure_channel_id()
    
    if not current_user.channel_id:
        return render_template('growth_analysis.html', error="No channel connected")
    
    try:
        growth_data = analyse_channel_growth(current_user.channel_id)
        predictions = predict_channel_growth(current_user.channel_id)
        
        return render_template('growth_analysis.html', 
                             growth=growth_data, 
                             predictions=predictions)
    except Exception as e:
        return render_template('growth_analysis.html', error=str(e))


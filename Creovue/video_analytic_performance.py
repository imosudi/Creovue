# =============================================================================
# VIDEO ANALYTICS & PERFORMANCE
# =============================================================================
from flask import render_template, request, jsonify
from flask_security import login_required, current_user
from . import app               
from .helper_funcrions import ensure_channel_id, get_video_performance_data, get_detailed_video_analytics, analyse_videos_batch, get_video_performance_trends
 
@app.route('/videos/performance')
@login_required
def video_performance():
    """Individual video performance analysis"""
    ensure_channel_id()
    
    if not current_user.channel_id:
        return render_template('video_performance.html', error="No channel connected")
    
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'upload_date')
    
    try:
        videos = get_video_performance_data(current_user.channel_id, page, sort_by)
        return render_template('video_performance.html', videos=videos)
    except Exception as e:
        return render_template('video_performance.html', error=str(e))

@app.route('/api/video/<video_id>/analytics')
@login_required
def api_video_analytics(video_id):
    """Detailed analytics for a specific video"""
    try:
        analytics = get_detailed_video_analytics(video_id, current_user.channel_id)
        return jsonify(analytics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/videos/batch-analysis', methods=['POST'])
@login_required
def batch_video_analysis():
    """Analyse multiple videos at once"""
    video_ids = request.json.get('video_ids', [])
    
    if not video_ids:
        return jsonify({"error": "No video IDs provided"}), 400
    
    try:
        analysis = analyse_videos_batch(video_ids, current_user.channel_id)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/videos/performance-trends')
@login_required
def video_performance_trends():
    """Video performance trends over time"""
    ensure_channel_id()
    
    timeframe = request.args.get('timeframe', '30d')
    metric = request.args.get('metric', 'views')
    
    try:
        trends = get_video_performance_trends(current_user.channel_id, timeframe, metric)
        return render_template('performance_trends.html', trends=trends)
    except Exception as e:
        return render_template('performance_trends.html', error=str(e))

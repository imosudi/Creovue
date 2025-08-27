# =============================================================================
# SEO & DISCOVERY TOOLS (Enhanced)
# =============================================================================
from flask import render_template, request, jsonify
from flask_security import login_required, current_user
from . import app
from .helper_funcrions import optimise_video_seo, generate_optimised_tags, optimise_video_title

@app.route('/seo/optimisation')
@login_required
def seo_optimisation():
    """SEO optimisation dashboard"""
    return render_template('seo_optimisation.html')

@app.route('/api/seo/video-optimisation', methods=['POST'])
@login_required
def api_video_seo_optimisation():
    """Optimise SEO for a specific video"""
    data = request.json
    video_id = data.get('video_id')
    target_keywords = data.get('keywords', [])
    
    try:
        optimisation = optimise_video_seo(video_id, target_keywords, current_user.channel_id)
        return jsonify(optimisation)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/seo/tag-generator', methods=['POST'])
@login_required
def tag_generator():
    """Generate optimised tags for video content"""
    data = request.json
    title = data.get('title', '')
    description = data.get('description', '')
    category = data.get('category', '')
    
    try:
        tags = generate_optimised_tags(title, description, category)
        return jsonify({"tags": tags})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/seo/title-optimiser', methods=['POST'])
@login_required
def title_optimiser():
    """Optimise video titles for better discovery"""
    data = request.json
    original_title = data.get('title', '')
    target_audience = data.get('audience', 'general')
    
    try:
        optimised_titles = optimise_video_title(original_title, target_audience)
        return jsonify({"optimised_titles": optimised_titles})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
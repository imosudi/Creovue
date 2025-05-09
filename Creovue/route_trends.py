# routes/trends.py - Enhanced API routes for trend functionality

from flask import Blueprint, render_template, jsonify, request, current_app
from datetime import datetime
import logging

from Creovue.models.trends  import (
    fetch_trending_keywords, 
    fetch_top_channels,
    get_trend_chart_data,
    get_category_distribution,
    get_related_keywords,
    get_trending_regions,
    clear_trend_cache
)

# Create Blueprint
trends_bp = Blueprint('trends', __name__)
logger = logging.getLogger('trends.routes')

@trends_bp.route('/trends')
def trends_page():
    """Render the main trends dashboard page"""
    regions = get_trending_regions()
    return render_template(
        'trends.html', 
        regions=regions, 
        default_region="GB",
        page_title="Content Trends Dashboard"
    )

@trends_bp.route('/trends/<keyword>')
def keyword_trends(keyword):
    """Render the specific keyword trends page"""
    regions = get_trending_regions()
    return render_template(
        'keyword_trends.html',
        keyword=keyword,
        regions=regions,
        default_region="GB",
        page_title=f"Trend Analysis: {keyword}"
    )

@trends_bp.route('/api/trend_data')
def trend_data():
    """
    Main API endpoint for fetching trend data
    
    Query parameters:
    - region: Country code (default: GB)
    - category: Category ID to filter by (optional)
    - keyword: Specific keyword to analyze (optional)
    """
    try:
        # Extract request parameters
        region = request.args.get('region', 'GB')
        category = request.args.get('category')
        keyword = request.args.get('keyword')
        
        # Get trend data
        trending_keywords = fetch_trending_keywords(region=region, category_id=category)
        top_channels = fetch_top_channels(region=region, category_id=category)
        chart_data = get_trend_chart_data(region=region, keyword=keyword)
        categories = get_category_distribution(region=region)
        
        # Include related keywords if a specific keyword was requested
        related_keywords = []
        if keyword:
            related_keywords = get_related_keywords(keyword)
        
        # Return comprehensive trend data
        return jsonify({
            "trending_keywords": trending_keywords,
            "top_channels": top_channels,
            "chart_data": chart_data,
            "category_distribution": categories,
            "related_keywords": related_keywords,
            "metadata": {
                "region": region,
                "timestamp": datetime.now().isoformat(),
                "category_filter": category
            }
        })
    except Exception as e:
        logger.error(f"Error in trend_data endpoint: {e}")
        return jsonify({
            "error": "Failed to fetch trend data",
            "message": str(e)
        }), 500

@trends_bp.route('/api/related_keywords')
def related_keywords_api():
    """
    Get related keywords for a given seed keyword
    
    Query parameters:
    - keyword: The seed keyword to find related terms for
    - limit: Maximum number of results to return (default: 10)
    """
    keyword = request.args.get('keyword')
    limit = int(request.args.get('limit', 10))
    
    if not keyword:
        return jsonify({"error": "Keyword parameter is required"}), 400
    
    related = get_related_keywords(keyword, max_results=limit)
    
    return jsonify({
        "keyword": keyword,
        "related_keywords": related
    })

@trends_bp.route('/api/channels')
def channels_api():
    """
    Get detailed channel data
    
    Query parameters:
    - region: Country code (default: GB)
    - category: Category ID to filter by (optional)
    - limit: Maximum results to return (default: 10)
    """
    region = request.args.get('region', 'GB')
    category = request.args.get('category')
    limit = int(request.args.get('limit', 10))
    
    channels = fetch_top_channels(
        region=region, 
        category_id=category,
        max_results=limit
    )
    
    return jsonify({
        "channels": channels,
        "metadata": {
            "region": region,
            "category": category,
            "timestamp": datetime.now().isoformat()
        }
    })

@trends_bp.route('/api/categories')
def categories_api():
    """Get category distribution data"""
    region = request.args.get('region', 'GB')
    categories = get_category_distribution(region=region)
    
    return jsonify({
        "categories": categories,
        "region": region
    })

@trends_bp.route('/api/regions')
def regions_api():
    """Get available regions for trend analysis"""
    return jsonify({
        "regions": get_trending_regions()
    })

@trends_bp.route('/api/clear_cache', methods=['POST'])
def clear_cache_api():
    """Admin endpoint to clear trend data cache"""
    # In production, add authentication here
    if clear_trend_cache():
        return jsonify({"status": "success", "message": "Cache cleared successfully"})
    else:
        return jsonify({"status": "error", "message": "Failed to clear cache"}), 500

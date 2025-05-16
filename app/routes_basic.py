import datetime
from flask_security import  login_required, roles_required
from . import app

from app.models.analytics import process_channel_analytics
from app.models.seo import get_seo_recommendations
from app.models.trends import fetch_trending_keywords, get_all_regions, get_available_categories, get_category_age_distribution, get_category_distribution, get_default_region, get_top_channels, get_trending_keywords, visualise_category_age_distribution_base64
from app.utils.yt_api import fetch_youtube_analytics
from flask import  jsonify, render_template, request

from .config import(
    creo_channel_id,
    creo_api_key
)


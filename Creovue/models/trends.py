# trends.py (Production-ready)
import requests
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import random
import re
import logging
import functools
from threading import Timer
from time import time
import os
import io
import base64

from collections import defaultdict
import random
from Creovue.utils.youtube_client import get_youtube_client
from Creovue.utils.decorators import cached, handle_api_error

from youtubesearchpython import Suggestions

import pycountry, geocoder
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend
import matplotlib.pyplot as plt
import numpy as np

from collections import Counter, defaultdict
from Creovue.app_secrets import creo_api_key, creo_base_url
# models/trends.py

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('trends')


# YouTube API configuration
#API_KEY = "YOUR_YOUTUBE_API_KEY"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
CACHE_DURATION = 3600  # Cache for 1 hour


# trends.py (Enhanced Production-ready)
# Cache storage
_trend_cache = {}
_cache_timestamps = {}


def get_youtube_client():
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=creo_api_key)

def sanitize_text(text):
    """Remove special characters and common stop words"""
    # Basic stopwords list
    stopwords = {'a', 'an', 'the', 'and', 'or', 'but', 'is', 'are', 'in', 'to', 'of', 'for', 'with'}
    # Remove non-alphanumeric characters and convert to lowercase
    text = re.sub(r'[^\w\s]', '', text.lower())
    # Split into words and filter out stopwords and short words
    words = [word for word in text.split() if word not in stopwords and len(word) > 2]
    return words

def fetch_trending_keywords(region="US"):
    youtube = get_youtube_client()
    try:
        response = youtube.videos().list(
            part="snippet",
            chart="mostPopular",
            regionCode=region,
            maxResults=50  # Increased to get better keyword data
        ).execute()

        keywords = []
        for item in response['items']:
            title = item['snippet']['title']
            description = item['snippet'].get('description', '')
            
            # Extract keywords from title and description
            keywords.extend(sanitize_text(title))
            keywords.extend(sanitize_text(description))

        # Count and return top 10 keywords
        counter = Counter(keywords)
        common = counter.most_common(10)
        return [{"name": word, "volume": count * 10} for word, count in common]
    except Exception as e:
        print(f"Error fetching trending keywords: {e}")
        return [{"name": f"Sample {i}", "volume": random.randint(50, 500)} for i in range(1, 11)]

def fetch_top_channels(region="US"):
    youtube = get_youtube_client()
    try:
        response = youtube.videos().list(
            part="snippet",
            chart="mostPopular",
            regionCode=region,
            maxResults=20  # Increased to get more diverse channels
        ).execute()

        channel_ids = list(set(item['snippet']['channelId'] for item in response['items']))
        channels_data = []

        for cid in channel_ids[:5]:
            channel = youtube.channels().list(part="snippet,statistics", id=cid).execute()
            if channel['items']:
                info = channel['items'][0]
                subscriber_count = int(info['statistics'].get('subscriberCount', 0))
                # Format subscriber count nicely
                if subscriber_count >= 1000000:
                    subscribers = f"{subscriber_count / 1000000:.1f}M"
                else:
                    subscribers = f"{subscriber_count // 1000}K"
                    
                channels_data.append({
                    "name": info['snippet']['title'],
                    "subscribers": subscribers,
                    "thumbnail": info['snippet'].get('thumbnails', {}).get('default', {}).get('url', '')
                })
        return channels_data
    except Exception as e:
        print(f"Error fetching top channels: {e}")
        return [{"name": f"Channel {i}", "subscribers": f"{random.randint(100, 999)}K", 
                "thumbnail": ""} for i in range(1, 6)]

def get_trend_chart_data():
    # Simulate a trend chart over 7 days using top keyword frequency
    labels = [(datetime.now() - timedelta(days=i)).strftime("%a") for i in reversed(range(7))]
    values = [random.randint(10, 50) for i in range(7)]  # Fixed variable name error
    
    # Add a second dataset for comparison
    values2 = [random.randint(5, 45) for i in range(7)]
    
    return {
        "labels": labels, 
        "values": values,
        "values2": values2
    }

def cached(expiry_seconds=CACHE_DURATION):
    """Decorator for caching API results"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            current_time = time()
            
            # Return cached result if valid
            if cache_key in _trend_cache and current_time - _cache_timestamps.get(cache_key, 0) < expiry_seconds:
                logger.info(f"Using cached data for {func.__name__}")
                return _trend_cache[cache_key]
            
            # Get fresh data
            result = func(*args, **kwargs)
            _trend_cache[cache_key] = result
            _cache_timestamps[cache_key] = current_time
            return result
        return wrapper
    return decorator

def get_youtube_client():
    """Get authenticated YouTube API client"""
    try:
        return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=creo_api_key)
    except Exception as e:
        logger.error(f"Failed to create YouTube API client: {e}")
        raise

def handle_api_error(func):
    """Decorator to handle API errors gracefully"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"API error in {func.__name__}: {e}")
            # Return sensible defaults based on function
            if "keywords" in func.__name__:
                return []
            elif "channels" in func.__name__:
                return []
            elif "chart" in func.__name__:
                return {"labels": [], "values": []}
            else:
                return None
    return wrapper

def extract_keywords_from_title(title):
    """Extract meaningful keywords from title"""
    # Remove special characters and lowercase
    cleaned = re.sub(r'[^\w\s]', ' ', title.lower())
    
    # Filter out common words and short terms
    common_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
                   "with", "by", "of", "from", "as", "is", "are", "was", "were", "be", 
                   "this", "that", "it", "what", "when", "where", "how", "why", "who",
                   "video", "new", "top", "best", "vs", "you", "your", "i", "we", "they"}
    
    keywords = [word for word in cleaned.split() if word not in common_words and len(word) > 2]
    return keywords

@cached(expiry_seconds=3600)  # Cache for 1 hour
@handle_api_error
def fetch_top_channels(region="GB", category_id=None, max_results=10):
    """
    Fetch top channels with detailed metrics
    
    Args:
        region (str): Country code (default: GB for United Kingdom)
        category_id (str, optional): YouTube category ID to filter by
        max_results (int): Maximum number of channels to return
        
    Returns:
        list: Channel data with detailed metrics
    """
    youtube = get_youtube_client()
    
    # Get trending videos first
    params = {
        "part": "snippet",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": 50  # Get more videos to find unique channels
    }
    
    if category_id:
        params["videoCategoryId"] = category_id
        
    response = youtube.videos().list(**params).execute()
    
    # Count channel occurrences and collect unique IDs
    channel_counts = Counter()
    channel_ids = set()
    channel_videos = defaultdict(list)
    
    for item in response.get('items', []):
        channel_id = item['snippet']['channelId']
        channel_title = item['snippet']['channelTitle']
        video_id = item['id']
        
        channel_counts[channel_id] += 1
        channel_ids.add(channel_id)
        channel_videos[channel_id].append(video_id)
    
    # Get detailed channel information for top channels
    top_channel_ids = [cid for cid, _ in channel_counts.most_common(max_results)]
    channels_data = []
    
    # Batch request channel details
    if top_channel_ids:
        for i in range(0, len(top_channel_ids), 50):  # Process in batches of 50
            batch_ids = top_channel_ids[i:i+50]
            channels_response = youtube.channels().list(
                part="snippet,statistics,brandingSettings",
                id=",".join(batch_ids)
            ).execute()
            
            for info in channels_response.get('items', []):
                cid = info['id']
                stats = info.get('statistics', {})
                branding = info.get('brandingSettings', {}).get('channel', {})
                
                # Format large numbers with K/M/B suffix
                subs = int(stats.get('subscriberCount', 0))
                views = int(stats.get('viewCount', 0))
                
                channels_data.append({
                    "id": cid,
                    "name": info['snippet']['title'],
                    "description": branding.get('description', ''),
                    "thumbnail": info['snippet']['thumbnails'].get('default', {}).get('url', ''),
                    "subscribers": format_number(subs),
                    "subscribers_raw": subs,
                    "views": format_number(views),
                    "video_count": stats.get('videoCount', 0),
                    "country": info['snippet'].get('country', ''),
                    "trending_videos": len(channel_videos[cid]),
                    "category": get_channel_category(branding.get('keywords', ''))
                })
    
    # Sort by trending score and subscriber count
    channels_data.sort(key=lambda x: (x["trending_videos"], x["subscribers_raw"]), reverse=True)
    return channels_data[:max_results]

def format_number(num):
    """Format large numbers with K/M/B suffix"""
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return str(num)

def get_channel_category(keywords_str):
    """Determine channel category from keywords"""
    if not keywords_str:
        return "General"
        
    keywords = keywords_str.lower().split(',')
    
    # Define category keywords
    categories = {
        "Gaming": ["gaming", "games", "gamer", "gameplay", "playthrough", "minecraft", "fortnite"],
        "Technology": ["tech", "technology", "coding", "programming", "computers", "software", "hardware"],
        "Entertainment": ["vlog", "comedy", "funny", "entertainment", "reaction", "challenge"],
        "Music": ["music", "song", "singer", "band", "rap", "hip hop", "rock"],
        "Education": ["learn", "education", "tutorial", "how to", "course", "lesson"],
        "Lifestyle": ["lifestyle", "fashion", "beauty", "makeup", "fitness", "health"]
    }
    
    # Count category matches
    category_scores = Counter()
    for category, terms in categories.items():
        for term in terms:
            if any(term in kw for kw in keywords):
                category_scores[category] += 1
    
    # Return best match or default
    if category_scores:
        return category_scores.most_common(1)[0][0]
    return "General"

@cached(expiry_seconds=3600)  # Cache for 1 hour
@handle_api_error
def get_trend_chart_data(days=14, region="GB", keyword=None):
    """
    Get historical trend data for charting
    
    Args:
        days (int): Number of days to include
        region (str): Country code
        keyword (str, optional): Specific keyword to track
        
    Returns:
        dict: Chart data with labels and datasets
    """
    # In a production environment, you would pull this from a database
    # where you've been storing daily trend data
    # For now, we'll generate realistic simulated data
    
    labels = [(datetime.now() - timedelta(days=i)).strftime("%d %b") for i in reversed(range(days))]
    
    # Create multiple datasets for different metrics
    datasets = []
    
    # Keyword volume dataset - create realistic trend pattern
    base_value = random.randint(20, 40)
    values = []
    
    # Generate realistic trending pattern with some randomness but following a trend
    trend_direction = random.choice([1, -1])  # 1 = upward trend, -1 = downward trend
    
    for i in range(days):
        # Add day of week pattern (weekends higher than weekdays)
        day_of_week = (datetime.now() - timedelta(days=days-i-1)).weekday()
        weekend_boost = 10 if day_of_week >= 5 else 0
        
        # Add trend direction
        trend_factor = (i / days) * 15 * trend_direction
        
        # Add randomness
        noise = random.randint(-5, 5)
        
        value = max(5, int(base_value + weekend_boost + trend_factor + noise))
        values.append(value)
    
    datasets.append({
        "label": f"{'Keyword Volume' if not keyword else f'{keyword} Volume'}",
        "data": values,
        "backgroundColor": "rgba(54, 162, 235, 0.5)",
        "borderColor": "rgba(54, 162, 235, 1)",
        "borderWidth": 1,
        "tension": 0.4  # Smooth line
    })
    
    # Engagement dataset (different pattern)
    engagement_values = [int(v * random.uniform(0.8, 1.2)) for v in values]
    datasets.append({
        "label": "Viewer Engagement",
        "data": engagement_values,
        "backgroundColor": "rgba(255, 99, 132, 0.5)",
        "borderColor": "rgba(255, 99, 132, 1)",
        "borderWidth": 1,
        "tension": 0.4
    })
    
    return {
        "labels": labels,
        "datasets": datasets
    }

@cached(expiry_seconds=43200)  # Cache for 12 hours
@handle_api_error
def get_related_keywords(keyword, max_results=10):
    """Find related keywords for a given seed keyword"""
    try:
        # This would ideally use a proper API, but we'll simulate with a model
        related_terms = []
        
        # Map of some common related terms (in a real app, use a proper API or ML model)
        seed_mapping = {
            "python": ["programming", "coding", "development", "django", "flask", "data science"],
            "javascript": ["react", "node.js", "web development", "frontend", "vue", "angular"],
            "gaming": ["minecraft", "fortnite", "playstation", "xbox", "pc gaming", "streaming"],
            "cooking": ["recipes", "baking", "chef", "food", "kitchen", "meal prep"],
            "fitness": ["workout", "gym", "exercise", "health", "nutrition", "weight loss"]
        }
        
        # Find closest match in our mapping
        best_match = None
        highest_similarity = -1
        
        for seed in seed_mapping:
            if keyword.lower() in seed.lower() or seed.lower() in keyword.lower():
                similarity = len(set(keyword.lower()) & set(seed.lower())) / len(set(keyword.lower()) | set(seed.lower()))
                if similarity > highest_similarity:
                    highest_similarity = similarity
                    best_match = seed
        
        if best_match and highest_similarity > 0.3:
            related_terms = seed_mapping[best_match]
        else:
            # Fallback: generate some variations
            related_terms = [
                f"best {keyword}",
                f"{keyword} tutorial",
                f"{keyword} guide",
                f"how to {keyword}",
                f"{keyword} tips",
                f"{keyword} for beginners"
            ]
        
        # Return with randomized scores
        return [
            {"keyword": term, "score": random.randint(60, 95)} 
            for term in related_terms[:max_results]
        ]
    except Exception as e:
        logger.error(f"Error in get_related_keywords: {e}")
        return []


def get_trending_regions():
    """Get list of available regions with localised names"""
    # Custom name mappings to match original entries and common usage
    custom_names = {
        "GB": "United Kingdom",
        "US": "United States",
        "KR": "South Korea",
        "KP": "North Korea",
        "TW": "Taiwan",
        "MK": "North Macedonia",
        # Add other custom mappings here if needed
    }
    
    regions = []
    for country in pycountry.countries:
        code = country.alpha_2
        name = custom_names.get(code, country.name)
        regions.append({"code": code, "name": name})
    print(regions)
    return regions

def get_trending_regions():
    """Get list of available regions with localised names"""
    return [
        {"code": "GB", "name": "United Kingdom"},
        {"code": "US", "name": "United States"},
        {"code": "CA", "name": "Canada"},
        {"code": "AU", "name": "Australia"},
        {"code": "DE", "name": "Germany"},
        {"code": "FR", "name": "France"},
        {"code": "JP", "name": "Japan"},
        {"code": "IN", "name": "India"},
        {"code": "BR", "name": "Brazil"},
        {"code": "KR", "name": "South Korea"}
    ]


# URL and route utility functions
def generate_trend_api_url(base_url, region="GB", category=None, keyword=None):
    """Generate API URL with optional parameters"""
    url = f"{base_url}/api/trend_data?region={region}"
    if category:
        url += f"&category={category}"
    if keyword:
        url += f"&keyword={keyword}"
    return url

def clear_trend_cache():
    """Clear all cached trend data"""
    global _trend_cache, _cache_timestamps
    _trend_cache = {}
    _cache_timestamps = {}
    logger.info("Trend cache cleared")
    return True



"""# Simulated category distribution
def get_category_distribution_(region="US"):
    categories = get_available_categories()
    distribution = {cat: random.randint(5, 25) for cat in categories}
    timestamp = (datetime.now() - timedelta(minutes=random.randint(10, 40))).strftime("%Y-%m-%d %H:%M")
    return distribution, timestamp"""



def get_all_regions():
    """Get list of available regions with localised names"""
    # Custom name mappings to match original entries and common usage
    custom_names = {
        "GB": "United Kingdom",
        "US": "United States",
        "KR": "South Korea",
        "KP": "North Korea",
        "TW": "Taiwan",
        "MK": "North Macedonia",
        # Add other custom mappings here if needed
    }
    
    regions = []
    for country in pycountry.countries:
        code = country.alpha_2
        name = custom_names.get(code, country.name)
        regions.append({"code": code, "name": name})
    
    return regions

# Default region
def get_default_region(client_ipaddr):
    """Determine the default region using client IP geolocation, fallback to server geolocation or 'US'."""
    # First attempt: Try using client IP if provided
    print("client_ipaddr: ", client_ipaddr)
    if client_ipaddr:
        try:
            client_location = geocoder.ip(client_ipaddr)
            print("client_location: ", client_location)
            if client_location and client_location.country:
                print("Country: ", client_location.country)
                return client_location.country.upper()
        except Exception as e:
            print(f"Client IP geolocation failed: {e}")
    
    # Second attempt: Use server's location (original logic)
    try:
        server_location = geocoder.ip('me')
        if server_location and server_location.country:
            return server_location.country.upper()
    except Exception as e:
        print(f"Server geolocation failed: {e}")
    
    # Final fallback
    return "US"

def get_available_categories(api_key, region_code="US"):
    """Retrieve available YouTube video categories using the YouTube Data API v3."""
    url = f"{creo_base_url}/videoCategories"
    
    params = {
        "part": "snippet",
        "regionCode": region_code,
        "key": api_key
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            error_msg = data["error"]["message"]
            raise Exception(f"YouTube API Error: {error_msg}")
        
        categories = []
        for item in data.get("items", []):
            if item["snippet"].get("assignable"):
                categories.append(item["snippet"]["title"])
        
        return sorted(categories)
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to connect to YouTube API: {str(e)}")
    

def get_trending_keywords(region, category):
    base_keywords = {
        # North America
        "US": ["AI tools 2025", "midjourney prompts", "productivity hacks", "SEO tips", "startup trends", 
            "crypto news", "Tesla updates", "Python tutorials", "side hustle ideas", "college life hacks"],
        "CA": ["Canada PR tips", "Toronto vlogs", "best winter gear", "AI startups Canada", "maple syrup recipes", 
            "hockey highlights", "remote jobs Canada", "immigration news", "indigenous culture", "Canadian real estate"],
        "MX": ["futbol mexicano", "tacos recipes", "narcos series", "Cancun travel tips", "regio montes music", 
            "Spanish learning", "work in USA", "Mexican startups", "Lucha Libre", "Día de Muertos"],

        # Europe
        "GB": ["Premier League", "UK visa updates", "London vlogs", "Brexit news", "British slang", 
            "tech jobs UK", "royal family gossip", "fish and chips recipe", "Scottish highlands travel", "AI regulations UK"],
        "DE": ["Bundesliga highlights", "German language tips", "Berlin startups", "Oktoberfest guide", "sausage recipes", 
            "car industry news", "study in Germany", "sustainability trends", "techno music", "EU politics"],
        "FR": ["Ligue 1 goals", "Paris travel vlogs", "French cuisine", "AI in France", "strike updates", 
            "wine tasting", "fashion trends 2025", "Disneyland Paris", "immigration laws", "Daft Punk remixes"],
        "IT": ["Serie A goals", "pasta recipes", "Italian lakes travel", "Ferrari news", "mama mia memes", 
            "work in Italy", "Venice vlogs", "Eurovision Italy", "luxury fashion", "Roman history"],
        "ES": ["La Liga highlights", "Ibiza party vlogs", "paella recipe", "Spanish property", "Sagrada Familia", 
            "flamenco music", "digital nomad Spain", "El Clásico", "tomato festival", "Catalan independence"],

        # Africa
        "NG": ["naija vlogs", "japa success stories", "BB Naija updates", "tech in Nigeria", "Afrobeats mix", 
            "Lagos traffic", "Nollywood movies", "Jollof rice wars", "remote jobs Nigeria", "politics today"],
        "ZA": ["load shedding updates", "Cape Town travel", "digital banking SA", "entrepreneur success", "amapiano hits", 
            "Kruger Park safari", "South African slang", "rugby world cup", "Mandela quotes", "township tours"],
        "KE": ["Nairobi hustle", "Safaricom news", "Maasai culture", "Kenyan comedy", "SGR train updates", 
            "KOT trends", "tea farming", "wildlife documentaries", "Swahili lessons", "M-Pesa transfer"],
        "EG": ["Pyramids tours", "Cairo traffic", "Egyptian cotton", "Ramadan recipes", "Nile cruise deals", 
            "El Sisi news", "Arabic lessons", "tech startups Egypt", "football league", "digital nomad visa"],
        "GH": ["Accra nightlife", "jollof recipe Ghana", "Asakaa drill music", "Year of Return", "tech in Ghana", 
            "Kumasi market", "cedi exchange rate", "Ghana jollof vs Nigeria", "university rankings", "kente fashion"],
        "TZ": ["Zanzibar beaches", "Serengeti safari", "Swahili proverbs", "Dodoma vs Dar", "bongo flava", 
            "Tanzanite mining", "Kilimanjaro hikes", "Samia Suluhu", "local markets", "ferry to Pemba"],
        "ET": ["Addis Ababa growth", "Ethiopian coffee", "Lucy skeleton", "Airlines expansion", "orthodox Christianity", 
            "injera recipes", "Lalibela churches", "running champions", "Amharic phrases", "Horn of Africa politics"],

        # Asia
        "IN": ["Bollywood trailers", "cricket highlights", "IIT preparation", "Indian wedding ideas", "tech jobs Bangalore", 
            "chai recipes", "stock market tips", "visa processing time", "Hindi movies", "coding interview prep"],
        "JP": ["anime releases", "Tokyo Olympics legacy", "ramen recipes", "cherry blossom forecast", "Japanese learning", 
            "vending machine culture", "Nintendo news", "karaoke hits", "remote work Japan", "minimalist living"],
        "CN": ["mandarin lessons", "Chinese New Year 2025", "tech innovations China", "dim sum recipes", "Chinese dramas", 
            "Alibaba deals", "study abroad programs", "EV market trends", "traditional medicine", "Great Wall tours"],
        "KR": ["K-pop new releases", "Korean skincare routine", "Seoul food tour", "Squid Game season 2", "Korean language tips", 
            "Samsung products", "Jeju Island travel", "kimchi recipe", "study in Korea", "esports tournaments"],
        "SG": ["Singapore hawker food", "MRT updates", "condo prices", "tech jobs Singapore", "Gardens by the Bay", 
            "Singlish phrases", "Singapore PR application", "staycation deals", "financial literacy", "NS for PRs"],

        # Oceania
        "AU": ["AFL highlights", "Sydney property market", "Great Barrier Reef tours", "Australian slang", "working holiday visa", 
            "Aussie BBQ recipes", "bushfire updates", "Melbourne coffee culture", "kangaroo facts", "cricket scores"],
        "NZ": ["All Blacks rugby", "Lord of the Rings locations", "Kiwi slang", "Auckland property", "Māori culture", 
            "New Zealand visa", "Wellington cafes", "sheep farming", "Hobbiton tours", "earthquake updates"],
        "FJ": ["Fiji vacation deals", "kava ceremony", "island hopping", "Fijian language", "rugby sevens", 
            "traditional food", "climate change impact", "coral reef protection", "digital nomad Fiji", "resort reviews"],

        # South America
        "BR": ["samba lessons", "Amazon rainforest tours", "Brazilian BBQ", "Carnival 2025", "football highlights", 
            "Rio beaches", "Portuguese lessons", "favela tours", "investment opportunities", "capoeira videos"],
        "AR": ["Messi highlights", "tango lessons", "mate tea benefits", "Buenos Aires nightlife", "Argentine beef", 
            "inflation updates", "Patagonia hiking", "Mendoza wine tour", "digital nomad Argentina", "economic news"],
        "CO": ["Colombian coffee", "Medellín transformation", "reggaeton hits", "digital nomad Colombia", "peso exchange", 
            "arepas recipe", "cartel history", "Encanto locations", "Spanish immersion", "remote work visa"],
        "CL": ["Chilean wine", "Santiago startups", "Patagonia trekking", "earthquake safety", "empanada recipes", 
            "Atacama Desert tours", "Chilean slang", "lithium mining news", "winter ski resorts", "political updates"],

        # Middle East
        "AE": ["Dubai property", "Burj Khalifa views", "UAE golden visa", "Abu Dhabi attractions", "Ramadan decorations", 
            "desert safari", "Expo 2025", "remote work Dubai", "tax-free living", "luxury shopping"],
        "SA": ["Saudi Vision 2030", "Riyadh Season", "NEOM updates", "tourist visa Saudi", "Makkah live", 
            "Arabic coffee recipe", "Saudi startups", "Red Sea project", "women driving Saudi", "desert camping"],
        "IL": ["Tel Aviv tech scene", "Israeli startups", "Dead Sea benefits", "Jerusalem tours", "hummus recipe", 
            "kibbutz volunteering", "Hebrew lessons", "Middle East politics", "Mediterranean beaches", "innovation ecosystem"],
        "TR": ["Istanbul street food", "Cappadocia balloons", "Turkish coffee reading", "lira exchange rate", "Bosphorus cruise", 
            "Turkish dramas", "property investment", "digital nomad Turkey", "baklava recipe", "ancient ruins tours"]
    }

    fallback = ["trending now", "viral video", "content growth", "audience engagement", "video marketing"]
    raw_keywords = base_keywords.get(region.upper(), fallback)

    print("category: ", category)
    # Optional category mix
    if category:
        #raw_keywords = [f"{category.lower()} {kw}" for kw in raw_keywords]
        raw_keywords = [str(item).lower() if isinstance(item, str) else item for item in category]

    keyword_list = [{"name": kw, "score": random.randint(55, 100)} for kw in raw_keywords]
    timestamp = (datetime.now() - timedelta(minutes=random.randint(5, 30))).strftime("%Y-%m-%d %H:%M")

    return keyword_list, timestamp


@cached(expiry_seconds=86400)  # Cache for 1 day
@handle_api_error
def get_category_distribution(region):
    """Get the distribution of video categories in trending content"""
    youtube = get_youtube_client()
    
    # First, get category list
    categories_response = youtube.videoCategories().list(
        part="snippet",
        regionCode=region
    ).execute()
    
    category_names = {
        item['id']: item['snippet']['title'] 
        for item in categories_response.get('items', [])
    }
    
    # Get trending videos with category info
    videos_response = youtube.videos().list(
        part="snippet",
        chart="mostPopular",
        regionCode=region,
        maxResults=50
    ).execute()
    
    # Count categories
    category_counts = Counter()
    for item in videos_response.get('items', []):
        category_id = item['snippet']['categoryId']
        category_counts[category_id] += 1
    
    # Prepare results with proper names
    results = []
    for cat_id, count in category_counts.most_common():
        if cat_id in category_names:
            results.append({
                "name": category_names[cat_id],
                "count": count,
                "percentage": round(count * 100 / sum(category_counts.values()), 1)
            })
    
    return results

@cached(expiry_seconds=86400)
@handle_api_error
def get_category_age_distribution(region):
    """
    Simulate age distribution of viewers for trending video categories.
    Args:
        region (str): e.g., 'US', 'IN'
    Returns:
        dict: {category_name: {age_group: view_count}}
    """
    youtube = get_youtube_client()

    # 1. Get category names
    categories_response = youtube.videoCategories().list(
        part="snippet",
        regionCode=region
    ).execute()

    category_names = {
        item['id']: item['snippet']['title']
        for item in categories_response.get('items', [])
        if item['snippet'].get('assignable')  # only actual video categories
    }

    # 2. Get trending videos
    videos_response = youtube.videos().list(
        part="snippet,statistics",
        chart="mostPopular",
        regionCode=region,
        maxResults=50
    ).execute()

    
    AGE_GROUPS = ["13-17", "18-24", "25-34", "35-44", "45-54", "55+"]
    AGE_DISTRIBUTION = {
        "13-17": 0.05,        "18-24": 0.20,        "25-34": 0.35,        "35-44": 0.20,        "45-54": 0.12,         "55+":   0.08
    }

    category_age_data = defaultdict(lambda: {
        "13-17": 0,        "18-24": 0,        "25-34": 0,        "35-44": 0,        "45-54": 0,         "55+": 0,
        "total_views": 0
    })
    # 3. Simulated age groups with weighted distribution
    #AGE_GROUPS = ["13-17", "18-24", "25-34", "35-44", "45-54", "55+"]
    AGE_WEIGHTS = [0.08, 0.25, 0.30, 0.18, 0.12, 0.07]  # simulated weights
    AGE_WEIGHTS = [0.05, 0.20, 0.35, 0.20, 0.12, 0.08] 

    #category_age_data = defaultdict(lambda: {
    #    "13-17": 0,         "18-24": 0,         "25-34": 0,        "35-44": 0,         "45-54": 0,        "55+": 0,        "total_views": 0
    #})

    # 4. Process each video
    for video in videos_response.get('items', []):
        stats = video.get('statistics', {})
        cat_id = video['snippet'].get('categoryId')
        view_count = int(stats.get('viewCount', 0))

        if not cat_id or cat_id not in category_names:
            continue

        cat_name = category_names[cat_id]
        age_distribution = random.choices(AGE_GROUPS, weights=AGE_WEIGHTS, k=10)

        for age_group in age_distribution:
            share = int(view_count * (1 / len(age_distribution)))
            category_age_data[cat_name][age_group] += share

        category_age_data[cat_name]["total_views"] += view_count

    return category_age_data

def visualise_category_age_distribution(region):
    """
    Create a visualisation of the age distribution for each category.

    Args:
        region (str): Region code (e.g. 'US', 'NG')
    Returns:
        matplotlib.figure.Figure: A horizontal bar chart figure
    """
    data = get_category_age_distribution(region)

    categories = list(data.keys())
    age_groups = ["13-17", "18-24", "25-34", "35-44", "45-54", "55+"]

    # Prepare chart canvas
    fig, ax = plt.subplots(figsize=(14, 8))

    # Bar settings
    bar_width = 0.12
    index = np.arange(len(categories))
    colors = ['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854', '#ffd92f']

    # Loop through each age group to plot
    for i, age_group in enumerate(age_groups):
        values = []
        for category in categories:
            total_views = data[category].get("total_views", 1)  # avoid div-by-zero
            count = data[category].get(age_group, 0)
            percent = (count / total_views) * 100
            values.append(round(percent, 2))
        ax.bar(index + i * bar_width, values, bar_width, label=age_group, color=colors[i])

    # Labels and formatting
    ax.set_xlabel("Categories")
    ax.set_ylabel("View Percentage (%)")
    ax.set_title(f"Age Distribution by YouTube Category in {region}")
    ax.set_xticks(index + bar_width * (len(age_groups) - 1) / 2)
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.legend(title="Age Group")

    plt.tight_layout()
    return fig

def visualise_category_age_distribution_base64(region):
    """
    Create a base64 image of the age distribution bar chart by YouTube category.

    Args:
        region (str): e.g. 'US', 'NG'
    Returns:
        str: base64-encoded PNG image as data URI
    """
    data = get_category_age_distribution(region)
    categories = list(data.keys())
    age_groups = ["13-17", "18-24", "25-34", "35-44", "45-54", "55+"]
    colors = ['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854', '#ffd92f']

    fig, ax = plt.subplots(figsize=(14, 8))
    bar_width = 0.12
    index = np.arange(len(categories))

    for i, age_group in enumerate(age_groups):
        values = []
        for category in categories:
            total_views = data[category].get("total_views", 1)
            count = data[category].get(age_group, 0)
            percent = (count / total_views) * 100
            values.append(round(percent, 2))
        ax.bar(index + i * bar_width, values, bar_width, label=age_group, color=colors[i])

    ax.set_xlabel("Categories")
    ax.set_ylabel("View Percentage (%)")
    ax.set_title(f"Age Distribution by YouTube Category in {region}")
    ax.set_xticks(index + bar_width * (len(age_groups) - 1) / 2)
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.legend(title="Age Group")

    plt.tight_layout()

    # Convert plot to base64 image
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    base64_img = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)  # Clean up
    return f"data:image/png;base64,{base64_img}"


# Simulated top channels
@cached(expiry_seconds=86400)
@handle_api_error
def get_top_channels(region):
    """
    Get top channels from trending videos in the specified region.
    
    Args:
        region (str): ISO region code (e.g. 'US', 'NG', 'IN')

    Returns:
        (list of dict, str): List of channel info + timestamp
    """
    youtube = get_youtube_client()

    # Step 1: Get trending videos
    video_resp = youtube.videos().list(
        part="snippet",
        chart="mostPopular",
        regionCode=region,
        maxResults=25
    ).execute()

    # Step 2: Extract unique channel IDs
    channel_map = {}
    for item in video_resp.get("items", []):
        snippet = item.get("snippet", {})
        channel_id = snippet.get("channelId")
        channel_title = snippet.get("channelTitle")
        if channel_id and channel_id not in channel_map:
            channel_map[channel_id] = channel_title

    # Step 3: Get channel stats
    channel_ids = list(channel_map.keys())
    channels_data = []
    
    for i in range(0, len(channel_ids), 50):  # YouTube API allows 50 IDs max per call
        ids_chunk = channel_ids[i:i + 50]
        chan_resp = youtube.channels().list(
            part="snippet,statistics",
            id=",".join(ids_chunk)
        ).execute()

        for chan in chan_resp.get("items", []):
            name = chan["snippet"]["title"]
            subs = chan["statistics"].get("subscriberCount", "0")
            avatar = chan["snippet"]["thumbnails"]["default"]["url"]
            published = chan["snippet"].get("publishedAt", "")

            # Estimate age in years from creation date
            try:
                created_date = datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ")
                years = max(1, int((datetime.utcnow() - created_date).days // 365))
                age_label = f"{years}+ yrs"
            except:
                age_label = "N/A"

            channels_data.append({
                "name": name,
                "subscribers": f"{int(subs):,}",
                "avatar_url": avatar,
                "channel_age": age_label
            })

    # Sort by subscriber count descending (if available)
    def sort_key(c):
        try:
            return int(c['subscribers'].replace(",", ""))
        except:
            return 0

    sorted_channels = sorted(channels_data, key=sort_key, reverse=True)[:10]

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    return sorted_channels , timestamp


@cached(expiry_seconds=1800)  # Cache for 30 minutes
@handle_api_error
def fetch_trending_keywords(region, category_id=None, max_results=50):
    """
    Fetch trending keywords with improved analysis and categorisation
    
    Args:
        region (str): Country code (default: GB for United Kingdom)
        category_id (str, optional): YouTube category ID to filter by
        max_results (int): Number of videos to analyse
        
    Returns:
        list: Keyword data with volume and trend indicators
    """
    youtube = get_youtube_client()
    
    # Build request parameters
    params = {
        "part": "snippet,statistics,contentDetails",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": max_results
    }
    
    if category_id:
        params["videoCategoryId"] = category_id
        
    response = youtube.videos().list(**params).execute()
    
    # Extract and process keywords
    all_keywords = []
    keyword_stats = defaultdict(lambda: {"count": 0, "views": 0, "videos": []})
    
    for item in response.get('items', []):
        video_id = item['id']
        title = item['snippet']['title']
        description = item['snippet'].get('description', '')
        tags = item['snippet'].get('tags', [])
        view_count = int(item['statistics'].get('viewCount', 0))
        
        # Extract keywords from title
        title_keywords = extract_keywords_from_title(title)
        all_keywords.extend(title_keywords)
        
        # Process all keywords including tags
        for keyword in set(title_keywords + tags):
            keyword = keyword.lower()
            if len(keyword) > 2:  # Skip very short keywords
                keyword_stats[keyword]["count"] += 1
                keyword_stats[keyword]["views"] += view_count
                keyword_stats[keyword]["videos"].append({
                    "id": video_id,
                    "title": title,
                    "views": view_count
                })
    
    # Calculate keyword metrics and rank
    result = []
    for keyword, data in keyword_stats.items():
        if data["count"] > 1:  # Only include keywords that appear multiple times
            avg_views = data["views"] / data["count"]
            result.append({
                "name": keyword,
                "volume": data["count"] * 100,  # Weighted volume
                "avg_views": int(avg_views),
                "videos_count": data["count"],
                "trend_score": int((data["count"] * avg_views) / 10000)  # Trend score formula
            })
    
    # Sort by trend score (combined frequency and views)
    result.sort(key=lambda x: x["trend_score"], reverse=True)
    return result[:max_results]  # Return top 15 keywords





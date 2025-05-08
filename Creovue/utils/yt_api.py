"""Module: yt_api.py."""
# utils/yt_api.py
import requests
import datetime
import time
import datetime



from Creovue.app_secets import creo_api_key, cre_base_url

def fetch_youtube_analytics(channel_id, metrics='views,subscribersGained', days=30):
    #print(channel_id, metrics); #time.sleep(300)
    """
    Fetch YouTube channel statistics for the specified channel.
    
    Args:
        channel_id (str): The YouTube channel ID
        metrics (str): Comma-separated metrics to retrieve (only used in function signature)
        days (int): Number of days to look back (only used in function signature)
        
    Returns:
        dict: Channel statistics
        
    Raises:
        Exception: If the channel ID or API key is invalid
    """
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days)
    
    url = f'{cre_base_url}/channels'
    params = {
        'part': 'statistics',
        'id': channel_id,  # Fixed: Use the parameter instead of hardcoded value
        'key': creo_api_key
    }

    #print("params: ", params)
    
    response = requests.get(url, params=params)
    data = response.json()
    #print(data); #time.sleep(300)
    # Add debug information
    if response.status_code != 200:
        error_message = f"API Error: Status code {response.status_code}"
        if "error" in data and "message" in data["error"]:
            error_message += f" - {data['error']['message']}"
        raise Exception(error_message)
    
    if "items" not in data or not data["items"]:
        raise Exception("Invalid channel ID or no data returned.")
        
    return data['items'][0]['statistics']

def validate_api_key():
    """
    Simple function to validate if the API key works at all.
    
    Returns:
        bool: True if the API key is valid, False otherwise
    """
    test_url = f"{cre_base_url}/videos"
    params = {
        'part': 'snippet',
        'chart': 'mostPopular',
        'maxResults': 1,
        'key': creo_api_key
    }
    
    response = requests.get(test_url, params=params)
    return response.status_code == 200

def fetch_trending_keywords():
    return [
        {"name": "AI tools", "volume": 4800},
        {"name": "video SEO", "volume": 3200},
        {"name": "YouTube algorithm", "volume": 2700}
    ]

def fetch_top_channels():
    return [
        {"name": "TechGuru", "subscribers": "1.2M"},
        {"name": "SEO Insights", "subscribers": "890K"},
        {"name": "ContentLab", "subscribers": "760K"}
    ]

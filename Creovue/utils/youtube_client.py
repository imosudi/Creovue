# Creovue/utils/youtube_client.py

import os
from googleapiclient.discovery import build
from Creovue.config import creo_api_key

def get_youtube_client():
    """
    Returns an authenticated YouTube Data API client.
    Requires `creo_api_key` to be defined in app_secrets.py
    """
    return build("youtube", "v3", developerKey=creo_api_key)

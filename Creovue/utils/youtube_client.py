# Creovue/utils/youtube_client.py
from flask import session
from google.oauth2.credentials import Credentials
import requests
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

import os
from googleapiclient.discovery import build
from Creovue.config import creo_api_key

def get_youtube_client():
    """
    Returns an authenticated YouTube Data API client.
    Requires `creo_api_key` to be defined in app_secrets.py
    """
    return build("youtube", "v3", developerKey=creo_api_key)



def ensure_channel_id():
    """
    If the current_user has no channel_id, query YouTube API to get it
    using their session token and update the DB.
    """
    from Creovue import db, app  # Avoid circular import

    if 'youtube_token' not in session:
        return

    if current_user.is_authenticated and not current_user.channel_id:
        creds = Credentials(**session['youtube_token'])

        response = requests.get(
            'https://www.googleapis.com/youtube/v3/channels',
            headers={'Authorization': f'Bearer {creds.token}'},
            params={'part': 'snippet', 'mine': 'true'}
        )

        data = response.json()
        items = data.get('items', [])

        if items:
            channel_id = items[0]['id']
            current_user.channel_id = channel_id
            try:
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                app.logger.error(f"Failed to update user with channel_id: {str(e)}")

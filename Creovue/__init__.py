#!/usr/bin/env python3
# Creovue/__init__.py

# Standard library imports
import os
import sys
import platform
import time

# Third-party imports
from flask import Flask
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from authlib.integrations.flask_client import OAuth

# Local application imports
from Creovue.matplotlib_cache_check import setup_matplotlib_cache
from .filters import format_number
from .config import (
    creo_appdb_host,
    creo_appdb_name,
    creo_appdb_user,
    creo_appdb_pass,
    flask_secret,
    flask_password_salt,
    creo_mail_server,
    creo_mail_default_sender,
    creo_mail_username,
    creo_mail_password,
    creo_mail_tls,
    creo_mail_ssl,
    creo_oauth_client_id,
    creo_oauth_client_secret,
    creo_google_redirect_uri,
    creo_google_auth_scope,
    creo_google_auth_uri,
    creo_google_token_uri,
    creo_google_auth_base_uri,
    creo_google_auth_redirect_uri
)

# Check matplotlib cache setup
if not setup_matplotlib_cache():
    exit(1)

# Commented out Python path manipulation code
'''
py_vers = (".").join(platform.python_version().split(".")[:2])
dir_path = os.path.dirname(os.path.realpath(__file__)).strip("Creovue")
python_path = os.path.join(dir_path, f"venv/lib/python{py_vers}/site-packages")
sys.path.insert(0, python_path)
'''

# Commented out print debug statements
# print(creo_mail_server, creo_mail_default_sender, creo_mail_username, creo_mail_password, creo_mail_tls, creo_mail_ssl)

# Config class reference
# Config, ProductionConfig, DevelopmentConfig

app = Flask(__name__)
# Construct the URI
#Creovue.config.from_object(Config) 

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{creo_appdb_user}:{creo_appdb_pass}@{creo_appdb_host}/{creo_appdb_name}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = flask_secret

# SECURITY CONFIGURATIONS
## Essential security settings
app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'
app.config['SECURITY_PASSWORD_SALT'] = flask_password_salt  # from your .env or config.py

## Enable features
app.config['SECURITY_REGISTERABLE'] = False
app.config['SECURITY_RECOVERABLE'] = False
app.config['SECURITY_CONFIRMABLE'] = False  # disable email confirmation for dev
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SECURITY_TRACKABLE'] = True
app.config['SECURITY_PASSWORD_SINGLE_HASH'] = False

## Redirects
app.config['SECURITY_POST_LOGIN_VIEW'] = '/dashboard'
app.config['SECURITY_POST_LOGOUT_VIEW'] = '/'
app.config['SECURITY_POST_REGISTER_VIEW'] = '/dashboard'




# Email configuration
app.config['MAIL_SERVER']               = creo_mail_server 
app.config['MAIL_PORT']                 = 587 #465 #creo_mail_server_port #465
app.config['MAIL_USE_TLS']              = creo_mail_tls #True #creo_mail_tls #True
app.config['MAIL_USE_SSL']              = creo_mail_ssl #False #creo_mail_ssl #False
app.config['MAIL_USERNAME']             = creo_mail_username 
app.config['MAIL_PASSWORD']             = creo_mail_password 
app.config['MAIL_DEFAULT_SENDER']       = creo_mail_default_sender 
app.config['SECURITY_EMAIL_SENDER']     = creo_mail_default_sender, 

#print("creo_oauth_client_id: ", creo_oauth_client_id, "\n", "creo_oauth_client_secret: ",  creo_oauth_client_secret, "\n", "creo_google_redirect_uri: ", creo_google_redirect_uri)
app.config["GOOGLE_CLIENT_ID"]          = creo_oauth_client_id
app.config["GOOGLE_CLIENT_SECRET"]      = creo_oauth_client_secret
app.config["GOOGLE_REDIRECT_URI"]      = creo_google_redirect_uri
app.config["GOOGLE_AUTH_SCOPE"]          = creo_google_auth_scope


# Google Oauth
app.config["SECURITY_OAUTH_ENABLE"] = True
app.config["SECURITY_OAUTH_PROVIDERS"] = {
    "google": {
        "consumer_key": creo_oauth_client_id,
        "consumer_secret": creo_oauth_client_secret,
        "request_token_params": {
            "scope": ["openid", "https://www.googleapis.com/auth/userinfo.profile",
                       "https://www.googleapis.com/auth/userinfo.email",
                       "https://www.googleapis.com/auth/youtube.readonly"  # For user authentication
            #'https://www.googleapis.com/auth/youtube.readonly'  # For YouTube access
        ]
        },
        "authorize_url": creo_google_auth_uri,
        "access_token_url": creo_google_token_uri,
        "base_url": creo_google_auth_base_uri,
        "client_kwargs": {
            "scope": ["openid", "https://www.googleapis.com/auth/userinfo.profile",
                       "https://www.googleapis.com/auth/userinfo.email",
                       "https://www.googleapis.com/auth/youtube.readonly"  # For user authentication
            #'https://www.googleapis.com/auth/youtube.readonly'  # For YouTube access
        ]
        },
        #"redirect_uri": creo_google_redirect_uri
        "redirect_uri": creo_google_auth_redirect_uri
    }
}



app.jinja_env.filters['format_number'] = format_number


db          = SQLAlchemy(app)
migrate     = Migrate(app, db)
moment      = Moment(app)
mail        = Mail(app)
oauth       = OAuth(app)

google = oauth.register(
    name='google',
    client_id=app.config["SECURITY_OAUTH_PROVIDERS"]["google"]["consumer_key"],
    client_secret=app.config["SECURITY_OAUTH_PROVIDERS"]["google"]["consumer_secret"],
    access_token_url=app.config["SECURITY_OAUTH_PROVIDERS"]["google"]["access_token_url"],
    authorize_url=app.config["SECURITY_OAUTH_PROVIDERS"]["google"]["authorize_url"],
    api_base_url=app.config["SECURITY_OAUTH_PROVIDERS"]["google"]["base_url"],
    client_kwargs=app.config["SECURITY_OAUTH_PROVIDERS"]["google"]["client_kwargs"]
)


import Creovue.routes

# mkdir -p /home/mosud/dev/Creovue/Creovue/static/uploads
# mkdir -p /home/mosud/dev/Creovue/Creovue/static/heatmaps
# sudo chmod 755 /home/mosud/dev/Creovue/Creovue/static/uploads
# mkdir -p Creovue/static/uploads
# mkdir -p Creovue/static/heatmaps
# chmod -R 775 Creovue/static
#pip install pytesseract
#sudo apt install tesseract-ocr  # or brew install tesseract on macOS

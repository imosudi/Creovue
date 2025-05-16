#!/usr/bin/env python3
#Creovue/__init__.py
import os, sys, platform

py_vers = (".").join(platform.python_version().split(".")[:2])
dir_path = os.path.dirname(os.path.realpath(__file__)).strip("Creovue")
#print(py_vers, dir_path)
python_path = os.path.join(dir_path, f"venv/lib/python{py_vers}/site-packages")
#print("python_path: ", python_path)
sys.path.insert(0, python_path)


import time
from flask import       Flask
from flask_moment       import Moment
from flask_migrate      import Migrate
from flask_sqlalchemy   import SQLAlchemy
from flask_mail         import Mail

from .config            import (
    creo_appdb_host, creo_appdb_name, creo_appdb_user, creo_appdb_pass, flask_secret, flask_password_salt, 
    creo_mail_server, creo_mail_default_sender, creo_mail_username, creo_mail_password, creo_mail_tls, creo_mail_ssl,
    creo_oauth_client_id, creo_oauth_client_secret,creo_google_redirect_uri, creo_google_auth_scope
)
#Config#, ProductionConfig, DevelopmentConfig

#print(creo_mail_server, creo_mail_default_sender, creo_mail_username, creo_mail_password, creo_mail_tls, creo_mail_ssl)
# In __init__.py or wherever you define the app
from .filters import format_number


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
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_RECOVERABLE'] = True
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



app.jinja_env.filters['format_number'] = format_number


db          = SQLAlchemy(app)
migrate     = Migrate(app, db)
moment      = Moment(app)
mail        = Mail(app)


import Creovue.routes
"""App configuration module."""
import os, json
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path) 


def confirmBool(val):
    try:
        if val.lower() == "true":
            return True
        else:
            return False
    except:
        return False    


# Generate a nice key using secrets.token_urlsafe()
flask_secret        = os.environ.get("FLASK_SECRET_KEY",  'PerhapsDi\vv/icultMIO@FICpmbdew223ahKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw') 

# Generate a good salt using: secrets.SystemRandom().getrandbits(128)
flask_password_salt = os.environ.get("FLASK_SECURITY_PASSWORD_SALT",  '0009561423456788536813238617350567801672850963412')
creo_appdb_user=os.environ.get("CREO_DB_USER")
creo_appdb_host=os.environ.get("CREO_DB_HOST")
creo_appdb_name=os.environ.get("CREO_DB_NAME")
creo_appdb_pass=os.environ.get("CREO_DB_PASS")



creo_mail_server         = os.environ.get("CREO_MAIL_SERVER")
#creo_mail_server_port    = int(os.environ.get("CREO_MAIL_PORT"))
creo_mail_ssl            = confirmBool(os.environ.get("CREO_MAIL_USE_SSL"))
creo_mail_tls            = confirmBool(os.environ.get("CREO_MAIL_USE_TLS"))
creo_mail_username       = os.environ.get("CREO_MAIL_USERNAME")
creo_mail_password       = os.environ.get("CREO_MAIL_PASSWORD")
creo_mail_default_sender = os.environ.get("CREO_MAIL_DEFAULT_SENDER")



creo_api_key = os.environ.get('CREO_API_KEY' ) # Note: This creo_appears to be truncated
cre_base_url = os.environ.get('CREO_BASE_URL')
creo_base_url = os.environ.get('CREO_BASE_URL')

# Example: Hardcoded YouTube channel ID and mock data for now
creo_channel_id =os.environ.get('CREO_CHANNEL_ID')
creo_mock_view_history = os.environ.get('CREO_MOCK_VIEW_HISTORY')
try:
    creo_mock_view_history = json.loads(creo_mock_view_history)
except :
    pass

creo_oauth_client_id= os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
creo_oauth_client_secret= os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')
creo_google_redirect_uri= os.getenv("GOOGLE_REDIRECT_URI")
creo_google_auth_scope = "https://www.googleapis.com/auth/youtube.readonly"
creo_google_auth_uri=os.getenv("GOOGLE_AUTH_URI")#https://accounts.google.com/o/oauth2/auth"
creo_google_token_uri=os.getenv("GOOGLE_TOKEN_URI")#https://oauth2.googleapis.com/token"
creo_google_auth_base_uri=os.getenv("GOOGLE_OAUTH_BASE_URL")
#print("creo_oauth_client_id: ", creo_oauth_client_id, "creo_oauth_client_secret: ", creo_oauth_client_secret, "creo_google_redirect_uri: ", creo_google_redirect_uri)
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{creo_appdb_user}:{creo_appdb_pass}@{creo_appdb_host}/{creo_appdb_name}"

class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}

os.environ['MPLCONFIGDIR'] = '/tmp/mpl_cache'
## Ensure:
# sudo mkdir -p /tmp/mpl_cache
# sudo chown www-data:www-data /tmp/mpl_cache
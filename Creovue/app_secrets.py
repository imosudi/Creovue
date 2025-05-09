import json
import os
from dotenv import load_dotenv

from os.path import join, dirname

load_dotenv() 
# Generate a nice key using secrets.token_urlsafe()
flask_secret        = os.environ.get("FLASK_SECRET_KEY",  'PerhapsDi\vv/icultMIO@FICpmbdew223ahKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw') 

# Generate a good salt using: secrets.SystemRandom().getrandbits(128)
flask_password_salt = os.environ.get("FLASK_SECURITY_PASSWORD_SALT",  '0009561423456788536813238617350567801672850963412')


creo_appdb_user=os.environ.get("CREO_DB_USER")
creo_appdb_host=os.environ.get("CREO_DB_HOST")
creo_appdb_name=os.environ.get("CREO_DB_NAME")
creo_appdb_pass=os.environ.get("CREO_DB_PASS")




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
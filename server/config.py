import logging
import os
import sys

AI_API_REMOTE = False

#Hugging face API configs
HUGGING_FACE_API = {
    "api_key": '',
    "provider": 'together',
    'url': 'https://api-inference.huggingface.co/models/'
}

#COUCH DB config
COUCHDB_CONF = {
    "connection_string": "http://localhost:5984/",
    "user": "demo",
    "password": "learning"
}

# Create an App logger, which will be used for debugging.
logger = logging.getLogger("ai_assistance")
logging.basicConfig(filename = 'ai_assistance.log', level = logging.INFO)

# Add utils directory to system paths
child_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(child_dir, '..'))
sys.path.append(parent_dir)

#CORS Config
DEFAULT_UI_PORT = "3000"
DEFAULT_SERVER_PORT = "8000"

ip_address = "localhost"

# Twitter configs:
twitter = {
    'API_KEY': '',
    'API_KEY_SECRET': ''
}

# File storage location
IMAGE_DIR = "/app/img/"

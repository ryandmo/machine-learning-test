import logging
import os
import sys
import socket

#Hugging face API configs
HUGGING_FACE_API = {
    "api_key": '',
    "provider": 'together',
    "model": "deepseek-ai/DeepSeek-R1"
}

#POSSIBLE_FINISH_REASON = ('stop', 'length', 'error', 'eos')
#INCOMPLETE_OR_FAILED_FINISHED_REASON = ('length', 'error')

#COUCH DB config
COUCHDB_CONF = {
    "connection_string": "http://localhost:5984/",
    "user": "demo",
    "password": "learning"
}
PARTITION_NAME = "default"

logger = logging.getLogger("chatbot")
logging.basicConfig(filename = 'chatbot.log', level = logging.INFO)

# Add utils directory to system paths
child_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(child_dir, '..'))
sys.path.append(parent_dir)

#CORS Config
DEFAULT_UI_PORT = "3000"
DEFAULT_SERVER_PORT = "8000"

ip_address = "localhost"
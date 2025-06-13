# creds.py

"""
Load ActiveMQ connection settings from environment variables (with optional .env support).
Ensure you have python-dotenv installed: pip install python-dotenv
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file (if present)
load_dotenv()

# Broker host and port
BROKER = [(
    os.getenv('ACTIVEMQ_HOST', 'localhost'),
    int(os.getenv('ACTIVEMQ_PORT', '61613'))
)]

# Destination (queue or topic)
DEST = os.getenv('ACTIVEMQ_DEST', '/queue/test')

# Credentials
USER = os.getenv('ACTIVEMQ_USER', 'admin')
PASS = os.getenv('ACTIVEMQ_PASS', 'admin')

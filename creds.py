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

# Destinations (queues or topics)
DEST = os.getenv('ACTIVEMQ_DEST', '/queue/test')  # Legacy destination for backward compatibility
SDR_DEST = os.getenv('ACTIVEMQ_SDR_DEST', '/queue/sdr')  # Destination for SDR data
PUBLISHER_DEST = os.getenv('ACTIVEMQ_PUBLISHER_DEST', '/queue/publisher')  # Destination for publisher data

# Credentials
USER = os.getenv('ACTIVEMQ_USER', 'admin')
PASS = os.getenv('ACTIVEMQ_PASS', 'admin')

import stomp
import time
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file (if present)
load_dotenv()

# Get ActiveMQ connection settings from environment variables
BROKER = [(
    os.getenv('ACTIVEMQ_HOST', 'localhost'),
    int(os.getenv('ACTIVEMQ_PORT', '61613'))
)]
USER = os.getenv('ACTIVEMQ_USER', 'admin')
PASS = os.getenv('ACTIVEMQ_PASS', 'admin')
DEST = os.getenv('ACTIVEMQ_SDR_DEST', '/queue/sdr')

# ActiveMQ listener class
class MyListener(stomp.ConnectionListener):
    def on_error(self, headers, message):
        print('ActiveMQ error:', message)
    def on_connected(self, headers):
        print("Connected to ActiveMQ")

def main():
    """Test connection to ActiveMQ and send a test message."""
    try:
        # Setup ActiveMQ connection
        print(f"Connecting to ActiveMQ at {BROKER}...")
        conn = stomp.Connection(host_and_ports=BROKER, heartbeats=(0, 0))
        conn.set_listener('', MyListener())
        conn.connect(login=USER, passcode=PASS, wait=True)
        
        # Send a test message
        test_message = {
            'timestamp': time.time(),
            'message': 'Test message from local machine',
            'test': True
        }
        print(f"Sending test message to {DEST}...")
        conn.send(destination=DEST, body=json.dumps(test_message))
        print("Test message sent successfully!")
        
        # Wait a moment before disconnecting
        time.sleep(1)
        
        # Disconnect
        conn.disconnect()
        print("Disconnected from ActiveMQ")
        print("Test completed successfully!")
        return True
    except Exception as e:
        print(f"Error: {e}")
        print("Test failed!")
        return False

if __name__ == "__main__":
    main()
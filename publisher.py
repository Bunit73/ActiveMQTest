#!/usr/bin/env python3
"""
Sends the current UTC timestamp every second to ActiveMQ via STOMP.
Usage:
    python time_publisher.py
"""
import time
import datetime
import stomp
import creds

def main():
    # Setup STOMP connection (disable heartbeats to avoid background errors)
    conn = stomp.Connection(host_and_ports=creds.BROKER, heartbeats=(0, 0))
    conn.connect(login=creds.USER, passcode=creds.PASS, wait=True)

    try:
        print(f"Connected to broker at {creds.BROKER}")
        print(f"Sending time to {creds.PUBLISHER_DEST} every second...")
        while True:
            # Get current UTC time as ISO string
            now = datetime.datetime.utcnow().isoformat() + 'Z'
            conn.send(
                destination=creds.PUBLISHER_DEST,
                body=now,
                headers={'content-type': 'text/plain'}
            )
            print(f"Sent: {now}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Interrupted by user, shutting down...")
    finally:
        conn.disconnect()

if __name__ == '__main__':
    main()

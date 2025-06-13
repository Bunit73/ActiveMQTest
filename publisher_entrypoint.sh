#!/bin/sh
set -e

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Waiting for ActiveMQ to be fully ready..."
sleep 10

echo "Starting publisher.py..."
python -u publisher.py

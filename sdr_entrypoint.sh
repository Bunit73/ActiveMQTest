#!/bin/sh
set -e

echo "Installing system dependencies for RTL-SDR..."
apt-get update && apt-get install -y librtlsdr0 librtlsdr-dev build-essential python3-dev

echo "Installing Python dependencies..."
# Install all requirements except pyrtlsdr
grep -v "pyrtlsdr" requirements.txt > temp_requirements.txt
pip install -r temp_requirements.txt

# Install pyrtlsdr separately with specific options
echo "Installing pyrtlsdr separately..."
pip install --no-cache-dir --no-binary :all: pyrtlsdr

echo "Verifying installation..."
pip list | grep pyrtlsdr

echo "Testing import..."
python -c "import pyrtlsdr; print('pyrtlsdr import successful')" || echo "pyrtlsdr import failed!"

echo "Waiting for ActiveMQ to be fully ready..."
sleep 30

echo "Starting sdr.py..."
python -u sdr.py

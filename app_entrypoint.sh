#!/bin/sh
set -e

echo "Installing Node.js dependencies..."
npm install

echo "Waiting for ActiveMQ to be fully ready..."
sleep 10

echo "Starting app.js..."
node app.js

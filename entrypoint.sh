#!/usr/bin/env bash
set -e

# 1) Start ActiveMQ in the background
/opt/activemq/bin/activemq start

# 2) Wait until STOMP port is open
echo "Waiting for ActiveMQ STOMP on 61613…"
while ! nc -z localhost 61613; do
  sleep 1
done

# 3) Launch your Node app
exec npm start

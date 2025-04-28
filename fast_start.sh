#!/bin/bash
# Fast startup script for N1O1 Clinical Trials
# This script loads environment variables and starts the application quickly

echo "===== N1O1 Clinical Trials Fast Start ====="

# Load environment variables
source ./load_env.sh

# Kill any existing processes on configured ports (with fallback to 5000)
PORT_TO_CHECK=${PORT:-5000}
echo "Checking for processes on port $PORT_TO_CHECK..."
fuser -k $PORT_TO_CHECK/tcp 2>/dev/null || echo "No process on port $PORT_TO_CHECK"

# Clear any Flask session files that might be causing issues
echo "Clearing Flask session files..."
rm -f flask_session/* 2>/dev/null

# Wait for ports to be released
echo "Waiting for ports to be released..."
sleep 1

# Set strict HTTP/cookie configuration in the runtime environment
echo "Configuring HTTP settings..."
export SESSION_COOKIE_SECURE=False
export PREFERRED_URL_SCHEME=http
export SERVER_NAME=""

# Start the application with the optimized settings
echo "Starting application on port $PORT..."
WORKERS=${GUNICORN_WORKERS:-1}
TIMEOUT=${GUNICORN_TIMEOUT:-300}
KEEP_ALIVE=${GUNICORN_KEEP_ALIVE:-120}

exec gunicorn --bind "0.0.0.0:$PORT" --timeout $TIMEOUT --workers $WORKERS --keep-alive $KEEP_ALIVE main:app
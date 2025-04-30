#!/bin/bash
# This script completely bypasses any environment variable issues
# by directly running the Flask application with Python

# Kill any existing processes on port 5000
echo "Checking for processes on port 5000..."
fuser -k 5000/tcp 2>/dev/null || echo "No processes found on port 5000"

# Give processes time to shut down
sleep 1

# Set environment variables directly without relying on external settings
export PORT=5000
export PREFERRED_URL_SCHEME=http
export SESSION_COOKIE_SECURE=False
export WERKZEUG_RUN_MAIN=true

echo "Starting N1O1 Clinical Trials application on port $PORT using direct Python runner..."

# Run the application using our direct Python starter
python app_starter.py
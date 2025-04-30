#!/bin/bash
# A simple script to run the Flask application with a fixed port
# and proper environment settings

# Kill any running gunicorn processes
pkill -f gunicorn || echo "No gunicorn processes found"
sleep 1

# Set environment variables explicitly
export PORT=5000
export PREFERRED_URL_SCHEME=http
export SESSION_COOKIE_SECURE=False

# Start the server with the hardcoded port value
echo "Starting server on port 5000..."
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
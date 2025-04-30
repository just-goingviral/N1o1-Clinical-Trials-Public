#!/bin/bash
# Kill any existing gunicorn processes
pkill -f gunicorn || echo "No gunicorn processes found"
sleep 1

# Set environment variables
export PORT=5000
export PREFERRED_URL_SCHEME="http"
export SESSION_COOKIE_SECURE="False"
export SERVER_NAME=""

# Start the application with the fixed port
echo "Starting application on port 5000..."
exec gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
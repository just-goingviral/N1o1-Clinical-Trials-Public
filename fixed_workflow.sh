#!/bin/bash
# Fixed workflow starter script with hardcoded port
# This avoids the empty PORT variable issue

# Set environment variables
export PORT=5000
export PREFERRED_URL_SCHEME=http
export SESSION_COOKIE_SECURE=False

# Output debugging information
echo "Starting N1O1 Clinical Trials application with fixed configuration:"
echo "PORT: $PORT"
echo "PREFERRED_URL_SCHEME: $PREFERRED_URL_SCHEME"
echo "SESSION_COOKIE_SECURE: $SESSION_COOKIE_SECURE"

# Start the application using gunicorn with fixed port
exec gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
#!/bin/bash
# Fixed workflow script for N1O1 Clinical Trials application
# This script uses a hardcoded port to prevent empty PORT variable issues

# Set a fixed port
export PORT=5000

# Set environment variables for URL handling
export PREFERRED_URL_SCHEME=http
export SESSION_COOKIE_SECURE=False
export SERVER_NAME=""

# Start the application with the fixed port
exec gunicorn --bind 0.0.0.0:$PORT --reuse-port --reload main:app

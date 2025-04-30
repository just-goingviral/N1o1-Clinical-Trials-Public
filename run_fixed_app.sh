#!/bin/bash
# Simple, reliable Flask application starter

# Set port explicitly to avoid environment variable issues
PORT=5000
export PORT=$PORT
export FLASK_APP=main.py
export FLASK_ENV=development
export PREFERRED_URL_SCHEME=http
export SESSION_COOKIE_SECURE=False

echo "Starting N1O1 Clinical Trials on port $PORT..."

# Run using Flask's built-in server for reliability
python -m flask run --host=0.0.0.0 --port=$PORT
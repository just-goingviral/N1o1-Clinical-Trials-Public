#!/bin/bash
# Simple startup script with explicit port

# Use environment variable PORT or default to 5000
PORT=${PORT:-5000}

# Print startup message
echo "Starting N1O1 Clinical Trials application on port $PORT"

# Run with gunicorn
exec gunicorn --bind "0.0.0.0:$PORT" --workers 1 --timeout 120 main:app
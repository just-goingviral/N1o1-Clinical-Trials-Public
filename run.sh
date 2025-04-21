#!/bin/bash
# Default to port 8080 if PORT environment variable is not set
PORT=${PORT:-8080}
echo "Starting N1O1 Clinical Trials application on port $PORT"
gunicorn --bind 0.0.0.0:$PORT main:app
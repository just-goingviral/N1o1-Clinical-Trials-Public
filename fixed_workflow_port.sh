#!/bin/bash

# This script explicitly sets PORT and other critical environment variables
# to ensure the application starts properly in the Replit workflow environment

# Explicitly set PORT
export PORT=5003

# Set other critical variables
export FLASK_APP=main.py
export PYTHONUNBUFFERED=1

# Print environment for debugging
echo "Starting application with PORT=$PORT"

# Start the application with gunicorn
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 120 main:app

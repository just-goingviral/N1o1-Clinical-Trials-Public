#!/bin/bash
# This script ensures the application starts with proper port configuration
# even if the PORT environment variable is not set

# Set a fixed port for development
export PORT=5000
echo "Setting PORT environment variable to $PORT"

# Enable deployment mode for secure cookies
export REPLIT_DEPLOYMENT=True
echo "Enabling deployment mode for secure cookies"

# Ensure session directory exists with proper permissions
mkdir -p flask_session
chmod 755 flask_session
echo "Session directory checked"

# Run gunicorn with explicit port binding
echo "Starting gunicorn on port $PORT..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 main:app
#!/bin/bash
# This script ensures the application starts with proper port configuration
# using port 5001 to avoid conflicts

# Set custom port to avoid conflicts
export PORT=5001
echo "Using port: $PORT"

# Disable secure cookies for development environment
# This prevents redirect loops
export REPLIT_DEPLOYMENT=False
echo "Disabling secure cookies for development"

# Ensure session directory exists with proper permissions
mkdir -p flask_session
chmod 755 flask_session
echo "Session directory checked"

# Run gunicorn with explicit port binding
echo "Starting gunicorn on port $PORT..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 main:app
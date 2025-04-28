#!/bin/bash
# This script terminates existing processes and starts a fresh instance
# of the application with a clean environment

echo "=== N1O1 Clinical Trials - Reset & Start Script ==="
echo "Terminating existing processes..."

# Kill all existing gunicorn processes
pkill -9 -f gunicorn
echo "Cleaned up gunicorn processes"

# Kill any Python processes that might be holding the port
pkill -9 -f "python.*5000"
pkill -9 -f "python.*5001"
echo "Cleaned up Python processes"

# Clear session files
rm -rf flask_session/*
mkdir -p flask_session
chmod 755 flask_session
echo "Cleared session files"

# Set port and configuration variables
export PORT=5001
echo "Setting PORT=$PORT"

# Disable secure cookies to prevent redirect loops
export SESSION_COOKIE_SECURE=False
export REPLIT_DEPLOYMENT=False
echo "Disabled secure cookies"

# Wait for ports to be fully released
sleep 2
echo "Starting server on port $PORT..."

# Start the application with explicit port binding
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 main:app
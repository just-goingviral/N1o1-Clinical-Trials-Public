#!/bin/bash
# A clean startup script that doesn't rely on environment variables
# This script kills any existing processes on port 5000 and starts the application fresh

echo "Starting N1O1 Clinical Trials clean startup sequence..."

# Kill any processes running on port 5000
echo "Checking for processes on port 5000..."
fuser -k 5000/tcp 2>/dev/null || echo "No process on port 5000"

# Wait a second to ensure ports are released
echo "Waiting for ports to be released..."
sleep 1

# Start the application with a fixed port
echo "Starting application on port 5000..."
export PORT=5000
exec gunicorn --bind 0.0.0.0:5000 --timeout 300 --workers 1 --keep-alive 120 main:app
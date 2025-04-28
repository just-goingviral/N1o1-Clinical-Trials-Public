#!/bin/bash
# Complete reset and startup script
# This script applies all fixes and starts the application cleanly

echo "===== N1O1 Clinical Trials Reset & Start ====="
echo "Applying comprehensive fixes for redirect issues..."

# Run the redirect fix script
python fix_redirects_simple.py

# Kill any existing processes on port 5000
echo "Checking for processes on port 5000..."
fuser -k 5000/tcp 2>/dev/null || echo "No process on port 5000"

# Clear any Flask session files that might be causing issues
echo "Clearing Flask session files..."
rm -f flask_session/* 2>/dev/null

# Wait for ports to be released
echo "Waiting for ports to be released..."
sleep 2

# Set strict HTTP/cookie configuration
echo "Setting strict HTTP configuration..."
export FLASK_RUN_PORT=5000
export PORT=5000
export FLASK_DEBUG=0

# Start the application with fixed settings
echo "Starting application on port 5000..."
exec gunicorn --bind 0.0.0.0:5000 --timeout 300 --workers 1 --keep-alive 120 main:app
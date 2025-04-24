#!/bin/bash
# Fix domain issues script
# Usage: ./fix_domain.sh

echo "Starting domain fix process..."

# Make the Python script executable
chmod +x fix_domain.py

# Run the Python script
python3 fix_domain.py

echo "Domain fix complete, restarting server..."

# Kill any running server processes
pkill -f gunicorn || true

# Clear any existing session files
rm -rf flask_session/* || true

# Restart the server (assuming gunicorn is used)
gunicorn --bind 0.0.0.0:5000 --reload main:app &

echo "Server restarted!"
echo "Please allow a few seconds for the server to initialize before accessing the application."
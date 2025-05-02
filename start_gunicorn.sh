#!/bin/bash

# Super simple Gunicorn starter with hardcoded port
# Avoid any environment variable or configuration issues

echo "Starting N1O1 Clinical Trials application with Gunicorn..."

# Force the PORT value
export PORT=5003

# Run Gunicorn with explicit configuration
gunicorn --bind 0.0.0.0:5003 --workers 1 --threads 8 --timeout 120 main:app

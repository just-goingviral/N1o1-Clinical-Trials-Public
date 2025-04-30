#!/bin/bash
# This script sets the PORT environment variable explicitly before starting the server
export PORT=5000
echo "Starting server with PORT explicitly set to $PORT"
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
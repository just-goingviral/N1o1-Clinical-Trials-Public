#!/bin/bash

# This script starts the N1O1 Clinical Trials application
# It explicitly sets the PORT environment variable to avoid the
# 'not a valid port number' error in the Replit workflow system

# Define port and host explicitly
port=5003
host="0.0.0.0"

echo "Starting N1O1 Clinical Trials application on ${host}:${port}"

# Define environment variables
export PORT=${port}
export FLASK_APP=simple_start.py
export FLASK_ENV=production

# Run the simplest possible server implementation
python simple_start.py

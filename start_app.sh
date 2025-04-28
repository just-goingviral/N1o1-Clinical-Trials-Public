#!/bin/bash
# Ensure port is set
PORT=5000
echo "Starting N1O1 Clinical Trials application on port $PORT"

# Run the application with gunicorn
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
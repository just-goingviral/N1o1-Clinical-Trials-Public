#!/bin/bash
# Run the application with fixed port 5000 regardless of environment variables
echo "Starting N1O1 Clinical Trials application with fixed port 5000..."
exec gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
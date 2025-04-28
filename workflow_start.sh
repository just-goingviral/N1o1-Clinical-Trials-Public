#!/bin/bash
# Special script for workflow - hardcodes everything

echo "Starting N1O1 Clinical Trials application..."
echo "Using fixed port 5000"

# Start with explicitly set port - no env var dependency
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
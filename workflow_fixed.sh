#!/bin/bash
# Fixed workflow script for N1O1 Clinical Trials app
# This addresses the issue with PORT environment variable

# Use hardcoded port value to avoid workflow issues
PORT=5000

echo "Starting N1O1 Clinical Trials app"
echo "Using port: $PORT"

# Ensure we're not using an empty port value
if [ -z "$PORT" ]; then
  echo "Error: PORT is empty, using default 5000"
  PORT=5000
fi

# Clean up any existing processes on this port
echo "Cleaning up port $PORT..."
fuser -k $PORT/tcp 2>/dev/null || true
sleep 1

# Start gunicorn with fixed settings
echo "Starting server on port $PORT..."
exec gunicorn --bind 0.0.0.0:$PORT --reuse-port --reload main:app
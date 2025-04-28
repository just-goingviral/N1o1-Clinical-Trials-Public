#!/bin/bash
# Run with a hardcoded port to prevent environment variable issues
# This script tries multiple ports if the default port is unavailable

echo "N1O1 Clinical Trials - Starting with hardcoded port..."

# Try each port in sequence
for PORT in 5000 8080 3000 3333 5001; do
  echo "Attempting to start on port $PORT..."
  
  # Check if port is already in use
  if lsof -i :$PORT > /dev/null 2>&1; then
    echo "Port $PORT is already in use, trying to kill the process..."
    fuser -k $PORT/tcp 2>/dev/null
    sleep 2
  fi
  
  # Try to start on this port
  echo "Starting on port $PORT..."
  gunicorn --bind 0.0.0.0:$PORT --timeout 300 --workers 1 --keep-alive 120 main:app
  
  # If we get here, the start failed
  echo "Failed to start on port $PORT, trying next port..."
  sleep 1
done

echo "ERROR: Could not start on any port. Please check for processes using ports and try again."
exit 1
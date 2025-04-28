#!/bin/bash
# Multi-port workflow launcher
# This script tries multiple ports until it finds an available one

# Output diagnostic information
echo "N1O1 Clinical Trials starting..."
echo "Working directory: $(pwd)"
echo "Current user: $(whoami)"
echo "Process ID: $$"

# Try each port in sequence
for PORT in 5000 5001 8080 3000 3333; do
  echo "Attempting to start on port $PORT..."
  
  # Try to kill any process on this port (ignore errors)
  fuser -k $PORT/tcp 2>/dev/null || true
  sleep 1
  
  # Try to start on this port with a timeout
  timeout 5s gunicorn --bind 0.0.0.0:$PORT --reload main:app &
  PID=$!
  
  # Wait briefly to see if it starts
  sleep 3
  
  # Check if the process is still running
  if kill -0 $PID 2>/dev/null; then
    echo "Successfully started on port $PORT (PID: $PID)"
    # Detach from this process and let it run
    disown $PID
    exit 0
  else
    echo "Failed to start on port $PORT, trying next port..."
  fi
done

echo "Error: Could not start on any port."
exit 1

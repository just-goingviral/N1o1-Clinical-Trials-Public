#!/bin/bash
# Reliable workflow script with hardcoded settings
# This script ensures the application starts regardless of environment issues

# Always use these fixed settings
FIXED_PORT=5000
FIXED_WORKERS=1
FIXED_TIMEOUT=300

# Diagnostic output
echo "Starting N1O1 Clinical Trials with fixed settings:"
echo "- Port: $FIXED_PORT"
echo "- Workers: $FIXED_WORKERS"
echo "- Timeout: $FIXED_TIMEOUT"

# Attempt to kill any existing process on this port
fuser -k $FIXED_PORT/tcp 2>/dev/null || echo "No existing process on port $FIXED_PORT"
sleep 2

# Use a direct command with all parameters hardcoded - no variables
exec gunicorn --bind 0.0.0.0:5000 --timeout 300 --workers 1 --keep-alive 120 main:app

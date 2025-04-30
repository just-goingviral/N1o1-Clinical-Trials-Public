#!/bin/bash
# Script to directly update the workflow command in the Replit environment
# This avoids restarting through the UI

# Set the fixed command
echo "Setting workflow command to use PORT=5000..."
echo "export PORT=5000 && gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app" > WORKFLOW_COMMAND.txt

# Print confirmation
echo "Updated WORKFLOW_COMMAND.txt to use explicit PORT value"
cat WORKFLOW_COMMAND.txt

# Try to run the application directly
echo "Starting application directly..."
export PORT=5000
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
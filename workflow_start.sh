#!/bin/bash
# Workflow startup script with port handling

# Load configuration if available
if [ -f "workflow_config.txt" ]; then
  source <(grep -v '^#' workflow_config.txt)
  echo "Configuration loaded from workflow_config.txt"
else
  # Default settings if config not available
  DEFAULT_PORT=5000
  WORKERS=1
  TIMEOUT=300
  KEEP_ALIVE=120
  echo "Using default configuration"
fi

# Set default PORT if not provided
if [ -z "$PORT" ]; then
  export PORT=$DEFAULT_PORT
  echo "PORT environment variable not set, using default: $PORT"
fi

# Ensure PORT is a valid number
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
  echo "Invalid PORT value: '$PORT', using default 5000 instead"
  export PORT=5000
fi

# Start the application with the PORT environment variable
echo "Starting application on port $PORT with $WORKERS workers"
exec gunicorn --bind "0.0.0.0:$PORT" --reuse-port --reload --timeout $TIMEOUT --workers $WORKERS --keep-alive $KEEP_ALIVE main:app
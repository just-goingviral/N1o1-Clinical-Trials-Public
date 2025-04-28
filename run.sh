#!/bin/bash
# Fixed run script to handle PORT environment variable properly

# Set a default port if PORT is not defined or is empty
if [ -z "${PORT}" ]; then
  export PORT=5000
  echo "PORT was not set, using default port: 5000"
else
  echo "Using PORT: ${PORT}"
fi

# Launch the application with the correct port
echo "Starting application on 0.0.0.0:${PORT}..."
exec gunicorn --bind "0.0.0.0:${PORT}" --timeout 300 --workers 1 --keep-alive 120 --log-level info main:app
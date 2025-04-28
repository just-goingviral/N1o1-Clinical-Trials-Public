#!/bin/bash

# Set default port if not provided
export PORT=${PORT:-5000}

# Start the application
exec gunicorn --bind 0.0.0.0:$PORT --reuse-port --reload main:app
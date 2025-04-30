#!/bin/bash
# Fixed script for starting the application with a hardcoded port
export PORT=5000
export PREFERRED_URL_SCHEME=http
export SESSION_COOKIE_SECURE=False
export SERVER_NAME=

# Start the server on a fixed port
exec gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
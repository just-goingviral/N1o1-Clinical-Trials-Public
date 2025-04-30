#!/bin/bash
# Fixed workflow command with hardcoded port 5000
export PORT=5000
export PREFERRED_URL_SCHEME=http
export SESSION_COOKIE_SECURE=False

# Start the server on a fixed port
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
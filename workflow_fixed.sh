#!/bin/bash
# Fixed workflow script with explicit port setting
export PORT=5000
export PREFERRED_URL_SCHEME=http
export SESSION_COOKIE_SECURE=False

# Start the server on port 5000
exec gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
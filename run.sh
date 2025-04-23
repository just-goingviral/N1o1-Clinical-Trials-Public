#!/bin/bash
export PORT=${PORT:-5000}
echo "Starting server on port $PORT for domain $REPLIT_DEPLOYMENT_DOMAIN"
gunicorn --bind 0.0.0.0:$PORT --timeout 300 --workers 1 --keep-alive 120 main:app

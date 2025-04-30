#!/bin/bash
# Start the Flask application with a fixed port
export PORT=5000
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
#!/bin/bash
# Set a fixed port value
PORT=5000
echo "PORT set to $PORT"

# Run the application with the explicit port
exec gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
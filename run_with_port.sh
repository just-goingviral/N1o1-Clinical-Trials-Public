
#!/bin/bash
# Set PORT from environment variable or default to 5000
export PORT=${PORT:-5000}
echo "Starting server on port $PORT"

# Try to kill any process using the port without relying on lsof
# This uses a more basic approach that works in more environments
fuser -k $PORT/tcp 2>/dev/null || echo "No process running on port $PORT or fuser not available"

# Give the system a moment to release the port
sleep 2

# Start the Flask application
exec gunicorn --bind 0.0.0.0:$PORT --timeout 300 --workers 1 --keep-alive 120 main:app

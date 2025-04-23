
#!/bin/bash
# Set PORT from environment variable or default to 5000
export PORT=${PORT:-5000}
echo "Starting server on port $PORT"

# Kill any process using the port
kill -9 $(lsof -t -i:$PORT) 2>/dev/null || echo "No process running on port $PORT"

# Start the Flask application
exec gunicorn --bind 0.0.0.0:$PORT --timeout 300 --workers 1 --keep-alive 120 main:app

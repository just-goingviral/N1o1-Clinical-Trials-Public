
#!/bin/bash
# Explicitly set PORT environment variable and run the Flask app
export PORT=${PORT:-5000}
echo "Starting server on port $PORT"
gunicorn --bind 0.0.0.0:$PORT --timeout 300 --workers 1 --keep-alive 120 main:app


#!/bin/bash
# Default to port 5000 for deployment compatibility
PORT=${PORT:-5000}
echo "Starting N1O1 Clinical Trials application on port $PORT"
gunicorn --bind 0.0.0.0:$PORT --timeout 300 --workers 1 --keep-alive 120 --log-level info main:app

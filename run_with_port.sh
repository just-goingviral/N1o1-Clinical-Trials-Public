
#!/bin/bash
# Improved run script for N1O1 Clinical Trials

# Use PORT from environment or default to 5000
export PORT=${PORT:-5000}
echo "Starting server on port $PORT"

# Try to kill any process running on the port
if command -v fuser &> /dev/null; then
  fuser -k ${PORT}/tcp 2>/dev/null || echo "No process running on port ${PORT} or fuser not available"
else
  echo "fuser not available, skipping port check"
fi

# Run with gunicorn for better production-like environment
exec gunicorn --bind 0.0.0.0:${PORT} --workers=1 --threads=4 --timeout 120 main:app

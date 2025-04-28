#!/bin/bash
# N1O1 Clinical Trials - Fixed Startup Script for Workflows
# This script starts the application with a hardcoded port
# and tries multiple ports if the first one fails
# to prevent the empty PORT environment variable issue

# Print with colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

info() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# Hard-coded ports to try - Never reference $PORT directly
PORTS=(5000 8080 3000 4567 5001)

for FIXED_PORT in "${PORTS[@]}"; do
  info "Attempting to start application on port $FIXED_PORT..."
  
  # Kill any existing process on the port
  info "Cleaning up any existing processes on port $FIXED_PORT..."
  fuser -k $FIXED_PORT/tcp 2>/dev/null || true
  sleep 2
  
  # Verify port is actually free
  if lsof -i:$FIXED_PORT > /dev/null 2>&1; then
    warn "Port $FIXED_PORT is still in use after cleanup. Trying next port..."
    continue
  fi
  
  # Set environment variables
  export PORT="$FIXED_PORT"
  export PREFERRED_URL_SCHEME="http"
  export SERVER_NAME=""
  export SESSION_COOKIE_SECURE="False"
  export FLASK_ENV="production"
  
  info "Starting N1O1 Clinical Trials application on port $FIXED_PORT..."
  info "URL Generation: PREFERRED_URL_SCHEME=$PREFERRED_URL_SCHEME"
  info "Cookie Security: SESSION_COOKIE_SECURE=$SESSION_COOKIE_SECURE"
  
  # Start the application with gunicorn using the hardcoded port directly
  # Use timeout to catch bind errors quickly
  timeout 5 gunicorn --bind "0.0.0.0:$FIXED_PORT" --reuse-port --reload main:app
  
  # Check if gunicorn started successfully
  if [ $? -eq 124 ]; then
    # Timeout occurred, which means it started successfully
    # Now start it properly without the timeout
    info "Port $FIXED_PORT is available. Starting application permanently..."
    exec gunicorn --bind "0.0.0.0:$FIXED_PORT" --reuse-port --reload main:app
    exit 0
  else
    warn "Failed to start on port $FIXED_PORT. Trying next port..."
  fi
done

error "Failed to find an available port after trying all options. Please manually kill processes and try again."
exit 1
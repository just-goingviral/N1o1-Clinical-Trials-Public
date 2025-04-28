#!/bin/bash
# N1O1 Clinical Trials - Robust Application Launcher
# This script tries multiple ports until it finds an available one
# and forces any conflicting processes to terminate.

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

# Configuration for URL generation
export PREFERRED_URL_SCHEME="http"
export SERVER_NAME=""
export SESSION_COOKIE_SECURE="False"
export FLASK_ENV="production"

# Define ports to try in order of preference
PORTS=(5000 8080 5001 3000 4567)

force_kill_all_servers() {
  # Last resort - find and kill all gunicorn processes
  warn "Forcefully killing ALL gunicorn processes..."
  pkill -9 -f gunicorn || true
  # Also kill Python processes serving on ports we might want to use
  for PORT in "${PORTS[@]}"; do
    fuser -k $PORT/tcp 2>/dev/null || true
  done
  # Give it time to close
  sleep 3
}

# First, force cleanup everything as a last resort
force_kill_all_servers

# Try each port in order
for PORT in "${PORTS[@]}"; do
  info "Attempting to start application on port $PORT..."
  
  # Double-check port is free
  if lsof -i:$PORT > /dev/null 2>&1; then
    warn "Port $PORT is still in use. Forcefully terminating the process..."
    fuser -k $PORT/tcp 2>/dev/null
    sleep 2
    
    # Check again
    if lsof -i:$PORT > /dev/null 2>&1; then
      warn "Port $PORT is still busy after cleanup. Skipping to next port..."
      continue
    fi
  fi
  
  # Set the port for the application
  export PORT="$PORT"
  
  info "Starting N1O1 Clinical Trials application on port $PORT..."
  info "URL Generation: PREFERRED_URL_SCHEME=$PREFERRED_URL_SCHEME"
  info "Cookie Security: SESSION_COOKIE_SECURE=$SESSION_COOKIE_SECURE"
  
  # Run gunicorn with proper settings
  exec gunicorn --bind "0.0.0.0:$PORT" --reuse-port --reload main:app
  
  # If exec fails for any reason, continue to next port
  warn "Failed to start on port $PORT. Trying next port..."
done

error "Could not start the application on any port. All available ports are in use."
error "Please manually check running processes with 'ps aux | grep gunicorn' and kill them."
exit 1
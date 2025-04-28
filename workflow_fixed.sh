#!/bin/bash
# N1O1 Clinical Trials - Fixed Workflow Script
# This script starts the application with reliable, hardcoded settings
# that work on both Replit and custom domains

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

# Hard-coded port for reliability
PORT=5000

# Kill any existing process on PORT
info "Cleaning up any existing processes on port $PORT..."
fuser -k $PORT/tcp 2>/dev/null || true
sleep 1

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
  error "gunicorn is not installed. Installing now..."
  pip install gunicorn
fi

# Set environment variables
export PORT=$PORT
export PREFERRED_URL_SCHEME="http"
export SERVER_NAME=""
export SESSION_COOKIE_SECURE="False"
export FLASK_ENV="production"

info "Starting N1O1 Clinical Trials application on port $PORT..."
info "URL Generation: PREFERRED_URL_SCHEME=$PREFERRED_URL_SCHEME"
info "Cookie Security: SESSION_COOKIE_SECURE=$SESSION_COOKIE_SECURE"

# Start the application with gunicorn
exec gunicorn --bind 0.0.0.0:$PORT --reuse-port --reload main:app
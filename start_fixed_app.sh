#!/bin/bash
# N1O1 Clinical Trials - Fixed Application Starter
# This script uses a fixed port and correct environment settings
# to prevent redirect loops and cookie-related issues

# Show colored output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
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

# Kill potentially conflicting processes
info "Cleaning up existing processes..."
pkill -9 -f gunicorn || true
sleep 1

# Set environment variables
export PORT=5000
export PREFERRED_URL_SCHEME=http
export SESSION_COOKIE_SECURE=False
export SERVER_NAME=""

info "Starting application with port $PORT"
info "URL Scheme: $PREFERRED_URL_SCHEME"
info "Cookie Security: $SESSION_COOKIE_SECURE"
info "Server Name: '[dynamic]'"

exec gunicorn --bind 0.0.0.0:$PORT --reuse-port --reload main:app

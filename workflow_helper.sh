#!/bin/bash
# N1O1 Clinical Trials - Workflow Helper
# This script patches the workflow command to use hardcoded port
# instead of relying on environment variables

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

# FIXED PORT SETTINGS
FIXED_PORT=5000

# Kill potentially conflicting processes
info "Cleaning up existing processes on port $FIXED_PORT..."
pkill -f gunicorn || true
fuser -k $FIXED_PORT/tcp 2>/dev/null || true
sleep 2

# Set environment variables
export PORT=$FIXED_PORT
export PREFERRED_URL_SCHEME=http
export SESSION_COOKIE_SECURE=False

info "Starting application with fixed port $FIXED_PORT"
info "URL Scheme: $PREFERRED_URL_SCHEME"
info "Cookie Security: $SESSION_COOKIE_SECURE"

exec gunicorn --bind 0.0.0.0:$FIXED_PORT --reuse-port --reload main:app
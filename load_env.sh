#!/bin/bash
# Load environment variables from .env file

# Load .env file if it exists
if [ -f ".env" ]; then
  echo "Loading environment variables from .env file"
  export $(grep -v '^#' .env | xargs)
  echo "Environment variables loaded"
else
  echo "No .env file found, using defaults"
fi

# Display key settings
echo "PORT: $PORT"
echo "FLASK_APP: $FLASK_APP"
echo "FLASK_ENV: $FLASK_ENV"
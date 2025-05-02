#!/bin/bash

# Fixed workflow shell script for N1O1 Clinical Trials application
# This script explicitly sets the port to 5003 and doesn't rely on environment variables

export PORT=5003
export FLASK_APP=main.py
export FLASK_ENV=production

echo "Starting N1O1 Clinical Trials with fixed port: $PORT"

# Run using python directly - the simplest and most reliable approach
python start_n1o1_standalone.py

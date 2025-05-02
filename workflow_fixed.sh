#!/bin/bash

# Fixed workflow script for N1O1 Clinical Trials application
# This script uses a hardcoded port value to avoid environment variable issues

PORT=5003
HOST="0.0.0.0"

echo "Starting N1O1 Clinical Trials application on ${HOST}:${PORT}"

# Run the application using the standalone server script
python start_n1o1_standalone.py

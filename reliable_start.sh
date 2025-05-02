#!/bin/bash

# Reliable starter script for N1O1 Clinical Trials
# Uses a hardcoded port value to avoid environment variable issues

echo "Starting N1O1 Clinical Trials application..."

# Set environment variables with explicit values
export PORT=5003
export FLASK_APP=reliable_start.py
export PYTHONPATH=.

# Run the application directly with Python
python3 reliable_start.py

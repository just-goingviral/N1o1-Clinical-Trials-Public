#!/bin/bash
# Direct, simplified Flask starter that avoids any PORT variable issues

echo "Starting N1O1 Clinical Trials on port 5000..."

# Use hardcoded port value to avoid environment variable issues
gunicorn --bind 0.0.0.0:5000 --workers 1 --timeout 120 main:app
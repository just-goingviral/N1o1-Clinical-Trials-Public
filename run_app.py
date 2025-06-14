#!/usr/bin/env python3
"""
Simple application runner for N1O1 Clinical Trials
This bypasses any workflow configuration issues
"""
import os
import sys

# Set environment variables
os.environ['PORT'] = '5000'
os.environ['FLASK_ENV'] = 'production'

# Import and run the main application
if __name__ == '__main__':
    from main import app
    print("Starting N1O1 Clinical Trials application on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)
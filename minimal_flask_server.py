#!/usr/bin/env python3
"""
Minimal Flask server for N1O1 Clinical Trials
Removes all dependencies on environment variables and external files
"""

import os
import sys
from flask import Flask

# Create a minimal Flask app
app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>N1O1 Clinical Trials</h1><p>Minimal server running successfully</p>'

@app.route('/health')
def health():
    return '{"status": "ok"}'

def run_server():
    """Run the Flask server directly without gunicorn"""
    # Hard code the port without using environment variables
    port = 5003  # Using a different port to avoid conflicts
    host = '0.0.0.0'
    
    print(f"Starting minimal N1O1 Clinical Trials server on {host}:{port}")
    sys.stdout.flush()  # Ensure output is visible immediately
    
    # Run Flask directly without gunicorn
    app.run(host=host, port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    run_server()

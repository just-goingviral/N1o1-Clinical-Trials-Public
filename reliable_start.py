#!/usr/bin/env python3
"""
Reliable starter script for N1O1 Clinical Trials application
This script hardcodes all critical values to avoid environment variable issues
"""

import os
import sys
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

# Create a minimal Flask application
app = Flask(__name__)

# Handle proxy headers for proper URL generation
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Set a secret key for sessions
app.secret_key = 'n1o1_development_key'

# Import main app only after setting up the Flask instance
from main import app as main_app

# Use the configured application from main.py
app = main_app

# We don't need to add a ping route as it already exists in main.py

if __name__ == '__main__':
    # Hardcode the port to avoid environment variable issues
    port = 5003
    host = '0.0.0.0'
    
    print(f"Starting N1O1 Clinical Trials application on {host}:{port}")
    sys.stdout.flush()
    
    # Run the application
    app.run(host=host, port=port, debug=False, use_reloader=False)

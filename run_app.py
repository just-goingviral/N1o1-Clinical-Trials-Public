#!/usr/bin/env python3
"""
Simple Flask application runner that works reliably in Replit
"""
import os
from main import app

if __name__ == '__main__':
    # Set environment variables for consistent URL scheme and cookies
    os.environ['PREFERRED_URL_SCHEME'] = 'http'
    os.environ['SESSION_COOKIE_SECURE'] = 'False'
    
    # Always use port 5000
    port = 5000
    print(f"Starting N1O1 Clinical Trials application on port {port}")
    
    # Start the application with debug mode disabled
    app.run(host='0.0.0.0', port=port, debug=False)
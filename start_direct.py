#!/usr/bin/env python3
"""
Super minimal direct-start script for N1O1 Clinical Trials
This avoids any environment variable or configuration issues
"""

import os
import sys
from werkzeug.serving import run_simple

# Set environment variables manually to avoid any issues
os.environ['PORT'] = '5003'
os.environ['FLASK_ENV'] = 'production'

# Import the Flask app - needs to be done after setting environment variables
from main import app

if __name__ == "__main__":
    # Hardcode values to avoid any configuration issues
    host = '0.0.0.0'
    port = 5003
    
    print(f"Starting N1O1 Clinical Trials application on {host}:{port}")
    sys.stdout.flush()
    
    try:
        # Use Werkzeug's run_simple to avoid Flask's run method
        run_simple(
            hostname=host,
            port=port,
            application=app,
            use_reloader=False,
            use_debugger=False,
            threaded=True
        )
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

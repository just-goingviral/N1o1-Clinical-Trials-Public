#!/usr/bin/env python3
"""
Simple direct starter for the N1O1 Clinical Trials application
This script runs Flask directly with a hardcoded port value
"""
import os
import sys
from main import app

if __name__ == "__main__":
    # Set essential environment variables
    os.environ["PORT"] = "5000"
    os.environ["PREFERRED_URL_SCHEME"] = "http"
    os.environ["SESSION_COOKIE_SECURE"] = "False"
    os.environ["WERKZEUG_SERVER_FD"] = ""  # Reset any inherited file descriptors
    
    # Hardcode the port to ensure it works
    PORT = 5000
    
    print(f"Starting N1O1 Clinical Trials on port {PORT}...")
    app.run(host="0.0.0.0", port=PORT, debug=True)
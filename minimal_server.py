#!/usr/bin/env python3
"""
Minimal server for N1O1 Clinical Trials
Designed to avoid any workflow or environment variable issues
"""
import os
import sys
import time
from main import app

def run_minimal_server():
    """Run a minimal Flask server with hardcoded port"""
    # Hardcode port to 5000
    PORT = 5000
    
    # Set essential environment variables with fixed values
    os.environ["PORT"] = str(PORT)
    os.environ["PREFERRED_URL_SCHEME"] = "http"
    os.environ["SESSION_COOKIE_SECURE"] = "False"
    os.environ["WERKZEUG_SERVER_FD"] = ""
    
    print(f"Starting N1O1 Clinical Trials on port {PORT}...")
    
    try:
        # Avoid using app.run() as it may cause issues with Replit
        # Instead use werkzeug's server directly
        from werkzeug.serving import run_simple
        run_simple('0.0.0.0', PORT, app, use_reloader=False, use_debugger=True)
    except Exception as e:
        print(f"Error starting server: {e}")
        return False
        
    return True

if __name__ == "__main__":
    # Run server
    run_minimal_server()
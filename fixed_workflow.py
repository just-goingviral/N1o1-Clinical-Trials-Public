#!/usr/bin/env python3
"""
Workflow-compatible server starter for N1O1 Clinical Trials
This version bypasses any environment variable issues by using direct port specification
"""
import os
import sys
import subprocess

def main():
    """Direct starter with hardcoded port value"""
    # Explicitly set the PORT environment variable to avoid errors
    hardcoded_port = 5000
    os.environ["PORT"] = str(hardcoded_port)
    
    # Set other important environment variables
    os.environ["PREFERRED_URL_SCHEME"] = "http"
    os.environ["SESSION_COOKIE_SECURE"] = "False"
    os.environ["WERKZEUG_SERVER_FD"] = ""  # Reset any inherited file descriptors
    
    print(f"Starting N1O1 Clinical Trials on port {hardcoded_port}...")
    
    # Use gunicorn with explicitly specified port
    cmd = [
        "gunicorn",
        "--bind", f"0.0.0.0:{hardcoded_port}",
        "--workers", "1",
        "--timeout", "120",
        "main:app"
    ]
    
    try:
        # Execute the command
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
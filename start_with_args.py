#!/usr/bin/env python3
"""
Command line application starter for N1O1 Clinical Trials
This script runs Flask directly with configurable port value via command line
to avoid environment variable issues in workflows
"""
import os
import sys
import argparse
from main import app

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Start N1O1 Clinical Trials application')
    parser.add_argument('--port', type=int, default=5000, help='Port number (default: 5000)')
    args = parser.parse_args()
    
    # Set essential environment variables
    os.environ["PORT"] = str(args.port)
    os.environ["PREFERRED_URL_SCHEME"] = "http"
    os.environ["SESSION_COOKIE_SECURE"] = "False"
    os.environ["WERKZEUG_SERVER_FD"] = ""  # Reset any inherited file descriptors
    
    print(f"Starting N1O1 Clinical Trials on port {args.port}...")
    app.run(host="0.0.0.0", port=args.port, debug=True)

if __name__ == "__main__":
    main()
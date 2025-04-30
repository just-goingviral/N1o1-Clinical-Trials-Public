#!/usr/bin/env python3
"""
Simple server starter for N1O1 Clinical Trials
Designed to work with Replit's workflow system
"""
import os
import sys

def main():
    print("Starting N1O1 Clinical Trials server...")

    # Hard code the port for reliability
    os.environ["PORT"] = "5000"
    os.environ["PREFERRED_URL_SCHEME"] = "http"
    os.environ["SESSION_COOKIE_SECURE"] = "False"
    
    # Create gunicorn command with explicit port binding
    cmd = f"gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app"
    
    print(f"Executing: {cmd}")
    os.system(cmd)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Minimal Flask launcher for N1O1 Clinical Trials
"""
import os
from flask import Flask
from main import app

if __name__ == "__main__":
    # Set essential environment variables
    os.environ["PORT"] = "5000"
    os.environ["PREFERRED_URL_SCHEME"] = "http"
    os.environ["SESSION_COOKIE_SECURE"] = "False"
    
    print("Starting N1O1 Clinical Trials on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=True)
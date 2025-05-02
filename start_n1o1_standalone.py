#!/usr/bin/env python3
"""
Standalone N1O1 Clinical Trials server
This script provides a minimal but functional version of the main application
without relying on complex initialization or environment variables

The server supports basic routes and system health checks.
It uses a hardcoded port (5003) to avoid any environment variable issues.
"""

import os
import sys
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, jsonify, request

# Create Flask app
app = Flask(__name__)

# Basic configuration to avoid any environment variable issues
app.config['SECRET_KEY'] = 'n1o1-clinical-trials-secure-key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['PREFERRED_URL_SCHEME'] = 'http'

# Routes
@app.route('/')
def index():
    """Main index page"""
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """Dashboard view"""
    return render_template('dashboard.html', title="N1O1 Clinical Trials Dashboard")

@app.route('/patients')
def patients_list():
    """Patients list view"""
    return render_template('patients.html', title="Patients - N1O1 Clinical Trials")

@app.route('/simulation')
def simulation():
    """Simulation view"""
    return render_template('simulation.html', title="Simulation - N1O1 Clinical Trials")

# System health and status endpoints
@app.route('/system/health')
def system_health():
    """System health check"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "server": "N1O1 Clinical Trials - Standalone"
    })

@app.route('/ping')
def ping():
    """Simple ping endpoint"""
    return jsonify({"status": "ok"})
    
# Run the server
def main():
    # Hard code the port without using environment variables
    port = 5003  # Using a non-standard port to avoid conflicts
    host = '0.0.0.0'
    
    print(f"Starting N1O1 Clinical Trials standalone server on {host}:{port}")
    sys.stdout.flush()  # Ensure output is visible immediately
    
    # Run Flask directly
    app.run(host=host, port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    main()

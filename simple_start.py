#!/usr/bin/env python3
"""
Simple direct starter for the N1O1 Clinical Trials application
This is the simplest possible script that can run a Flask server
without any environment dependencies
"""

import sys
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>N1O1 Clinical Trials</h1><p>System is running</p>'

@app.route('/ping')
def ping():
    return '{"status": "ok"}'
    
if __name__ == "__main__":
    port = 5003
    host = '0.0.0.0'
    print(f"Starting super-minimal N1O1 server on {host}:{port}")
    sys.stdout.flush()
    app.run(host=host, port=port, debug=False, use_reloader=False)

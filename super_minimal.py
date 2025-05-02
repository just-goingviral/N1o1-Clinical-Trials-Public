#!/usr/bin/env python3
"""
Super minimal Flask server for N1O1 Clinical Trials
Contains everything in a single file without any external dependencies
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>N1O1 Clinical Trials</h1><p>Test server running successfully</p>'

@app.route('/health')
def health():
    return '{"status": "ok"}'

if __name__ == '__main__':
    port = 5000
    print(f"Starting minimal N1O1 Clinical Trials server on port {port}")
    app.run(host='0.0.0.0', port=port)

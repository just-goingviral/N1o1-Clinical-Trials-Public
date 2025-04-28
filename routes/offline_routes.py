"""
Offline mode routes for N1O1 Clinical Trials
Handles serving the offline page and checking online status
"""

from flask import Blueprint, render_template, jsonify, current_app
import os
import datetime

# Create blueprint
offline_bp = Blueprint('offline', __name__)

@offline_bp.route('/offline')
def offline_page():
    """Serve the offline page"""
    return render_template('offline.html')

@offline_bp.route('/api/server-status')
def server_status():
    """Check if the server is available - used by service worker to detect online status"""
    # Return basic information about the server
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'version': current_app.config.get('VERSION', '1.0.0')
    })

@offline_bp.route('/manifest.json')
def manifest():
    """Serve the PWA manifest file"""
    # This route is needed to ensure the manifest is properly served with the correct MIME type
    from flask import send_from_directory
    return send_from_directory('static', 'manifest.json', mimetype='application/manifest+json')

@offline_bp.route('/service-worker.js')
def service_worker():
    """Serve the service worker JavaScript file"""
    # This route is needed to ensure the service worker is properly served with the correct MIME type
    from flask import send_from_directory
    return send_from_directory('static/js', 'service-worker.js', mimetype='application/javascript')
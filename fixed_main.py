"""
N1O1 Clinical Trials - Main Application
Fixed version with optimized configuration for reliable deployment
"""
import os
import sys
import uuid
import logging
import datetime
import tempfile
import subprocess
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path

from flask import Flask, render_template, redirect, url_for, request, session, jsonify, g, abort, flash
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create app and configure it for reliability
class Base(DeclarativeBase):
    pass

# Create the app
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'n1o1-clinical-trials-dev-key'),
    SESSION_TYPE='filesystem',
    SESSION_PERMANENT=False,
    SESSION_USE_SIGNER=True,
    PERMANENT_SESSION_LIFETIME=timedelta(days=1),
    SESSION_COOKIE_SAMESITE='Lax',  # Allows redirects from other sites
    SESSION_COOKIE_SECURE=False,    # Set to False for HTTP
    SERVER_NAME=None,               # Use the request's host header
    PREFERRED_URL_SCHEME='http',    # Force HTTP scheme for URL generation
)

# Setup database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Fix for reverse proxy and URL generation
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Create database
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Setup login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Add required user loader function
@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    # Return None for now - we'll implement proper user loading later
    return None

# Health check route for deployment verification
@app.route('/system/health')
def system_health():
    """Check system health"""
    try:
        # Check database connection
        db_status = "connected" if db.session.execute("SELECT 1").scalar() == 1 else "disconnected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Return system health information
    return jsonify({
        "status": "online",
        "timestamp": str(datetime.utcnow()),
        "database": db_status,
        "session": "initialized",
        "port": os.environ.get("PORT", "5000"),
        "blueprints": {
            "api": True,
            "patient": True,
            "simulation": True,
            "analyzer": True
        }
    })

@app.route('/ping')
def ping():
    """Simple ping endpoint to keep the app alive"""
    return "pong"

@app.route('/')
def index():
    """Main index page - dashboard"""
    return render_template('index.html', page_title="N1O1 Clinical Trials Dashboard")

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all exceptions for improved reliability"""
    logger.error(f"Unhandled exception: {str(e)}")
    return render_template('error.html', error=str(e)), 500

# Import models to create tables
with app.app_context():
    try:
        # Make sure to import the models here
        sys.path.append('.')  # Ensure current directory is in path
        # Import models if available, but continue if not
        try:
            import models
        except ImportError:
            logger.warning("Models module not found, database tables may not be created")
        
        # Create database tables
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")

# Add safe_url_for to prevent redirect loops
def safe_url_for(endpoint, **kwargs):
    """Generate URLs consistently with HTTP scheme to prevent redirect loops"""
    if '_external' in kwargs and kwargs['_external']:
        kwargs['_scheme'] = 'http'
    return url_for(endpoint, **kwargs)

# Add to template context
@app.context_processor
def inject_safe_url_for():
    """Inject safe_url_for into template context"""
    return dict(url_for=safe_url_for)

# Create safe redirect function to prevent loops
def safe_redirect(endpoint, **kwargs):
    """Generate a redirect that always uses http scheme to prevent loops"""
    target = safe_url_for(endpoint, **kwargs)
    return redirect(target)

if __name__ == '__main__':
    # Use hardcoded port for reliability
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting N1O1 Clinical Trials on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
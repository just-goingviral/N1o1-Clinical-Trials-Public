"""
N1O1 Clinical Trials - Main Application
"""
from flask import Flask, render_template, redirect, url_for, session, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
import os
from werkzeug.middleware.proxy_fix import ProxyFix
from models import db, Patient, Simulation, User, init_db
from routes import analyzer_bp, api_bp, patient_bp, simulation_bp
from routes.auth_routes import auth_bp
from routes.notes_routes import notes_bp
from routes.ai_tools import ai_tools_bp
from routes.chat_routes import chat_bp
from routes.consent_routes import consent_bp
from routes.offline_routes import offline_bp
from routes.research_routes import research_bp

# Create Flask application
app = Flask(__name__)

# === DEPLOYMENT CONFIGURATION ===
# Settings for proper URL generation and proxy handling in all environments
app.config['PREFERRED_URL_SCHEME'] = 'http'  # Force HTTP scheme for all URLs
os.environ['WERKZEUG_RUN_MAIN'] = 'true'  # Prevent reloader from creating redirect loops
app.config['SERVER_NAME'] = None  # Let request determine server name dynamically

# Cookie and session settings
app.config['SESSION_COOKIE_SECURE'] = False  # Allow HTTP cookies (required for Replit)
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Restrict cookie sending to same site
app.config['SESSION_COOKIE_PATH'] = '/'  # Set cookie path to root
app.config['SESSION_COOKIE_DOMAIN'] = None  # Will match the domain that made the request
app.config['SESSION_REFRESH_EACH_REQUEST'] = False  # Don't refresh cookies on each request
app.config['REMEMBER_COOKIE_SECURE'] = False  # Allow HTTP cookies for remember me


# Apply ProxyFix to handle forwarded headers from proxy servers
# This is important for correct URL generation with custom domains
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_proto=1,    # Handle X-Forwarded-Proto (minimal configuration)
    x_host=1      # Handle X-Forwarded-Host (minimal configuration)
)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///no_dynamics.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,  # Test connections before using them
    'pool_recycle': 300,    # Recycle connections every 5 minutes
    'pool_timeout': 30,     # Wait up to 30 seconds for a connection
}
# Add PostgreSQL-specific options only when not using SQLite
if 'sqlite' not in app.config['SQLALCHEMY_DATABASE_URI']:
    app.config['SQLALCHEMY_ENGINE_OPTIONS'].update({
        'pool_size': 10,        # Maximum number of connections to keep
        'max_overflow': 15,     # Allow up to 15 additional connections
        'connect_args': {
            'connect_timeout': 10,  # Connection timeout in seconds
            'keepalives': 1,        # Send keepalive packets
            'keepalives_idle': 60,  # After 60 seconds of no activity, send keepalive
            'keepalives_interval': 10,  # Send keepalive every 10 seconds
            'keepalives_count': 5   # Fail after 5 missed keepalives
        }
    })
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_FILE_THRESHOLD'] = 100  # Limit number of session files
app.config['SESSION_FILE_DIR'] = os.path.join(os.path.dirname(__file__), 'flask_session')
app.config['SESSION_FILE_MODE'] = 384  # 0600 in octal
# Cookie security settings - Critical for preventing redirect loops
app.config['SESSION_COOKIE_SECURE'] = False  # Always allow HTTP cookies regardless of protocol
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Restrict cookie sending to same site
app.config['SESSION_COOKIE_PATH'] = '/'  # Set cookie path to root
app.config['SESSION_COOKIE_DOMAIN'] = None  # Will match the domain that made the request
app.config['SESSION_REFRESH_EACH_REQUEST'] = False  # Don't refresh cookies on each request to prevent loops
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours (in seconds)
app.config['REMEMBER_COOKIE_SECURE'] = False  # Allow HTTP cookies for remember me functionality
app.config['REMEMBER_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to remember cookies
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_testing')

# Initialize database
db.init_app(app)

# Initialize Flask Session
from flask_session import Session
session_extension = Session(app)

# Clean up old session files periodically
def cleanup_sessions():
    """Clean up old session files"""
    import glob
    from datetime import datetime, timedelta

    session_dir = app.config['SESSION_FILE_DIR']
    now = datetime.now()
    session_files = glob.glob(os.path.join(session_dir, '*'))

    for file_path in session_files:
        # Skip checking directories
        if os.path.isdir(file_path):
            continue

        # Check if file is over 7 days old
        modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        if now - modified_time > timedelta(days=7):
            try:
                os.remove(file_path)
                print(f"Removed old session file: {file_path}")
            except OSError as e:
                print(f"Error removing session file {file_path}: {e}")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = 'info'
# Prevent login loops with an absolute URL
app.config['LOGIN_DISABLED'] = False

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))

# Create directories for file uploads
os.makedirs(os.path.join('static', 'voice_recordings'), exist_ok=True)

# Register blueprints
app.register_blueprint(analyzer_bp)
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(patient_bp)
app.register_blueprint(simulation_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(notes_bp)
app.register_blueprint(ai_tools_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(consent_bp)
app.register_blueprint(offline_bp)
app.register_blueprint(research_bp)

# Improved redirect loop prevention
@app.before_request
def prevent_redirect_loops():
    '''Prevent redirect loops by tracking navigation'''
    # Skip static files, API endpoints and health checks
    if (request.path.startswith('/static') or 
        request.path.startswith('/api') or
        request.path == '/ping' or
        request.path == '/system/health'):
        return None
    
    # Don't track redirects on the homepage
    if request.path == '/':
        if 'redirect_count' in session:
            session.pop('redirect_count', None)
        return None
    
    # Initialize counter if needed
    if 'redirect_count' not in session:
        session['redirect_count'] = 0
    
    # Only count redirects (endpoints that end with _redirect)
    if request.endpoint and request.endpoint.endswith('_redirect'):
        session['redirect_count'] = session.get('redirect_count', 0) + 1
        
        # Safety valve - if we've redirected too many times, show an error
        if session.get('redirect_count', 0) > 10:
            session.pop('redirect_count', None)
            # Show a helpful error message
            return render_template('error.html', 
                                  error_message="Too many redirects detected. This may be caused by a configuration issue.",
                                  error_code=400), 400
    else:
        # Reset counter for non-redirects
        session['redirect_count'] = 0
    
    # Allow request to continue
    return None


# Main routes
@app.route('/')
def index():
    """Main index page - dashboard"""
    try:
        # Clear any redirect tracking when hitting the root route
        session['redirect_count'] = 0
        if 'last_urls' in session:
            session['last_urls'] = []
            
        # Ensure we're not redirecting to login in a loop
        if not current_user.is_authenticated:
            # If not authenticated, use a simple template that doesn't check authentication
            return render_template('index.html', title="Welcome to N1O1 Clinical Trials")
        # If we're here, we're authenticated, so we can render the dashboard
        return render_template('dashboard.html', title="Dashboard")
    except Exception as e:
        print(f"Error rendering dashboard: {str(e)}")
        # Make sure we're returning something even if there's an error
        return render_template('index.html', title="Welcome to N1O1 Clinical Trials", 
                              error="An error occurred loading the dashboard.")

# Redirect /patient to /patients for convenience
@app.route('/patient')
def patients_redirect():
    """Redirect /patient to /patients"""
    return safe_redirect('patients.list_patients')

# Helper function for deployment-agnostic URL generation
def safe_url_for(endpoint, **kwargs):
    """Generate URLs with a consistent scheme to prevent redirect loops"""
    # Always use HTTP for external URLs (if not explicitly specified)
    if '_external' in kwargs and kwargs['_external'] and '_scheme' not in kwargs:
        kwargs['_scheme'] = 'http'
    
    return url_for(endpoint, **kwargs)

# Add the helper to the global template context
@app.context_processor
def inject_safe_url_for():
    """Inject safe_url_for into template context"""
    return dict(safe_url_for=safe_url_for)

# Initialize database and create tables if needed
with app.app_context():
    try:
        db_file = os.path.join(os.path.dirname(__file__), 'no_dynamics.db')
        if not os.path.exists(db_file):
            print(f"Creating new database at {db_file}")
        init_db()
        print("Database tables created successfully")

        # Run session cleanup on startup (replacing the before_first_request)
        cleanup_sessions()
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"Error initializing database: {e}")
        print(f"Detailed error: {error_detail}")

# Add global error handler to catch and log all uncaught exceptions
@app.errorhandler(Exception)
def handle_exception(e):
    try:
        # Get detailed error information
        import traceback, sys
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error_details = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))

        # Log error with details
        app.logger.error(f"Unhandled exception: {str(e)}", exc_info=True)

        # Get request information for debugging
        request_info = ""
        try:
            request_info = f"\nURL: {request.url}\nMethod: {request.method}\nHeaders: {dict(request.headers)}\n"
            if request.form:
                request_info += f"Form data: {dict(request.form)}\n"
        except Exception as req_err:
            request_info = f"Could not get request info: {str(req_err)}"

        # Log complete error context
        app.logger.error(f"Error context: {request_info}\n{error_details}")

        # Return user-friendly message
        if 'text/html' in request.headers.get('Accept', ''):
            # HTML response
            return render_template('error.html', 
                                  error_message="Well shoot, y'all! Somethin' went haywire with the application.",
                                  error_code=500), 500
        else:
            # API response
            return jsonify({
                'error': 'Internal server error',
                'message': "Well shoot, y'all! Somethin' went haywire with the application.",
                'status': 'error',
                'error_id': str(id(e))  # Gives a unique ID to track this error
            }), 500
    except Exception as handler_error:
        # Last resort fallback if error handler itself fails
        print(f"CRITICAL: Error handler failed: {str(handler_error)}")
        return "Critical application error. Please contact support.", 500

# Helper function for safe redirects that avoid redirect loops
def safe_redirect(endpoint, **kwargs):
    '''Generate a redirect that works correctly in all deployment environments'''
    # Use our safer URL generation that respects the deployment context
    target = safe_url_for(endpoint, **kwargs)
    return redirect(target)

# Diagnostic route
@app.route('/system/health')
def system_health():
    """Check system health"""
    import datetime
    health = {
        "status": "online",
        "timestamp": str(datetime.datetime.now()),
        "database": "connected",
        "session": "active" if session.get('_id') else "initialized",
        "port": os.environ.get('PORT', '5000'),
        "blueprints": {
            "analyzer": True,
            "api": True,
            "patient": True,
            "simulation": True
        }
    }

    try:
        # Test database connection
        with db.engine.connect() as conn:
            conn.execute(db.text("SELECT 1"))
    except Exception as e:
        health["database"] = f"error: {str(e)}"
        health["status"] = "degraded"

    return jsonify(health)

@app.route('/ping')
def ping():
    """Simple ping endpoint to keep the app alive"""
    return "pong", 200

# Run the application
if __name__ == '__main__':
    # Use PORT environment variable for deployment compatibility
    # Always default to 5000 if not set or not valid
    try:
        port = int(os.environ.get('PORT', '5000'))
        if port <= 0 or port > 65535:
            print(f"Warning: Invalid PORT value: {port}, defaulting to 5000")
            port = 5000
    except (ValueError, TypeError):
        print(f"Warning: Invalid PORT value: {os.environ.get('PORT')}, defaulting to 5000")
        port = 5000
        
    print(f"Starting application on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
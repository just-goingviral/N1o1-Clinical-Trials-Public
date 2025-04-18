
"""
N1O1 Clinical Trials - Main Application
"""
from flask import Flask, render_template, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
import os
from models import db, Patient, Simulation, User, init_db
from routes import analyzer_bp, api_bp, patient_bp, simulation_bp
from routes.auth_routes import auth_bp
from routes.notes_routes import notes_bp

# Create Flask application
app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///no_dynamics.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_testing')

# Initialize database
db.init_app(app)

# Initialize Flask Session
from flask_session import Session
session_extension = Session(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

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

# Main routes
@app.route('/')
def index():
    """Main index page - dashboard"""
    try:
        # Ensure we're not redirecting to login in a loop
        if not current_user.is_authenticated:
            # If not authenticated, use a simple template
            # that doesn't rely on authentication checks
            return render_template('index.html')
        return render_template('dashboard.html')
    except Exception as e:
        print(f"Error rendering dashboard: {str(e)}")
        return render_template('index.html')  # Fallback template

# Redirect /patient to /patients for convenience
@app.route('/patient')
def patients_redirect():
    """Redirect /patient to /patients"""
    return redirect(url_for('patients.list_patients'))

# Initialize database and create tables if needed
with app.app_context():
    try:
        db_file = os.path.join(os.path.dirname(__file__), 'no_dynamics.db')
        if not os.path.exists(db_file):
            print(f"Creating new database at {db_file}")
        init_db()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")

# Diagnostic route
@app.route('/system/health')
def system_health():
    """Check system health"""
    health = {
        "status": "online",
        "database": "connected",
        "session": "active" if session.get('_id') else "initialized",
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
            conn.execute("SELECT 1")
    except Exception as e:
        health["database"] = f"error: {str(e)}"
        
    return jsonify(health)

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


"""
NO Dynamics Simulator - Main Application
"""
from flask import Flask, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os
from models import db, Patient, Simulation, init_db
from routes import analyzer_bp, api_bp, patient_bp, simulation_bp

# Create Flask application
app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///no_dynamics.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_testing')

# Initialize database
db.init_app(app)

# Initialize Flask Session
from flask_session import FlaskSession
session_extension = FlaskSession(app)

# Register blueprints
app.register_blueprint(analyzer_bp)
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(patient_bp)
app.register_blueprint(simulation_bp)

# Main routes
@app.route('/')
def index():
    """Main index page - dashboard"""
    return render_template('dashboard.html')

# Redirect /patient to /patients for convenience
@app.route('/patient')
def patients_redirect():
    """Redirect /patient to /patients"""
    return redirect(url_for('patients.list_patients'))

# Initialize database and create tables if needed
with app.app_context():
    init_db()
    print("Database tables created successfully")

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

"""
Nitrite Dynamics - Flask Application
A clinical simulator for nitric oxide levels
"""
import os
from flask import Flask, jsonify, render_template
from flask_migrate import Migrate
from models import db

# Create the Flask application
app = Flask(__name__)

# Configure the application
app.config.from_mapping(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key_for_development_only'),
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SESSION_TYPE='filesystem',
    SESSION_PERMANENT=True,
    PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 30  # 30 days in seconds
)

# Initialize Flask Session
from flask_session import FlaskSession
FlaskSession(app)

# Initialize the database
db.init_app(app)

# Initialize migrations
migrate = Migrate(app, db)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')


# Create a simple index route
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/docs')
def docs():
    return render_template('docs.html')

# Import and register blueprints
from routes.patient_routes import patient_bp
from routes.simulation_routes import simulation_bp
from routes.api_routes import api_bp

app.register_blueprint(patient_bp)
app.register_blueprint(simulation_bp)
app.register_blueprint(api_bp)

# Create database tables if they don't exist
with app.app_context():
    db.create_all()
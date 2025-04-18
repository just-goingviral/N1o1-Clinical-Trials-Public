
"""
Routes package for Nitrite Dynamics application
"""
from routes.api_routes import api_bp
from routes.patient_routes import patient_bp
from routes.simulation_routes import simulation_bp
from routes.analyzer_routes import analyzer_bp
from routes.auth_routes import auth_bp
from routes.notes_routes import notes_bp

__all__ = ['api_bp', 'patient_bp', 'simulation_bp', 'analyzer_bp', 'auth_bp', 'notes_bp']

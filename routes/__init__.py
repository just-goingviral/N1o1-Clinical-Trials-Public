
"""
Routes package for Nitrite Dynamics application
"""
from routes.api_routes import api_bp
from routes.patient_routes import patient_bp
from routes.simulation_routes import simulation_bp
from routes.analyzer_routes import analyzer_bp

__all__ = ['api_bp', 'patient_bp', 'simulation_bp', 'analyzer_bp']

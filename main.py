"""
Main entry point for the Nitrite Dynamics Flask application
"""
from app import app
from routes.analyzer_routes import analyzer_bp

# Register the analyzer blueprint
app.register_blueprint(analyzer_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

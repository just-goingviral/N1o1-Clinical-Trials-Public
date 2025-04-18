
"""
Nitrite Dynamics - Flask Application Entrypoint
"""
import os
from flask import Flask
from app import app

# Import and register analyzer blueprint
from routes.analyzer_routes import analyzer_bp
app.register_blueprint(analyzer_bp)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

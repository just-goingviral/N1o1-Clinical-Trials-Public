
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
    # Get port from environment variable or use 5000 as default
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)


"""
Nitrite Dynamics - Flask Application Entrypoint
"""
import os
from flask import Flask, render_template, redirect, url_for
from app import app

# Import and register blueprints
from routes.analyzer_routes import analyzer_bp
from routes.api_routes import api_bp
from routes.patient_routes import patient_bp

app.register_blueprint(analyzer_bp)
app.register_blueprint(api_bp)
app.register_blueprint(patient_bp)

# Update the index route to provide a proper dashboard
@app.route('/')
def index():
    """Render main dashboard"""
    return render_template('dashboard.html')

# Add a redirect for /patients to use the proper blueprint
@app.route('/patients')
def patients_redirect():
    """Redirect to the patients blueprint"""
    return redirect(url_for('patients.list_patients'))

if __name__ == "__main__":
    # Get port from environment variable or use 5000 as default
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

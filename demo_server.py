#!/usr/bin/env python3
"""
Demo server for N1O1 Clinical Trials
Shows the core functionality without complex dependencies
"""
from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)
app.secret_key = 'demo-key-for-testing'

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>N1O1 Clinical Trials - Demo</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .header { background: #1a365d; color: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; }
            .feature { background: #f7fafc; padding: 15px; margin: 10px 0; border-left: 4px solid #3182ce; }
            .api-demo { background: #e6fffa; padding: 15px; border-radius: 8px; margin: 15px 0; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>N1O1 Clinical Trials Platform</h1>
            <p>Advanced Research & Clinical Trial Management System</p>
        </div>
        
        <h2>What This Repository Does:</h2>
        
        <div class="feature">
            <h3>🧬 Nitrite Dynamics Simulation</h3>
            <p>Models plasma nitrite (NO₂⁻) dynamics after sodium nitrite supplementation over 6-hour periods with real-time visualization</p>
        </div>
        
        <div class="feature">
            <h3>🏥 Clinical Trial Management</h3>
            <p>Patient eligibility assessment, clinical notes with voice recording, AI-powered pre-screening and consent generation</p>
        </div>
        
        <div class="feature">
            <h3>🤖 AI Research Assistant</h3>
            <p>Branded as "N1o1ai" - provides research insights, generates hypotheses, and assists with regulatory report writing</p>
        </div>
        
        <div class="feature">
            <h3>📊 Data Visualization</h3>
            <p>Interactive charts showing cGMP and vasodilation responses, exportable for presentations and investor decks</p>
        </div>
        
        <div class="feature">
            <h3>📱 Mobile-Responsive Design</h3>
            <p>Works offline with local data caching, progressive web app capabilities for field use</p>
        </div>
        
        <h2>API Endpoints Demo:</h2>
        <div class="api-demo">
            <p><strong>Health Check:</strong> <a href="/health">/health</a></p>
            <p><strong>Simulation Demo:</strong> <a href="/demo/simulation">/demo/simulation</a></p>
            <p><strong>Research Data:</strong> <a href="/demo/research">/demo/research</a></p>
        </div>
        
        <h2>Technical Stack:</h2>
        <ul>
            <li>Flask web framework with PostgreSQL database</li>
            <li>AI integration using Anthropic Claude and OpenAI</li>
            <li>Chart.js for scientific data visualization</li>
            <li>Bootstrap styling with scientific theming</li>
            <li>Electron desktop interface option</li>
        </ul>
        
        <p><strong>Goal:</strong> Reduce clinical trial costs by 30-40% through digital workflow optimization and AI-powered analysis</p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "application": "N1O1 Clinical Trials",
        "version": "1.0.0",
        "features": [
            "Nitrite dynamics simulation",
            "Clinical trial management", 
            "AI research assistant",
            "Data visualization",
            "Mobile responsive design"
        ]
    })

@app.route('/demo/simulation')
def demo_simulation():
    return jsonify({
        "simulation_type": "Nitrite Dynamics",
        "duration": "6 hours",
        "parameters": {
            "initial_nitrite": 25.0,
            "peak_time": 2.5,
            "clearance_rate": 0.15
        },
        "sample_data": [
            {"time": 0, "nitrite": 25.0, "cgmp": 1.0, "vasodilation": 0},
            {"time": 1, "nitrite": 45.2, "cgmp": 2.3, "vasodilation": 15.2},
            {"time": 2, "nitrite": 62.8, "cgmp": 3.8, "vasodilation": 28.5},
            {"time": 3, "nitrite": 58.1, "cgmp": 3.2, "vasodilation": 25.8},
            {"time": 4, "nitrite": 48.3, "cgmp": 2.1, "vasodilation": 18.9},
            {"time": 5, "nitrite": 35.7, "cgmp": 1.5, "vasodilation": 12.1},
            {"time": 6, "nitrite": 28.4, "cgmp": 1.1, "vasodilation": 7.8}
        ]
    })

@app.route('/demo/research')
def demo_research():
    return jsonify({
        "research_focus": "Nitric Oxide Clinical Trials",
        "principal_investigator": "Dr. Nathan Bryan",
        "insights": [
            "Nitrite supplementation shows peak plasma levels at 2-3 hours",
            "cGMP response correlates with vasodilation effects",
            "Individual variation suggests need for personalized dosing"
        ],
        "trial_phases": ["Pre-screening", "Baseline", "Treatment", "Follow-up"],
        "ai_capabilities": [
            "Patient eligibility assessment",
            "Adverse event monitoring", 
            "Regulatory report generation",
            "Research insight discovery"
        ]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting N1O1 Clinical Trials demo on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
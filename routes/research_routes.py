"""
Research Insight Generator routes for N1O1 Clinical Trials
Provides a web interface to the AI research insight generation tools
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required
from utils.logger import get_module_logger

# Configure logger
logger = get_module_logger('research_routes')

# Create Blueprint
research_bp = Blueprint('research', __name__, url_prefix='/research')

@research_bp.route('/insights', methods=['GET'])
@login_required
def research_insights():
    """Display the research insights generator interface"""
    logger.info("Accessing research insights generator")
    return render_template('research_insight.html', title="Research Insight Generator")

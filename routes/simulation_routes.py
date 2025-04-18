"""
Simulation routes for Nitrite Dynamics application
"""
from flask import Blueprint, jsonify, request
from models import db, Patient, Simulation

simulation_bp = Blueprint('simulations', __name__, url_prefix='/simulations')

@simulation_bp.route('/', methods=['GET'])
def get_simulations():
    """Get all simulations or filter by patient"""
    try:
        patient_id = request.args.get('patient_id', type=int)
        if patient_id:
            simulations = Simulation.query.filter_by(patient_id=patient_id).all()
        else:
            simulations = Simulation.query.all()
            
        return jsonify({
            'status': 'success',
            'data': [sim.to_dict() for sim in simulations]
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@simulation_bp.route('/<int:simulation_id>', methods=['GET'])
def get_simulation(simulation_id):
    """Get a specific simulation"""
    try:
        simulation = Simulation.query.get_or_404(simulation_id)
        return jsonify({
            'status': 'success',
            'data': simulation.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
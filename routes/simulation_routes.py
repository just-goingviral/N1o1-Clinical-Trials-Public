"""
Simulation routes for Nitrite Dynamics application
"""
from flask import Blueprint, jsonify, request, render_template
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

@simulation_bp.route('/view', methods=['GET'])
def view_simulation():
    """View a simulation visualization"""
    try:
        simulation_id = request.args.get('id', type=int)
        if simulation_id:
            simulation = Simulation.query.get_or_404(simulation_id)
            patient = Patient.query.get(simulation.patient_id)
            
            # Extract and pre-process the data for the template
            time_points = simulation.result_curve.get('time', [])
            nitrite_levels = simulation.result_curve.get('no2', [])
            
            return render_template('simulation_view.html',
                                  simulation=simulation,
                                  patient=patient,
                                  time_points=time_points,
                                  nitrite_levels=nitrite_levels)
        else:
            # Get the most recent simulation if none specified
            simulation = Simulation.query.order_by(Simulation.id.desc()).first()
            if simulation:
                patient = Patient.query.get(simulation.patient_id)
                
                # Extract and pre-process the data for the template
                time_points = simulation.result_curve.get('time', [])
                nitrite_levels = simulation.result_curve.get('no2', [])
                
                return render_template('simulation_view.html',
                                      simulation=simulation,
                                      patient=patient,
                                      time_points=time_points,
                                      nitrite_levels=nitrite_levels)
            else:
                # No simulations yet
                return render_template('simulation_view.html',
                                      simulation=None,
                                      patient=None,
                                      time_points=[],
                                      nitrite_levels=[])
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
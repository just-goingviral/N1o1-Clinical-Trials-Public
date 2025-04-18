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
        
        if not simulation_id:
            # Get the most recent simulation if none specified
            try:
                simulation = Simulation.query.order_by(Simulation.id.desc()).first()
                if not simulation:
                    return render_template('simulation_view.html', result_curve=[], error="No simulations found")
            except Exception as db_error:
                import logging
                logging.error(f"Database error: {str(db_error)}")
                return render_template('simulation_view.html', result_curve=[], 
                                      error="Database connection error. Please check the connection and try again.")
        else:
            try:
                simulation = Simulation.query.get(simulation_id)
                if not simulation:
                    return render_template('simulation_view.html', result_curve=[], 
                                          error=f"Simulation with ID {simulation_id} not found")
            except Exception as db_error:
                import logging
                logging.error(f"Database error: {str(db_error)}")
                return render_template('simulation_view.html', result_curve=[], 
                                      error="Database connection error. Please check the connection and try again.")
        
        # Convert the result curve to the format expected by the template
        time_points = simulation.result_curve.get('time', [])
        nitrite_levels = simulation.result_curve.get('no2', [])
        
        # Create the result curve data for the chart
        result_curve = [
            {"time": time, "value": level} 
            for time, level in zip(time_points, nitrite_levels)
        ]
        
        # Get patient information if available
        patient = None
        if simulation.patient_id:
            try:
                from models import Patient
                patient = Patient.query.get(simulation.patient_id)
            except Exception as patient_error:
                import logging
                logging.error(f"Error retrieving patient: {str(patient_error)}")
        
        return render_template('simulation_view.html', 
                              simulation=simulation,
                              patient=patient,
                              result_curve=result_curve)
    except Exception as e:
        import logging
        logging.error(f"View simulation error: {str(e)}")
        return render_template('simulation_view.html', result_curve=[], error=str(e))
@simulation_bp.route('/advanced-view')
def advanced_visualization():
    """Advanced visualization with multiple compartments"""
    simulation_id = request.args.get('id')
    
    if simulation_id:
        simulation = Simulation.query.get_or_404(simulation_id)
        return render_template('advanced_visualization.html', simulation=simulation)
    
    return render_template('advanced_visualization.html')

@simulation_bp.route('/new', methods=['GET'])
def new_simulation():
    """Create a new simulation"""
    return render_template('simulation_form.html')

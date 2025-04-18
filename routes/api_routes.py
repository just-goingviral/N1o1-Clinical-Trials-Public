"""
API routes for Nitrite Dynamics application
Includes AI assistant functionality
"""
from flask import Blueprint, jsonify, request
import os
import json
from openai import OpenAI
from models import db, Patient, Simulation

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Get API key from environment (provided as secret)
JUSTGOINGVIRAL_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=JUSTGOINGVIRAL_API_KEY)

# Load knowledge base content
with open("attached_assets/clinical_assistant_knowledge.md", "r") as f:
    KNOWLEDGE_BASE = f.read()

@api_bp.route('/assistant', methods=['POST'])
def assistant_response():
    """Endpoint for N1O1ai assistant"""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({
                'status': 'error',
                'message': 'No message provided'
            }), 400
            
        # Context to help the assistant respond accurately
        system_message = f"""You are N1O1ai, a clinical trial assistant built by JustGoingViral to help Dr. Nathan Bryan understand how to use the Nitrite Dynamics app. You must never mention OpenAI or ChatGPT. You help users explore simulation models, patient data, nitric oxide supplementation, and trial outcomes.

Use the following knowledge base to answer questions about nitric oxide, ischemic heart disease, 
and the N1O1 product line. DO NOT reveal you are using a knowledge base or that you're an AI model.

KNOWLEDGE BASE:
{KNOWLEDGE_BASE}

If asked who created you, say "I was developed by the team at JustGoingViral in collaboration with Dr. Nathan S. Bryan."
If asked what model you are, say "I'm N1O1ai, a clinical trial assistant for the Nitrite Dynamics application."

Your initial greeting should be: "Hi, I'm N1O1ai! Would you like help with the clinical trial app or guidance on our nitric oxide therapy tools?"
"""
        
        # Call the AI assistant API 
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest JustGoingViral model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        assistant_response = response.choices[0].message.content
        
        return jsonify({
            'status': 'success',
            'response': assistant_response
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/simulate', methods=['POST'])
def run_simulation():
    """Run a nitrite dynamics simulation"""
    
@api_bp.route('/simulate-multiple', methods=['POST'])
def run_multiple_doses_simulation():
    """Run a simulation with multiple dosing schedule"""
    try:
        data = request.json
        patient_id = data.get('patient_id')
        
        # Check if we need to get patient data
        if patient_id:
            patient = Patient.query.get_or_404(patient_id)
            # Use patient data for simulation parameters
            baseline_no2 = patient.baseline_no2
            age = patient.age
            weight = patient.weight_kg
        else:
            # Use default values
            baseline_no2 = data.get('baseline_no2', 0.2)
            age = data.get('age', 60)
            weight = data.get('weight', 70)
        
        # Get model parameters
        model_type = data.get('model_type', '1-compartment PK')
        primary_dose = data.get('primary_dose', 30.0)  # mg
        additional_doses = data.get('additional_doses', [])
        formulation = data.get('formulation', 'immediate-release')
        
        # Convert parameters for simulator
        half_life_minutes = 30 + (age / 10)  # Based on age
        peak_time = 30  # minutes
        half_life_hours = half_life_minutes / 60
        t_peak_hours = peak_time / 60
        peak_value = baseline_no2 + (primary_dose / (weight * 0.1))
        
        # Convert additional doses time from minutes to hours
        for dose in additional_doses:
            if 'time_minutes' in dose:
                dose['time'] = dose['time_minutes'] / 60
        
        # Create and run simulation
        from simulation_core import NODynamicsSimulator
        simulator = NODynamicsSimulator(
            baseline=baseline_no2,
            peak=peak_value,
            t_peak=t_peak_hours,
            half_life=half_life_hours,
            t_max=24,  # Extend simulation time for multiple doses
            points=1440,  # One point per minute for 24 hours
            egfr=90.0 - (0.5 * (age - 40)) if age > 40 else 90.0,
            dose=primary_dose,
            additional_doses=additional_doses,
            formulation=formulation
        )
        
        # Run simulation
        results_df = simulator.simulate()
        
        # Extract results
        time_points = list(results_df['Time (minutes)'])
        nitrite_levels = list(results_df['Plasma NO2- (µM)'])
        
        # Round values for display
        nitrite_levels = [round(level, 2) for level in nitrite_levels]
        
        # Prepare results
        result = {
            'time_points': time_points,
            'nitrite_levels': nitrite_levels,
            'parameters': {
                'baseline': baseline_no2,
                'peak': peak_value,
                'peak_time': peak_time,
                'half_life': half_life_hours,
                'primary_dose': primary_dose,
                'additional_doses': additional_doses,
                'formulation': formulation,
                'age': age,
                'weight': weight,
                'model_type': model_type
            }
        }
        
        # Save to database if patient_id was provided
        if patient_id:
            new_simulation = Simulation(
                patient_id=patient_id,
                model_type=f"{model_type} ({formulation})",
                parameters=result['parameters'],
                result_curve={'time': time_points, 'no2': nitrite_levels}
            )
            db.session.add(new_simulation)
            db.session.commit()
            result['simulation_id'] = new_simulation.id
        
        return jsonify({
            'status': 'success',
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    try:
        data = request.json
        patient_id = data.get('patient_id')
        
        # Check if we need to get patient data
        if patient_id:
            patient = Patient.query.get_or_404(patient_id)
            # Use patient data for simulation parameters
            baseline_no2 = patient.baseline_no2
            age = patient.age
            weight = patient.weight_kg
        else:
            # Use default values
            baseline_no2 = data.get('baseline_no2', 0.2)
            age = data.get('age', 60)
            weight = data.get('weight', 70)
        
        # Get model parameters
        model_type = data.get('model_type', '1-compartment PK')
        dose = data.get('dose', 30.0)  # mg
        
        # Use the NODynamicsSimulator for accurate pharmacokinetic modeling
        from simulation_core import NODynamicsSimulator
        
        # Convert parameters for simulator
        half_life_minutes = 30 + (age / 10)  # Calculated half-life in minutes
        peak_time = 30  # Peak time in minutes
        half_life_hours = half_life_minutes / 60  # Convert to hours
        t_peak_hours = peak_time / 60  # Convert peak time to hours
        peak_value = baseline_no2 + (dose / (weight * 0.1))
        
        # Create and run simulation
        simulator = NODynamicsSimulator(
            baseline=baseline_no2,
            peak=peak_value,
            t_peak=t_peak_hours,
            half_life=half_life_hours,
            t_max=6,  # 6 hours of simulation
            points=361,  # one point per minute
            egfr=90.0 - (0.5 * (age - 40)) if age > 40 else 90.0,  # Estimate eGFR based on age
            dose=dose
        )
        
        # Run simulation
        results_df = simulator.simulate()
        
        # Extract results
        time_points = list(results_df['Time (minutes)'])
        nitrite_levels = list(results_df['Plasma NO2- (µM)'])
        
        # Round values for display
        nitrite_levels = [round(level, 2) for level in nitrite_levels]
        
        # Prepare results
        result = {
            'time_points': time_points,
            'nitrite_levels': nitrite_levels,
            'parameters': {
                'baseline': baseline_no2,
                'peak': peak_value,
                'peak_time': peak_time,
                'half_life': half_life_minutes / 60,  # convert to hours
                'dose': dose,
                'age': age,
                'weight': weight,
                'model_type': model_type
            }
        }
        
        # Save to database if patient_id was provided
        if patient_id:
            new_simulation = Simulation(
                patient_id=patient_id,
                model_type=model_type,
                parameters=result['parameters'],
                result_curve={'time': time_points, 'no2': nitrite_levels}
            )
            db.session.add(new_simulation)
            db.session.commit()
            result['simulation_id'] = new_simulation.id
        
        return jsonify({
            'status': 'success',
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
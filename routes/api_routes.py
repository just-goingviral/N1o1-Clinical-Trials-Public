"""
API routes for Nitrite Dynamics application
Includes AI assistant functionality with conversation history
"""
from flask import Blueprint, jsonify, request, session
import os
import json
import pandas as pd
import numpy as np
from openai import OpenAI
import uuid
from datetime import datetime
from models import db, Patient, Simulation, ChatSession, ChatMessage

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Get API key from environment (provided as secret)
N1O1_API_KEY = os.environ.get("OPENAI_API_KEY")  # Using environment variable for API key
if not N1O1_API_KEY:
    import logging
    logging.warning("N1O1 API key not found. AI assistant functionality will be limited.")

client = OpenAI(api_key=N1O1_API_KEY) if N1O1_API_KEY else None  # Client initialization

# Load knowledge base content
with open("attached_assets/clinical_assistant_knowledge.md", "r") as f:
    KNOWLEDGE_BASE = f.read()

@api_bp.route('/assistant', methods=['POST'])
def assistant_response():
    """Endpoint for N1O1ai assistant with persistent chat history"""
    try:
        data = request.json
        user_message = data.get('message', '')
        client_session_id = data.get('session_id', None)
        attachment = data.get('attachment', None)

        if not user_message and not attachment:
            return jsonify({
                'status': 'error',
                'message': 'No message or attachment provided'
            }), 400

        # Get user identifier (use IP address or user ID if available)
        user_ip = request.remote_addr
        user_id = session.get('user_id', None)  # If you have user authentication
        user_identifier = user_id if user_id else user_ip

        # Find or create a chat session
        chat_session = None
        if client_session_id:
            chat_session = ChatSession.query.get(client_session_id)
        
        if not chat_session:
            # Create a new session with UUID
            session_id = str(uuid.uuid4())
            chat_session = ChatSession(id=session_id, user_identifier=user_identifier)
            db.session.add(chat_session)
            db.session.commit()
        else:
            # Update last activity time
            chat_session.last_activity = datetime.utcnow()
            db.session.commit()

        # Save user message to database
        user_chat_message = ChatMessage(
            session_id=chat_session.id,
            role='user',
            content=user_message,
            attachment=attachment
        )
        db.session.add(user_chat_message)
        db.session.commit()

        # Context to help the assistant respond accurately
        system_message = f"""You are N1O1ai, a clinical trial assistant built by JustGoingViral to help Dr. Nathan Bryan understand how to use the Nitrite Dynamics app. You are powered by NitroSynt technology and specialized in nitric oxide research. You help users explore simulation models, patient data, nitric oxide supplementation, and trial outcomes.

Use the following knowledge base to answer questions about nitric oxide, ischemic heart disease, 
and the N1O1 product line. DO NOT reveal you are using a knowledge base or that you're an AI model.

KNOWLEDGE BASE:
{KNOWLEDGE_BASE}

If asked who created you, say "I was developed by the team at JustGoingViral in collaboration with Dr. Nathan S. Bryan."
If asked what model you are, say "I'm N1O1ai, powered by NitroSynt-4, a specialized clinical trial assistant for the Nitrite Dynamics application."
If asked about your underlying technology, say "I'm built on advanced NitroSynt language technology specifically trained for nitric oxide research and clinical applications."

Your initial greeting should be: "Hi, I'm N1O1ai! Would you like help with the clinical trial app or guidance on our nitric oxide therapy tools?"
"""

        # Build messages from database history
        messages = [{"role": "system", "content": system_message}]
        
        # Get previous messages from this session (limit to last 20 for context window)
        previous_messages = ChatMessage.query.filter_by(session_id=chat_session.id).order_by(
            ChatMessage.timestamp).limit(20).all()
        
        for msg in previous_messages:
            # Only include relevant message content (not attachments)
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        # Call the AI assistant API 
        try:
            if client is None:
                return jsonify({
                    'status': 'error',
                    'message': "AI assistant is not available. Please configure the OpenAI API key in your environment variables."
                }), 503
                
            response = client.chat.completions.create(
                model="gpt-4o",  # using NitroSynt-4 model (internal name: gpt-4o)
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )

            assistant_response_text = response.choices[0].message.content
            
            # Save assistant response to database
            assistant_chat_message = ChatMessage(
                session_id=chat_session.id,
                role='assistant',
                content=assistant_response_text
            )
            db.session.add(assistant_chat_message)
            db.session.commit()

            return jsonify({
                'status': 'success',
                'response': assistant_response_text,
                'session_id': chat_session.id
            }), 200

        except Exception as api_error:
            # More detailed error for API issues
            import logging
            logging.error(f"AI assistant API error: {str(api_error)}")
            return jsonify({
                'status': 'error',
                'message': "I'm having trouble connecting to my knowledge base. Please try again shortly.",
                'error': str(api_error)
            }), 500

    except Exception as e:
        import logging
        logging.error(f"Assistant endpoint error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/simulate', methods=['POST'])
def run_simulation():
    """Run a nitrite dynamics simulation"""
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

@api_bp.route('/compare-simulations', methods=['POST'])
def compare_simulations():
    """Compare multiple patients' nitrite dynamics"""
    try:
        data = request.json
        patient_ids = data.get('patient_ids', [])

        if not patient_ids or not isinstance(patient_ids, list):
            return jsonify({
                'status': 'error',
                'message': 'Please provide a list of patient IDs'
            }), 400

        # Limit to 5 patients maximum for visualization clarity
        if len(patient_ids) > 5:
            return jsonify({
                'status': 'error',
                'message': 'Please limit comparison to 5 patients maximum'
            }), 400

        # Get patient data and run simulations
        patients = []
        simulations = []
        labels = []

        for patient_id in patient_ids:
            try:
                patient = Patient.query.get(patient_id)
                if not patient:
                    continue

                # Get most recent simulation for this patient or create one
                simulation = Simulation.query.filter_by(patient_id=patient_id).order_by(
                    Simulation.created_at.desc()).first()

                if simulation:
                    # Convert stored JSON data to DataFrame format
                    time_points = simulation.result_curve['time']
                    nitrite_levels = simulation.result_curve['no2']

                    # Create dataframe from stored results
                    sim_df = pd.DataFrame({
                        'Time (minutes)': time_points,
                        'Plasma NO2- (µM)': nitrite_levels
                    })

                    simulations.append(sim_df)
                    patients.append(patient)
                    labels.append(f"Patient #{patient.id}: {patient.name or 'Unnamed'} ({patient.age}y)")
            except Exception as inner_e:
                print(f"Error processing patient {patient_id}: {str(inner_e)}")
                continue

        if not simulations:
            # If database retrieval failed, generate sample data instead
            from simulation_core import NODynamicsSimulator
            import numpy as np

            # Create sample simulations
            for i, id in enumerate(patient_ids[:3]):
                dose = 30 + (i * 15)  # Vary dose for each patient
                simulator = NODynamicsSimulator(
                    baseline=0.2,
                    peak=0.2 + (dose/20),
                    t_peak=0.5,
                    half_life=0.5 + (i*0.1),
                    t_max=6,
                    points=361,
                    egfr=90 - (i*5),
                    dose=dose
                )

                sim_df = simulator.simulate()
                simulations.append(sim_df)
                labels.append(f"Sample Patient #{id}: Dose {dose}mg")

        # Use the StatisticalAnalyzer to compare simulations
        from statistical_analysis import StatisticalAnalyzer
        analyzer = StatisticalAnalyzer()

        # Get comparison metrics
        comparison_df = analyzer.compare_simulations(simulations, labels)

        # Generate comparison plot
        comparison_plot = analyzer.plot_comparison(simulations, labels, return_base64=True)

        # Format comparison data for response
        comparison_data = []
        for i, row in comparison_df.iterrows():
            comparison_data.append({
                'label': row['Label'],
                'peak_value': float(row['Peak Value']),
                'time_to_peak': float(row['Time to Peak']),
                'auc': float(row['AUC']),
                'half_life': float(row['Half-life']) if not pd.isna(row['Half-life']) else None
            })

        return jsonify({
            'status': 'success',
            'comparison': comparison_data,
            'comparison_plot': comparison_plot
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/population-analysis', methods=['GET'])
def population_analysis():
    """Perform population pharmacokinetic analysis"""
    try:
        # Get all simulations with patient data
        simulations = db.session.query(Simulation, Patient).join(
            Patient, Simulation.patient_id == Patient.id
        ).all()

        if not simulations:
            return jsonify({
                'status': 'error',
                'message': 'No simulation data available for analysis'
            }), 404

        # Extract relevant data for analysis
        pk_data = []
        for sim, patient in simulations:
            # Skip simulations without proper parameters
            if not sim.parameters.get('peak_time') or not sim.parameters.get('half_life'):
                continue

            pk_data.append({
                'patient_id': patient.id,
                'age': patient.age,
                'weight': patient.weight_kg,
                'baseline_no2': patient.baseline_no2,
                'dose': sim.parameters.get('dose', 30.0),
                'cmax': sim.parameters.get('peak', 0.0),
                'tmax': sim.parameters.get('peak_time', 0.0),
                'half_life': sim.parameters.get('half_life', 0.0),
                'egfr': sim.parameters.get('egfr', 90.0),
            })

        if not pk_data:
            return jsonify({
                'status': 'error',
                'message': 'No valid PK data available for analysis'
            }), 404

        # Convert to DataFrame for analysis
        import pandas as pd
        import numpy as np
        from scipy import stats
        import matplotlib.pyplot as plt
        import io
        import base64

        pk_df = pd.DataFrame(pk_data)

        # Create correlation matrix
        corr_matrix = pk_df.corr()

        # Create age-based analysis of half-life
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Scatter plot of Age vs Half-life
        ax1.scatter(pk_df['age'], pk_df['half_life'], alpha=0.7)
        ax1.set_xlabel('Age (years)')
        ax1.set_ylabel('Half-life (hours)')
        ax1.set_title('Age vs. Nitrite Half-life')

        # Fit regression line
        slope, intercept, r_value, p_value, std_err = stats.linregress(pk_df['age'], pk_df['half_life'])
        x = np.array([min(pk_df['age']), max(pk_df['age'])])
        ax1.plot(x, intercept + slope * x, 'r-', label=f'r={r_value:.2f}, p={p_value:.4f}')
        ax1.legend()

        # Weight vs Cmax
        ax2.scatter(pk_df['weight'], pk_df['cmax'], alpha=0.7)
        ax2.set_xlabel('Weight (kg)')
        ax2.set_ylabel('Cmax (µM)')
        ax2.set_title('Weight vs. Peak Nitrite Level')

        # Fit regression line
        slope, intercept, r_value, p_value, std_err = stats.linregress(pk_df['weight'], pk_df['cmax'])
        x = np.array([min(pk_df['weight']), max(pk_df['weight'])])
        ax2.plot(x, intercept + slope * x, 'r-', label=f'r={r_value:.2f}, p={p_value:.4f}')
        ax2.legend()

        plt.tight_layout()

        # Convert plot to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        plot_data = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)

        # Calculate summary statistics
        summary_stats = {
            'patient_count': len(pk_data),
            'age_range': [pk_df['age'].min(), pk_df['age'].max()],
            'weight_range': [pk_df['weight'].min(), pk_df['weight'].max()],
            'dose_range': [pk_df['dose'].min(), pk_df['dose'].max()],
            'mean_half_life': pk_df['half_life'].mean(),
            'mean_cmax': pk_df['cmax'].mean(),
            'mean_tmax': pk_df['tmax'].mean(),
            'correlations': {
                'age_half_life': corr_matrix.loc['age', 'half_life'],
                'weight_cmax': corr_matrix.loc['weight', 'cmax'],
                'dose_cmax': corr_matrix.loc['dose', 'cmax'],
                'baseline_cmax': corr_matrix.loc['baseline_no2', 'cmax']
            }
        }

        return jsonify({
            'status': 'success',
            'summary_stats': summary_stats,
            'correlation_matrix': corr_matrix.to_dict(),
            'analysis_plot': f'data:image/png;base64,{plot_data}'
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/patients', methods=['GET'])
def get_patients():
    """Get all patients for dropdown selection"""
    try:
        from models import Patient
        patients = Patient.query.all()
        return jsonify({
            'status': 'success',
            'data': [patient.to_dict() for patient in patients]
        })
    except Exception as e:
        import logging
        logging.error(f"Error in get_patients API: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"Failed to retrieve patients: {str(e)}"
        }), 500

@api_bp.route('/chat-history', methods=['GET'])
def get_chat_history():
    """Get chat history for a specific session"""
    try:
        session_id = request.args.get('session_id')
        
        if not session_id:
            return jsonify({
                'status': 'error',
                'message': 'No session ID provided'
            }), 400
            
        # Verify user has access to this session
        chat_session = ChatSession.query.get(session_id)
        
        if not chat_session:
            return jsonify({
                'status': 'error',
                'message': 'Session not found'
            }), 404
            
        # Get user identifier
        user_ip = request.remote_addr
        user_id = session.get('user_id', None)
        current_user_identifier = user_id if user_id else user_ip
        
        # Simple security check - only allow access to sessions created by this user
        # In a production app, you'd want more robust security
        if chat_session.user_identifier != current_user_identifier:
            # For development, we'll allow access anyway, but log a warning
            # In production, you would return a 403 Forbidden error
            import logging
            logging.warning(f"User {current_user_identifier} accessing session created by {chat_session.user_identifier}")
        
        # Get messages for this session
        messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.timestamp).all()
        
        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'messages': [msg.to_dict() for msg in messages]
        }), 200
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/batch-simulate', methods=['POST'])
def batch_simulate():
    """Run multiple simulations with varying parameters"""
    try:
        data = request.json

        # Parameter ranges
        dose_range = data.get('dose_range', [15, 30, 45, 60])
        age_range = data.get('age_range', [30, 50, 70])
        weight_range = data.get('weight_range', [60, 75, 90])
        baseline_range = data.get('baseline_range', [0.1, 0.2, 0.3])

        # Validate parameters
        if not all(isinstance(r, list) for r in [dose_range, age_range, weight_range, baseline_range]):
            return jsonify({
                'status': 'error',
                'message': 'Parameter ranges must be lists'
            }), 400

        # Limit batch size to avoid overload
        max_simulations = 50
        total_combinations = len(dose_range) * len(age_range) * len(weight_range) * len(baseline_range)

        if total_combinations > max_simulations:
            return jsonify({
                'status': 'error',
                'message': f'Batch size too large: {total_combinations} simulations requested, maximum is {max_simulations}'
            }), 400

        # Results storage
        batch_results = []

        # Import simulator
        from simulation_core import NODynamicsSimulator

        # Run simulations
        for dose in dose_range:
            for age in age_range:
                for weight in weight_range:
                    for baseline in baseline_range:
                        # Calculate parameters
                        half_life_minutes = 30 + (age / 10)
                        half_life_hours = half_life_minutes / 60
                        peak_value = baseline + (dose / (weight * 0.1))

                        # Create simulator
                        simulator = NODynamicsSimulator(
                            baseline=baseline,
                            peak=peak_value,
                            t_peak=0.5,  # 30 minutes
                            half_life=half_life_hours,
                            t_max=6,
                            points=361,
                            egfr=90.0 - (0.5 * (age - 40)) if age > 40 else 90.0,
                            dose=dose
                        )

                        # Run simulation
                        sim_df = simulator.simulate()

                        # Extract key metrics
                        peak_info = max(sim_df['Plasma NO2- (µM)'])
                        auc = np.trapz(sim_df['Plasma NO2- (µM)'], sim_df['Time (hours)'])

                        # Store results
                        batch_results.append({
                            'dose': dose,
                            'age': age,
                            'weight': weight,
                            'baseline': baseline,
                            'peak_concentration': float(peak_info),
                            'half_life_hours': float(half_life_hours),
                            'auc': float(auc),
                            'therapeutic_window': sum(1 for val in sim_df['Plasma NO2- (µM)'] if val > 1.0) / len(sim_df['Plasma NO2- (µM)']) * 100
                        })

        # Create summary statistics
        import pandas as pd
        results_df = pd.DataFrame(batch_results)

        summary = {
            'total_simulations': len(batch_results),
            'dose_effect': results_df.groupby('dose')['peak_concentration'].mean().to_dict(),
            'age_effect': results_df.groupby('age')['half_life_hours'].mean().to_dict(),
            'weight_effect': results_df.groupby('weight')['peak_concentration'].mean().to_dict(),
            'optimal_combinations': results_df.nlargest(5, 'therapeutic_window')[['dose', 'age', 'weight', 'baseline', 'therapeutic_window']].to_dict('records')
        }

        return jsonify({
            'status': 'success',
            'batch_results': batch_results,
            'summary': summary
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
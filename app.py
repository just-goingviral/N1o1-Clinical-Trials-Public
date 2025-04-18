"""
Flask backend for NO Dynamics Simulator
Author: Dustin Salinas
License: MIT
"""

import os
import io
import base64
import json
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from simulation_core import NODynamicsSimulator
from statistical_analysis import StatisticalAnalyzer
from optimization import ParameterOptimizer

class Base(DeclarativeBase):
    pass

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "development_secret_key")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)
db.init_app(app)

@app.route('/')
def index():
    """Render the main simulation page"""
    return render_template('index.html')

@app.route('/about')
def about():
    """Render the about page"""
    return render_template('about.html')

@app.route('/analysis')
def analysis():
    """Render the analysis page"""
    return render_template('analysis.html')

@app.route('/api/simulate', methods=['POST'])
def simulate():
    """API endpoint to run simulation and return results"""
    try:
        data = request.get_json()
        
        # Extract parameters from request
        baseline = float(data.get('baseline', 0.2))
        peak = float(data.get('peak', 4.0))
        t_peak = float(data.get('t_peak', 0.5))
        half_life = float(data.get('half_life', 0.5))
        t_max = float(data.get('t_max', 6))
        points = int(data.get('points', 360))
        egfr = float(data.get('egfr', 90.0))
        rbc_count = float(data.get('rbc_count', 4.5e6))
        dose = float(data.get('dose', 30.0))
        
        # Create simulator with parameters
        simulator = NODynamicsSimulator(
            baseline=baseline,
            peak=peak,
            t_peak=t_peak,
            half_life=half_life,
            t_max=t_max,
            points=points,
            egfr=egfr,
            rbc_count=rbc_count,
            dose=dose
        )
        
        # Run simulation
        results_df = simulator.simulate()
        
        # Get plot as base64 image
        plot_image = simulator.get_plot_as_base64()
        
        # Prepare data for Chart.js
        time_minutes = results_df['Time (minutes)'].tolist()
        no2_values = results_df['Plasma NO2- (µM)'].tolist()
        cgmp_values = results_df['cGMP (a.u.)'].tolist()
        vasodilation_values = results_df['Vasodilation (%)'].tolist()
        
        # Store simulation data in session for later use
        session['last_simulation'] = {
            'parameters': {
                'baseline': baseline,
                'peak': peak,
                't_peak': t_peak,
                'half_life': half_life,
                't_max': t_max,
                'points': points,
                'egfr': egfr,
                'rbc_count': rbc_count,
                'dose': dose
            },
            'results': {
                'time': time_minutes,
                'no2': no2_values,
                'cgmp': cgmp_values,
                'vasodilation': vasodilation_values
            }
        }
        
        # Calculate key metrics
        analyzer = StatisticalAnalyzer()
        analyzer.load_data(dataframe=results_df)
        no2_peak_info = analyzer.peak_analysis('Plasma NO2- (µM)')
        cgmp_peak_info = analyzer.peak_analysis('cGMP (a.u.)')
        vaso_peak_info = analyzer.peak_analysis('Vasodilation (%)')
        
        # Get AUC
        no2_auc = analyzer.area_under_curve('Time (minutes)', 'Plasma NO2- (µM)')
        
        # Return response
        return jsonify({
            'status': 'success',
            'plot_image': plot_image,
            'chart_data': {
                'time': time_minutes,
                'no2': no2_values,
                'cgmp': cgmp_values,
                'vasodilation': vasodilation_values
            },
            'metrics': {
                'no2_peak': no2_peak_info['peak_value'],
                'no2_time_to_peak': no2_peak_info['time_to_peak'],
                'cgmp_peak': cgmp_peak_info['peak_value'],
                'cgmp_time_to_peak': cgmp_peak_info['time_to_peak'],
                'vaso_peak': vaso_peak_info['peak_value'],
                'vaso_time_to_peak': vaso_peak_info['time_to_peak'],
                'no2_auc': no2_auc
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/export-csv', methods=['GET'])
def export_csv():
    """Export the latest simulation results as CSV"""
    try:
        # Check if there's a simulation in the session
        if 'last_simulation' not in session:
            return jsonify({
                'status': 'error',
                'message': 'No simulation data available. Run a simulation first.'
            }), 400
        
        # Get simulation data from session
        sim_data = session['last_simulation']
        
        # Create DataFrame
        time = sim_data['results']['time']
        time_hours = [t / 60 for t in time]
        no2 = sim_data['results']['no2']
        cgmp = sim_data['results']['cgmp']
        vasodilation = sim_data['results']['vasodilation']
        
        df = pd.DataFrame({
            'Time (hours)': time_hours,
            'Time (minutes)': time,
            'Plasma NO2- (µM)': no2,
            'cGMP (a.u.)': cgmp,
            'Vasodilation (%)': vasodilation
        })
        
        # Create CSV in memory
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        # Create response
        return send_file(
            io.BytesIO(csv_buffer.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='nitrite_simulation_results.csv'
        )
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/analyze-sensitivity', methods=['POST'])
def analyze_sensitivity():
    """Analyze parameter sensitivity"""
    try:
        data = request.get_json()
        
        # Extract parameters
        parameter = data.get('parameter', 'dose')
        min_value = float(data.get('min_value', 5.0))
        max_value = float(data.get('max_value', 60.0))
        num_points = int(data.get('num_points', 5))
        
        # Create values to test
        values = np.linspace(min_value, max_value, num_points)
        
        # Get fixed parameters from last simulation or use defaults
        if 'last_simulation' in session:
            fixed_params = session['last_simulation']['parameters']
        else:
            fixed_params = {
                'baseline': 0.2,
                'peak': 4.0,
                't_peak': 0.5,
                'half_life': 0.5,
                'egfr': 90.0,
                'rbc_count': 4.5e6,
                'dose': 30.0
            }
        
        # Perform sensitivity analysis
        optimizer = ParameterOptimizer()
        sensitivity_df, _ = optimizer.get_parameter_sensitivity(parameter, values, fixed_params)
        
        # Generate plot
        sensitivity_plot = optimizer.plot_sensitivity(parameter, values, fixed_params, return_base64=True)
        
        # Prepare data for response
        sensitivity_data = sensitivity_df.to_dict(orient='records')
        
        return jsonify({
            'status': 'success',
            'sensitivity_data': sensitivity_data,
            'plot': sensitivity_plot
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/optimize', methods=['POST'])
def optimize_parameters():
    """Optimize parameters to fit uploaded experimental data"""
    try:
        # Check if file is in the request
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No file selected'
            }), 400
        
        # Read the CSV file
        df = pd.read_csv(file)
        
        # Check for required columns
        if len(df.columns) < 2:
            return jsonify({
                'status': 'error',
                'message': 'CSV file must have at least two columns: time and concentration'
            }), 400
        
        # Try to detect time and concentration columns
        time_col = next((col for col in df.columns if 'Time' in col or 'time' in col), df.columns[0])
        conc_col = next((col for col in df.columns if 'NO2' in col or 'nitrite' in col or 'Nitrite' in col), df.columns[1])
        
        # Initialize optimizer
        optimizer = ParameterOptimizer()
        optimizer.load_data(dataframe=df, time_column=time_col, target_column=conc_col)
        
        # Set parameters to optimize
        params_to_optimize = {
            'baseline': 0.2,
            'peak': 4.0,
            't_peak': 0.5,
            'half_life': 0.5
        }
        
        # Run optimization
        result = optimizer.optimize(params_to_optimize=params_to_optimize)
        
        # Generate fit plot
        fit_plot = optimizer.plot_fit(return_base64=True)
        
        # Prepare response
        return jsonify({
            'status': 'success',
            'optimization_result': {
                'parameters': result['best_parameters'],
                'rmse': result['rmse'],
                'success': result['success'],
                'message': result['message']
            },
            'plot': fit_plot
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/compare-simulations', methods=['POST'])
def compare_simulations():
    """Compare multiple simulations with different parameters"""
    try:
        data = request.get_json()
        
        # Extract parameters for multiple simulations
        parameter_sets = data.get('parameter_sets', [])
        labels = data.get('labels', [])
        
        if not parameter_sets:
            return jsonify({
                'status': 'error',
                'message': 'No parameter sets provided'
            }), 400
        
        # Generate default labels if not provided
        if not labels or len(labels) != len(parameter_sets):
            labels = [f"Simulation {i+1}" for i in range(len(parameter_sets))]
        
        # Run simulations
        simulations = []
        for params in parameter_sets:
            simulator = NODynamicsSimulator(
                baseline=float(params.get('baseline', 0.2)),
                peak=float(params.get('peak', 4.0)),
                t_peak=float(params.get('t_peak', 0.5)),
                half_life=float(params.get('half_life', 0.5)),
                t_max=float(params.get('t_max', 6)),
                points=int(params.get('points', 360)),
                egfr=float(params.get('egfr', 90.0)),
                rbc_count=float(params.get('rbc_count', 4.5e6)),
                dose=float(params.get('dose', 30.0))
            )
            sim_df = simulator.simulate()
            simulations.append(sim_df)
        
        # Compare simulations
        analyzer = StatisticalAnalyzer()
        comparison_df = analyzer.compare_simulations(simulations, labels)
        
        # Generate comparison plot
        comparison_plot = analyzer.plot_comparison(simulations, labels, return_base64=True)
        
        # Prepare data for Chart.js
        chart_data = {
            'labels': labels,
            'datasets': []
        }
        
        # Extract data for each simulation
        for i, sim_df in enumerate(simulations):
            time_minutes = sim_df['Time (minutes)'].tolist()
            no2_values = sim_df['Plasma NO2- (µM)'].tolist()
            
            if i == 0:
                chart_data['time'] = time_minutes
            
            chart_data['datasets'].append({
                'label': labels[i],
                'data': no2_values
            })
        
        return jsonify({
            'status': 'success',
            'comparison': comparison_df.to_dict(orient='records'),
            'chart_data': chart_data,
            'plot': comparison_plot
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

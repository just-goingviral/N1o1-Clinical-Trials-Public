#!/usr/bin/env python3
"""
N1O1 Clinical Trials Simulator
A command-line tool for simulating nitrite, cGMP, and vasodilation dynamics

Author: Dustin Salinas
License: MIT
"""

import argparse
import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from simulation_core import NODynamicsSimulator
from statistical_analysis import StatisticalAnalyzer
from optimization import ParameterOptimizer

def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Simulate nitrite, cGMP, and vasodilation dynamics',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Basic simulation parameters
    parser.add_argument('--baseline', type=float, default=0.2,
                        help='Baseline plasma nitrite concentration (µM)')
    parser.add_argument('--peak', type=float, default=4.0,
                        help='Peak plasma nitrite concentration (µM)')
    parser.add_argument('--t-peak', type=float, default=0.5,
                        help='Time to peak concentration (hours)')
    parser.add_argument('--half-life', type=float, default=0.5,
                        help='Elimination half-life (hours)')
    parser.add_argument('--t-max', type=float, default=6,
                        help='Maximum simulation time (hours)')
    parser.add_argument('--points', type=int, default=360,
                        help='Number of time points for simulation')
    
    # Additional physiological parameters
    parser.add_argument('--egfr', type=float, default=90.0,
                        help='Estimated glomerular filtration rate (mL/min)')
    parser.add_argument('--rbc-count', type=float, default=4.5e6,
                        help='Red blood cell count (cells/µL)')
    parser.add_argument('--dose', type=float, default=30.0,
                        help='Dose of NO2- administered (mg)')
    
    # Output options
    parser.add_argument('--output', type=str, default=None,
                        help='Output file path for the plot')
    parser.add_argument('--csv', type=str, default=None,
                        help='Export results to CSV file')
    parser.add_argument('--animate', action='store_true',
                        help='Show animation instead of static plot')
    parser.add_argument('--save-animation', type=str, default=None,
                        help='Save animation to file (GIF or MP4)')
    
    # Analysis options
    parser.add_argument('--analyze', type=str, default=None,
                        help='Analyze CSV file with experimental data')
    parser.add_argument('--optimize', type=str, default=None,
                        help='Optimize parameters to fit experimental data in CSV file')
    parser.add_argument('--sensitivity', type=str, default=None,
                        help='Perform sensitivity analysis on parameter (e.g., "dose")')
    
    # Specific analyses options
    parser.add_argument('--no-plot', action='store_true',
                        help='Do not display plot (useful for batch processing)')
    
    return parser.parse_args()

def main():
    """Main function"""
    args = parse_arguments()
    
    # Create simulator with command-line parameters
    simulator = NODynamicsSimulator(
        baseline=args.baseline,
        peak=args.peak,
        t_peak=args.t_peak,
        half_life=args.half_life,
        t_max=args.t_max,
        points=args.points,
        egfr=args.egfr,
        rbc_count=args.rbc_count,
        dose=args.dose
    )
    
    # Run simulation
    results_df = simulator.simulate()
    
    # Export to CSV if requested
    if args.csv:
        csv_file = simulator.export_to_csv(args.csv)
        print(f"Results exported to {csv_file}")
    
    # Analyze experimental data if provided
    if args.analyze:
        if not os.path.exists(args.analyze):
            print(f"Error: File {args.analyze} not found.")
            return 1
        
        analyzer = StatisticalAnalyzer()
        data = analyzer.load_data(args.analyze)
        
        # Match column names
        if 'Plasma NO2- (µM)' in data.columns:
            target_column = 'Plasma NO2- (µM)'
        elif 'Plasma NO2-' in data.columns:
            target_column = 'Plasma NO2-'
        else:
            target_column = data.columns[1]  # Assume second column is the target
        
        # Print analysis results
        summary = analyzer.create_summary_report(target_column)
        print("\nAnalysis Results:")
        for key, value in summary.items():
            print(f"  {key}: {value}")
    
    # Optimize parameters if requested
    if args.optimize:
        if not os.path.exists(args.optimize):
            print(f"Error: File {args.optimize} not found.")
            return 1
        
        print("\nOptimizing parameters to fit experimental data...")
        optimizer = ParameterOptimizer()
        
        # Try to auto-detect column names
        exp_data = pd.read_csv(args.optimize)
        time_col = next((col for col in exp_data.columns if 'Time' in col), exp_data.columns[0])
        target_col = next((col for col in exp_data.columns if 'NO2' in col), exp_data.columns[1])
        
        optimizer.load_data(args.optimize, time_column=time_col, target_column=target_col)
        
        # Optimize standard parameters
        optimization_results = optimizer.optimize()
        
        print("\nOptimization Results:")
        print(f"  RMSE: {optimization_results['rmse']:.4f}")
        print("  Best Parameters:")
        for param, value in optimization_results['best_parameters'].items():
            print(f"    {param}: {value:.4f}")
        
        # Plot fit if not disabled
        if not args.no_plot:
            fig = optimizer.plot_fit()
            plt.show()
    
    # Perform sensitivity analysis if requested
    if args.sensitivity:
        param_name = args.sensitivity
        valid_params = ['baseline', 'peak', 't_peak', 'half_life', 'egfr', 'rbc_count', 'dose']
        
        if param_name not in valid_params:
            print(f"Error: Invalid parameter '{param_name}'. Valid options: {', '.join(valid_params)}")
            return 1
        
        # Define range of values to test
        if param_name == 'baseline':
            values = np.linspace(0.05, 1.0, 5)
        elif param_name == 'peak':
            values = np.linspace(1.0, 10.0, 5)
        elif param_name == 't_peak':
            values = np.linspace(0.1, 2.0, 5)
        elif param_name == 'half_life':
            values = np.linspace(0.1, 2.0, 5)
        elif param_name == 'egfr':
            values = np.linspace(30.0, 150.0, 5)
        elif param_name == 'rbc_count':
            values = np.linspace(2.0e6, 7.0e6, 5)
        elif param_name == 'dose':
            values = np.linspace(5.0, 60.0, 5)
        
        print(f"\nPerforming sensitivity analysis on {param_name}...")
        optimizer = ParameterOptimizer()
        
        # Create fixed parameters (current command-line values)
        fixed_params = {
            'baseline': args.baseline,
            'peak': args.peak,
            't_peak': args.t_peak,
            'half_life': args.half_life,
            'egfr': args.egfr,
            'rbc_count': args.rbc_count,
            'dose': args.dose
        }
        
        # Get sensitivity analysis results
        sensitivity_df, _ = optimizer.get_parameter_sensitivity(param_name, values, fixed_params)
        
        print("\nSensitivity Analysis Results:")
        print(sensitivity_df.to_string(index=False))
        
        # Plot if not disabled
        if not args.no_plot:
            fig = optimizer.plot_sensitivity(param_name, values, fixed_params)
            plt.show()
    
    # Display results if not in analysis-only mode
    if not args.no_plot and not args.optimize and not args.sensitivity:
        if args.animate:
            # Show animation
            ani = simulator.create_animation(save_path=args.save_animation)
            plt.show()
        else:
            # Show static plot
            simulator.plot_static(save_path=args.output)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

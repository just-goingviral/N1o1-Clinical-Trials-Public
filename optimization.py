"""
Parameter optimization module for NO dynamics simulation
Author: Dustin Salinas
License: MIT
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from simulation_core import NODynamicsSimulator
import matplotlib.pyplot as plt
from io import BytesIO
import base64

class ParameterOptimizer:
    """
    A class for optimizing NO dynamics simulation parameters to fit experimental data
    """
    
    def __init__(self, experimental_data=None):
        """
        Initialize the parameter optimizer
        
        Parameters:
        -----------
        experimental_data : pandas.DataFrame, optional
            DataFrame containing experimental data with 'Time' and target columns
        """
        self.experimental_data = experimental_data
        self.simulator = NODynamicsSimulator()
        self.target_column = None
        self.time_column = None
        self.result = None
        self.best_params = None
        self.best_simulation = None
    
    def load_data(self, file_path=None, dataframe=None, time_column='Time (minutes)', target_column='Plasma NO2- (µM)'):
        """
        Load experimental data for fitting
        
        Parameters:
        -----------
        file_path : str, optional
            Path to a CSV file containing experimental data
        dataframe : pandas.DataFrame, optional
            DataFrame containing experimental data
        time_column : str, optional
            Name of the column containing time values
        target_column : str, optional
            Name of the column containing target values to fit
            
        Returns:
        --------
        pandas.DataFrame
            The loaded experimental data
        """
        if file_path is not None:
            self.experimental_data = pd.read_csv(file_path)
        elif dataframe is not None:
            self.experimental_data = dataframe.copy()
        else:
            raise ValueError("Either file_path or dataframe must be provided")
        
        self.time_column = time_column
        self.target_column = target_column
        
        # Check if the required columns exist
        if self.time_column not in self.experimental_data.columns:
            raise ValueError(f"Time column '{self.time_column}' not found in data")
        if self.target_column not in self.experimental_data.columns:
            raise ValueError(f"Target column '{self.target_column}' not found in data")
        
        return self.experimental_data
    
    def _objective_function(self, params, param_names):
        """
        Objective function for optimization (RMSE between simulation and experimental data)
        
        Parameters:
        -----------
        params : array-like
            Parameter values to try
        param_names : list
            Names of the parameters in the same order as params
            
        Returns:
        --------
        float
            Root mean square error between simulation and experimental data
        """
        # Create a parameter dictionary for the simulator
        param_dict = {name: value for name, value in zip(param_names, params)}
        
        # Update the simulator with these parameters
        for param_name, value in param_dict.items():
            setattr(self.simulator, param_name, value)
        
        # Run the simulation
        simulation_df = self.simulator.simulate()
        
        # Convert time if needed
        if 'minutes' in self.time_column and 'hours' in simulation_df.columns[0]:
            sim_time_col = 'Time (hours)'
            exp_time_values = self.experimental_data[self.time_column].values / 60.0
        elif 'hours' in self.time_column and 'minutes' in simulation_df.columns[1]:
            sim_time_col = 'Time (minutes)'
            exp_time_values = self.experimental_data[self.time_column].values * 60.0
        else:
            sim_time_col = simulation_df.columns[0] if 'Time' in simulation_df.columns[0] else simulation_df.columns[1]
            exp_time_values = self.experimental_data[self.time_column].values
        
        # Interpolate simulation values at experimental time points
        target_col = [col for col in simulation_df.columns if self.target_column.split('(')[0].strip() in col][0]
        sim_values = np.interp(exp_time_values, simulation_df[sim_time_col].values, simulation_df[target_col].values)
        
        # Calculate RMSE
        exp_values = self.experimental_data[self.target_column].values
        rmse = np.sqrt(np.mean((sim_values - exp_values) ** 2))
        
        return rmse
    
    def optimize(self, params_to_optimize=None, bounds=None, method='L-BFGS-B'):
        """
        Optimize simulation parameters to fit experimental data
        
        Parameters:
        -----------
        params_to_optimize : dict, optional
            Dictionary of parameter names and initial values to optimize
            Default is {'baseline': 0.2, 'peak': 4.0, 't_peak': 0.5, 'half_life': 0.5}
        bounds : dict, optional
            Dictionary of parameter bounds (min, max) for each parameter
            Default uses reasonable bounds for each parameter
        method : str, optional
            Optimization method to use
            
        Returns:
        --------
        dict
            Dictionary containing optimization results
        """
        if self.experimental_data is None:
            raise ValueError("No experimental data loaded. Call load_data first.")
        
        # Default parameters to optimize if none provided
        if params_to_optimize is None:
            params_to_optimize = {
                'baseline': 0.2,
                'peak': 4.0,
                't_peak': 0.5,
                'half_life': 0.5
            }
        
        # Default bounds if none provided
        if bounds is None:
            bounds = {
                'baseline': (0.01, 1.0),
                'peak': (0.5, 20.0),
                't_peak': (0.1, 2.0),
                'half_life': (0.1, 5.0),
                'egfr': (30.0, 150.0),
                'rbc_count': (2.0e6, 7.0e6),
                'dose': (5.0, 100.0)
            }
        
        # Get parameter names and initial values
        param_names = list(params_to_optimize.keys())
        initial_values = [params_to_optimize[name] for name in param_names]
        
        # Get bounds for the parameters being optimized
        param_bounds = [bounds.get(name, (0.01, 100.0)) for name in param_names]
        
        # Run optimization
        self.result = minimize(
            self._objective_function,
            initial_values,
            args=(param_names,),
            bounds=param_bounds,
            method=method
        )
        
        # Update best parameters
        self.best_params = {name: value for name, value in zip(param_names, self.result.x)}
        
        # Run simulation with best parameters
        for param_name, value in self.best_params.items():
            setattr(self.simulator, param_name, value)
        
        self.best_simulation = self.simulator.simulate()
        
        # Prepare results summary
        optimization_results = {
            'best_parameters': self.best_params,
            'rmse': self.result.fun,
            'success': self.result.success,
            'message': self.result.message,
            'iterations': self.result.nit,
            'function_evaluations': self.result.nfev
        }
        
        return optimization_results
    
    def plot_fit(self, return_base64=False):
        """
        Plot the experimental data and the optimized simulation
        
        Parameters:
        -----------
        return_base64 : bool, optional
            If True, return a base64 encoded image string
            
        Returns:
        --------
        matplotlib.figure.Figure or str
            Figure object or base64 encoded image string
        """
        if self.best_simulation is None:
            raise ValueError("No optimization results. Call optimize first.")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Convert time if needed for plotting
        if 'minutes' in self.time_column and 'hours' in self.best_simulation.columns[0]:
            sim_time_col = 'Time (hours)'
            exp_time_values = self.experimental_data[self.time_column].values / 60.0
            x_label = 'Time (hours)'
        elif 'hours' in self.time_column and 'minutes' in self.best_simulation.columns[1]:
            sim_time_col = 'Time (minutes)'
            exp_time_values = self.experimental_data[self.time_column].values * 60.0
            x_label = 'Time (minutes)'
        else:
            sim_time_col = self.best_simulation.columns[0] if 'Time' in self.best_simulation.columns[0] else self.best_simulation.columns[1]
            exp_time_values = self.experimental_data[self.time_column].values
            x_label = self.time_column
        
        # Plot experimental data
        ax.scatter(
            exp_time_values, 
            self.experimental_data[self.target_column], 
            color='red', 
            marker='o', 
            label='Experimental Data'
        )
        
        # Plot optimized simulation
        target_col = [col for col in self.best_simulation.columns if self.target_column.split('(')[0].strip() in col][0]
        ax.plot(
            self.best_simulation[sim_time_col], 
            self.best_simulation[target_col], 
            color='blue', 
            linewidth=2, 
            label='Optimized Simulation'
        )
        
        # Add parameters to plot
        param_text = '\n'.join([f"{param}: {value:.3f}" for param, value in self.best_params.items()])
        ax.text(
            0.02, 0.98, 
            f"Best Parameters:\n{param_text}\nRMSE: {self.result.fun:.4f}",
            transform=ax.transAxes,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
        )
        
        ax.set_xlabel(x_label)
        ax.set_ylabel(self.target_column)
        ax.set_title('Optimization Results: Experimental Data vs. Optimized Simulation')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        
        plt.tight_layout()
        
        if return_base64:
            buffer = BytesIO()
            fig.savefig(buffer, format='png', dpi=100)
            buffer.seek(0)
            img_str = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close(fig)
            return f'data:image/png;base64,{img_str}'
        else:
            return fig
    
    def get_parameter_sensitivity(self, parameter, values, fixed_params=None):
        """
        Analyze sensitivity of the model to a specific parameter
        
        Parameters:
        -----------
        parameter : str
            Name of the parameter to analyze
        values : list
            List of values to test for the parameter
        fixed_params : dict, optional
            Dictionary of fixed parameter values for other parameters
            
        Returns:
        --------
        pandas.DataFrame
            DataFrame containing sensitivity analysis results
        """
        if fixed_params is None and self.best_params is not None:
            fixed_params = self.best_params
        elif fixed_params is None:
            fixed_params = {
                'baseline': 0.2,
                'peak': 4.0,
                't_peak': 0.5,
                'half_life': 0.5,
                'egfr': 90.0,
                'rbc_count': 4.5e6,
                'dose': 30.0
            }
        
        # Make a copy of fixed parameters
        base_params = fixed_params.copy()
        
        # Store simulation results for each parameter value
        results = []
        simulations = []
        
        for value in values:
            # Set parameter value
            base_params[parameter] = value
            
            # Update simulator parameters
            for param_name, param_value in base_params.items():
                setattr(self.simulator, param_name, param_value)
            
            # Run simulation
            sim_df = self.simulator.simulate()
            simulations.append(sim_df)
            
            # Extract key metrics
            target_col = 'Plasma NO2- (µM)'
            time_col = 'Time (hours)' if 'Time (hours)' in sim_df.columns else 'Time (minutes)'
            
            peak_idx = sim_df[target_col].idxmax()
            peak_value = sim_df.loc[peak_idx, target_col]
            time_to_peak = sim_df.loc[peak_idx, time_col]
            auc = np.trapz(sim_df[target_col], sim_df[time_col])
            
            # Store results
            results.append({
                'Parameter': parameter,
                'Value': value,
                'Peak': peak_value,
                'Time to Peak': time_to_peak,
                'AUC': auc
            })
        
        return pd.DataFrame(results), simulations
    
    def plot_sensitivity(self, parameter, values, fixed_params=None, return_base64=False):
        """
        Plot sensitivity analysis results
        
        Parameters:
        -----------
        parameter : str
            Name of the parameter to analyze
        values : list
            List of values to test for the parameter
        fixed_params : dict, optional
            Dictionary of fixed parameter values for other parameters
        return_base64 : bool, optional
            If True, return a base64 encoded image string
            
        Returns:
        --------
        matplotlib.figure.Figure or str
            Figure object or base64 encoded image string
        """
        # Run sensitivity analysis
        sensitivity_df, simulations = self.get_parameter_sensitivity(parameter, values, fixed_params)
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Plot parameter values vs metrics in the first subplot
        ax1.plot(sensitivity_df['Value'], sensitivity_df['Peak'], 'o-', label='Peak Concentration')
        ax1.set_xlabel(f'{parameter} Value')
        ax1.set_ylabel('Peak Concentration (µM)')
        ax1.grid(True, alpha=0.3)
        ax1.set_title(f'Parameter Sensitivity: Effect of {parameter} on Peak')
        
        # Plot concentration-time profiles in the second subplot
        colors = plt.cm.viridis(np.linspace(0, 1, len(values)))
        
        for i, (sim_df, value) in enumerate(zip(simulations, values)):
            time_col = 'Time (hours)' if 'Time (hours)' in sim_df.columns else 'Time (minutes)'
            target_col = 'Plasma NO2- (µM)'
            
            ax2.plot(
                sim_df[time_col], 
                sim_df[target_col], 
                color=colors[i], 
                linewidth=2, 
                label=f'{parameter}={value}'
            )
        
        ax2.set_xlabel('Time')
        ax2.set_ylabel('Plasma NO2- (µM)')
        ax2.set_title(f'Concentration-Time Profiles for Different {parameter} Values')
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='best')
        
        plt.tight_layout()
        
        if return_base64:
            buffer = BytesIO()
            fig.savefig(buffer, format='png', dpi=100)
            buffer.seek(0)
            img_str = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close(fig)
            return f'data:image/png;base64,{img_str}'
        else:
            return fig

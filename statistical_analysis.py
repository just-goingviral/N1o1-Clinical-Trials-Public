"""
Statistical analysis module for NO dynamics simulation data
Author: Dustin Salinas
License: MIT
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
from io import BytesIO
import base64

class StatisticalAnalyzer:
    """
    A class for analyzing nitrite, cGMP, and vasodilation data from clinical trials
    """
    
    def __init__(self):
        """Initialize the statistical analyzer"""
        pass
    
    def load_data(self, file_path=None, dataframe=None):
        """
        Load data either from a CSV file or a pandas DataFrame
        
        Parameters:
        -----------
        file_path : str, optional
            Path to a CSV file containing simulation or experimental data
        dataframe : pandas.DataFrame, optional
            DataFrame containing simulation or experimental data
            
        Returns:
        --------
        pandas.DataFrame
            The loaded data
        """
        if file_path is not None:
            self.data = pd.read_csv(file_path)
        elif dataframe is not None:
            self.data = dataframe.copy()
        else:
            raise ValueError("Either file_path or dataframe must be provided")
        
        return self.data
    
    def compute_descriptive_statistics(self, columns=None):
        """
        Compute descriptive statistics for the specified columns
        
        Parameters:
        -----------
        columns : list, optional
            List of column names to analyze. If None, analyze all numeric columns.
            
        Returns:
        --------
        pandas.DataFrame
            DataFrame containing descriptive statistics
        """
        if not hasattr(self, 'data'):
            raise ValueError("No data loaded. Call load_data first.")
        
        if columns is None:
            numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()
        else:
            numeric_cols = [col for col in columns if col in self.data.columns]
        
        stats_df = self.data[numeric_cols].describe().T
        
        # Add additional statistics
        stats_df['median'] = self.data[numeric_cols].median()
        stats_df['skew'] = self.data[numeric_cols].skew()
        stats_df['kurtosis'] = self.data[numeric_cols].kurtosis()
        stats_df['variance'] = self.data[numeric_cols].var()
        
        return stats_df
    
    def area_under_curve(self, x_column, y_column):
        """
        Calculate the area under the curve using the trapezoidal rule
        
        Parameters:
        -----------
        x_column : str
            Name of the column containing x values (typically time)
        y_column : str
            Name of the column containing y values
            
        Returns:
        --------
        float
            Area under the curve
        """
        if not hasattr(self, 'data'):
            raise ValueError("No data loaded. Call load_data first.")
        
        x = self.data[x_column].values
        y = self.data[y_column].values
        
        auc = np.trapz(y, x)
        return auc
    
    def peak_analysis(self, column):
        """
        Identify the peak value and time to peak for a column
        
        Parameters:
        -----------
        column : str
            Name of the column to analyze
            
        Returns:
        --------
        dict
            Dictionary containing peak value and time to peak
        """
        if not hasattr(self, 'data'):
            raise ValueError("No data loaded. Call load_data first.")
        
        time_col = 'Time (hours)' if 'Time (hours)' in self.data.columns else 'Time (minutes)'
        
        peak_idx = self.data[column].idxmax()
        peak_value = self.data.loc[peak_idx, column]
        time_to_peak = self.data.loc[peak_idx, time_col]
        
        return {
            'peak_value': peak_value,
            'time_to_peak': time_to_peak,
            'peak_index': peak_idx
        }
    
    def half_life_analysis(self, column, baseline=None):
        """
        Calculate the half-life of a substance based on simulation or experimental data
        
        Parameters:
        -----------
        column : str
            Name of the column to analyze
        baseline : float, optional
            Baseline value. If None, the first value is used as baseline.
            
        Returns:
        --------
        float
            Estimated half-life in hours
        """
        if not hasattr(self, 'data'):
            raise ValueError("No data loaded. Call load_data first.")
        
        time_col = 'Time (hours)' if 'Time (hours)' in self.data.columns else 'Time (minutes)'
        if time_col == 'Time (minutes)':
            time_factor = 60.0  # Convert minutes to hours
        else:
            time_factor = 1.0
        
        # Get peak information
        peak_info = self.peak_analysis(column)
        peak_idx = peak_info['peak_index']
        peak_value = peak_info['peak_value']
        
        # Use data after the peak for half-life calculation
        post_peak_data = self.data.iloc[peak_idx:].copy()
        
        if len(post_peak_data) < 3:
            return None  # Not enough data points for calculation
        
        # If no baseline provided, use the last value as an approximation
        if baseline is None:
            baseline = post_peak_data[column].iloc[-1]
        
        # Calculate the time it takes to reach half of the peak value above baseline
        half_value = baseline + (peak_value - baseline) / 2
        
        # Find the closest point to the half value
        post_peak_data['diff_from_half'] = abs(post_peak_data[column] - half_value)
        half_idx = post_peak_data['diff_from_half'].idxmin()
        
        half_time = post_peak_data.loc[half_idx, time_col]
        peak_time = post_peak_data.loc[peak_idx, time_col]
        
        half_life = (half_time - peak_time) / time_factor
        
        return half_life
    
    def compare_simulations(self, simulations, labels=None, column='Plasma NO2- (µM)'):
        """
        Compare multiple simulation results
        
        Parameters:
        -----------
        simulations : list
            List of pandas DataFrames containing simulation results
        labels : list, optional
            List of labels for the simulations
        column : str, optional
            Column to compare across simulations
            
        Returns:
        --------
        pandas.DataFrame
            DataFrame containing comparison metrics
        """
        if labels is None:
            labels = [f"Simulation {i+1}" for i in range(len(simulations))]
        
        if len(simulations) != len(labels):
            raise ValueError("Length of simulations and labels must be the same")
        
        comparison_metrics = []
        
        for i, sim_df in enumerate(simulations):
            analyzer = StatisticalAnalyzer()
            analyzer.load_data(dataframe=sim_df)
            
            time_col = 'Time (hours)' if 'Time (hours)' in sim_df.columns else 'Time (minutes)'
            
            peak_info = analyzer.peak_analysis(column)
            auc = analyzer.area_under_curve(time_col, column)
            half_life = analyzer.half_life_analysis(column)
            
            metrics = {
                'Label': labels[i],
                'Peak Value': peak_info['peak_value'],
                'Time to Peak': peak_info['time_to_peak'],
                'AUC': auc,
                'Half-life': half_life
            }
            
            comparison_metrics.append(metrics)
        
        return pd.DataFrame(comparison_metrics)
    
    def plot_comparison(self, simulations, labels=None, column='Plasma NO2- (µM)', return_base64=False):
        """
        Create a comparison plot of multiple simulations
        
        Parameters:
        -----------
        simulations : list
            List of pandas DataFrames containing simulation results
        labels : list, optional
            List of labels for the simulations
        column : str, optional
            Column to compare across simulations
        return_base64 : bool, optional
            If True, return a base64 encoded image string
            
        Returns:
        --------
        matplotlib.figure.Figure or str
            Figure object or base64 encoded image string
        """
        if labels is None:
            labels = [f"Simulation {i+1}" for i in range(len(simulations))]
        
        if len(simulations) != len(labels):
            raise ValueError("Length of simulations and labels must be the same")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(simulations)))
        
        for i, sim_df in enumerate(simulations):
            time_col = 'Time (hours)' if 'Time (hours)' in sim_df.columns else 'Time (minutes)'
            
            if time_col == 'Time (minutes)':
                x_label = 'Time (minutes)'
            else:
                x_label = 'Time (hours)'
            
            ax.plot(sim_df[time_col], sim_df[column], 
                   label=labels[i], color=colors[i], linewidth=2)
        
        ax.set_xlabel(x_label)
        ax.set_ylabel(column)
        ax.set_title(f'Comparison of {column} Across Simulations')
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
    
    def confidence_interval(self, column, confidence=0.95):
        """
        Calculate confidence interval for a column
        
        Parameters:
        -----------
        column : str
            Name of the column to analyze
        confidence : float, optional
            Confidence level (0 to 1)
            
        Returns:
        --------
        tuple
            Lower and upper bounds of the confidence interval
        """
        if not hasattr(self, 'data'):
            raise ValueError("No data loaded. Call load_data first.")
        
        data = self.data[column].dropna()
        
        mean = data.mean()
        sem = stats.sem(data)
        interval = stats.t.interval(confidence, len(data)-1, loc=mean, scale=sem)
        
        return interval
    
    def create_summary_report(self, column='Plasma NO2- (µM)'):
        """
        Create a summary report of the key metrics
        
        Parameters:
        -----------
        column : str, optional
            Column to analyze
            
        Returns:
        --------
        dict
            Dictionary containing key metrics
        """
        if not hasattr(self, 'data'):
            raise ValueError("No data loaded. Call load_data first.")
        
        time_col = 'Time (hours)' if 'Time (hours)' in self.data.columns else 'Time (minutes)'
        
        peak_info = self.peak_analysis(column)
        auc = self.area_under_curve(time_col, column)
        half_life = self.half_life_analysis(column)
        desc_stats = self.compute_descriptive_statistics([column])
        
        report = {
            'Column': column,
            'Peak Value': peak_info['peak_value'],
            'Time to Peak': peak_info['time_to_peak'],
            'AUC': auc,
            'Half-life': half_life,
            'Mean': desc_stats.loc[column, 'mean'],
            'Std Dev': desc_stats.loc[column, 'std'],
            'Min': desc_stats.loc[column, 'min'],
            'Max': desc_stats.loc[column, 'max']
        }
        
        return report

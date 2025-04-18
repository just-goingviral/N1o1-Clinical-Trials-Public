"""
Core simulation module for N1O1 Clinical Trials 
Based on pharmacokinetic models of nitrite metabolism
Author: Dustin Salinas
License: MIT
"""

import numpy as np
from scipy.integrate import solve_ivp
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from io import BytesIO
import base64

class NODynamicsSimulator:
    """
    A class for simulating nitrite, cGMP, and vasodilation dynamics after nitrite supplementation
    """
    
    def __init__(self, 
                 baseline=0.2,     # Baseline plasma nitrite concentration (µM)
                 peak=4.0,         # Peak plasma nitrite concentration (µM)
                 t_peak=0.5,       # Time to peak concentration (hours)
                 half_life=0.5,    # Elimination half-life (hours)
                 t_max=6,          # Maximum simulation time (hours)
                 points=360,       # Number of time points for simulation
                 egfr=90.0,        # Estimated glomerular filtration rate (mL/min)
                 rbc_count=4.5e6,  # Red blood cell count (cells/µL)
                 dose=30.0,        # Dose of NO2- administered (mg)
                 additional_doses=None, # Additional doses as list of dicts with 'time' and 'amount'
                 formulation="immediate-release" # Formulation type (immediate-release, extended-release)
                ):
        """
        Initialize the simulator with customizable parameters
        """
        self.baseline = baseline
        self.peak = peak
        self.t_peak = t_peak
        self.half_life = half_life
        self.t_max = t_max
        self.points = points
        self.egfr = egfr
        self.rbc_count = rbc_count
        self.dose = dose
        self.additional_doses = additional_doses or []
        self.formulation = formulation
        """
        Initialize the simulator with customizable parameters
        """
        self.baseline = baseline
        self.peak = peak
        self.t_peak = t_peak
        self.half_life = half_life
        self.t_max = t_max
        self.points = points
        self.egfr = egfr
        self.rbc_count = rbc_count
        self.dose = dose
        
        # Calculated values
        self.k_clear = self._renal_clearance_rate(self.egfr)
        self.k_rbc = self._rbc_scavenging_rate(self.rbc_count)
        
        # Initialized values for simulation results
        self.t_eval = None
        self.plasma_no2 = None
        self.cgmp_levels = None
        self.vasodilation = None
        self.results_df = None
    
    def _renal_clearance_rate(self, egfr):
        """Calculate renal clearance rate based on eGFR"""
        return 0.1 * (egfr / 60.0)
    
    def _rbc_scavenging_rate(self, rbc_count, oxygen_saturation=0.97):
        """
        Calculate RBC scavenging rate based on RBC count and oxygen saturation
        
        Parameters:
        -----------
        rbc_count : float
            Red blood cell count (cells/µL)
        oxygen_saturation : float
            Blood oxygen saturation (0-1), default 0.97 (normoxia)
            Lower values represent hypoxic conditions
        
        Returns:
        --------
        float
            Scavenging rate constant
        """
        # Base scavenging rate
        base_rate = 0.02 * (rbc_count / 1.0e6)
        
        # Hypoxia adjustment factor - RBCs convert less nitrite to NO when oxygenated
        # and more when deoxygenated (hypoxic conditions)
        hypoxia_factor = 1 - oxygen_saturation  # Higher in hypoxia
        
        # Adjust scavenging rate (higher value = faster scavenging)
        return base_rate * (1 - 0.5 * hypoxia_factor)
    
    def simulate_hypoxia(self, oxygen_saturation=0.8):
        """
        Run simulation under hypoxic conditions
        
        Parameters:
        -----------
        oxygen_saturation : float
            Blood oxygen saturation (0-1), lower values = more hypoxic
            
        Returns:
        --------
        pandas.DataFrame
            Simulation results under hypoxic conditions
        """
        # Store original k_rbc
        original_k_rbc = self.k_rbc
        
        # Set hypoxic k_rbc
        self.k_rbc = self._rbc_scavenging_rate(self.rbc_count, oxygen_saturation)
        
        # Run simulation
        results = self.simulate()
        
        # Reset to original value
        self.k_rbc = original_k_rbc
        
        return results
    
    def _dose_input(self, t, dose=30.0, t_IR=0.0, additional_doses=None):
        """
        Model dose input with support for multiple dosing regimens
        
        Parameters:
        -----------
        t : float
            Current time (hours)
        dose : float
            Primary dose (mg)
        t_IR : float
            Time of primary dose administration (hours)
        additional_doses : list of dict, optional
            List of additional doses, each a dict with 'time' and 'amount' keys
        """
        # Immediate release approximation (standard dissolution)
        result = 0.0
        
        # Primary dose
        if t_IR <= t < (t_IR + 0.083):  # Approximating quick dissolution (5 min)
            result += (dose / 0.083)
            
        # Additional doses if specified
        if additional_doses:
            for dose_info in additional_doses:
                dose_time = dose_info['time']  # Time in hours
                dose_amount = dose_info['amount']  # Dose in mg
                
                if dose_time <= t < (dose_time + 0.083):
                    result += (dose_amount / 0.083)
                    
        return result
    
    def _no2_ode(self, t, y):
        """
        ODE model for nitrite concentration with tissue distribution
        y[0]: Plasma nitrite concentration (µM)
        y[1]: Tissue nitrite concentration (µM) - represents muscle, organs, etc.
        y[2]: Erythrocyte nitrite concentration (µM) - represents RBC-bound nitrite
        """
        # Adapt absorption rate based on formulation
        dissolution_factor = 1.0
        if self.formulation == "extended-release":
            dissolution_factor = 0.3  # Slower dissolution for extended release
        
        input_flux = self._dose_input(
            t, 
            dose=self.dose * dissolution_factor,
            additional_doses=self.additional_doses
        )
        
        # Transfer rate constants
        k_plasma_to_tissue = 0.05  # Plasma to tissue transfer rate
        k_tissue_to_plasma = 0.03  # Tissue to plasma transfer rate
        k_plasma_to_rbc = self.k_rbc * 0.5  # Plasma to RBC transfer rate
        k_rbc_to_no = 0.01  # RBC nitrite to NO conversion rate (increases in hypoxia)
        
        # Tissue distribution - two-way transfer between plasma and tissues
        plasma_to_tissue = k_plasma_to_tissue * y[0]
        tissue_to_plasma = k_tissue_to_plasma * y[1]
        
        # RBC interactions
        plasma_to_rbc = k_plasma_to_rbc * y[0]
        rbc_to_no = k_rbc_to_no * y[2]
        
        # Renal clearance only applies to plasma
        renal_clearance = self.k_clear * y[0]
        
        # Extended release formulation continues to release drug over time
        if self.formulation == "extended-release":
            extended_release_rate = 0.7 * self.dose * np.exp(-t / 2) / 4  # Sustained release over ~4 hours
            if t < 4:  # Only contribute during the first 4 hours
                input_flux += extended_release_rate
        
        # Differential equations for each compartment
        dplasma_dt = input_flux + tissue_to_plasma - plasma_to_tissue - plasma_to_rbc - renal_clearance
        dtissue_dt = plasma_to_tissue - tissue_to_plasma
        drbc_dt = plasma_to_rbc - rbc_to_no
        
        return [dplasma_dt, dtissue_dt, drbc_dt]
    
    def _calculate_cgmp(self, no2_array):
        """Calculate cGMP levels based on nitrite concentration"""
        return 10 * (no2_array / max(no2_array)) if max(no2_array) > 0 else np.zeros_like(no2_array)
    
    def _calculate_vasodilation(self, cgmp_array):
        """Calculate vasodilation percentage based on cGMP levels"""
        return 100 + 50 * (cgmp_array / max(cgmp_array)) if max(cgmp_array) > 0 else 100 * np.ones_like(cgmp_array)
    
    def simulate(self):
        """Run the simulation with current parameters using multi-compartment model"""
        self.t_eval = np.linspace(0, self.t_max, self.points)
        
        # Initial conditions for all compartments
        # [plasma, tissue, RBC]
        initial_conditions = [self.baseline, self.baseline * 0.5, self.baseline * 0.2]
        
        # Solve the ODE system
        sol = solve_ivp(
            lambda t, y: self._no2_ode(t, y), 
            [0, self.t_max], 
            initial_conditions, 
            t_eval=self.t_eval,
            method='RK45',
            rtol=1e-6
        )
        
        # Extract solutions for each compartment
        self.plasma_no2 = sol.y[0]
        self.tissue_no2 = sol.y[1]
        self.rbc_no2 = sol.y[2]
        
        # Calculate total body nitrite (weighted sum)
        self.total_body_no2 = 0.7 * self.plasma_no2 + 0.2 * self.tissue_no2 + 0.1 * self.rbc_no2
        
        # Calculate bioactive NO (proportional to RBC nitrite in our model)
        self.bioactive_no = 0.5 * self.rbc_no2
        
        # Calculate derived physiological outputs
        self.cgmp_levels = self._calculate_cgmp(self.bioactive_no)
        self.vasodilation = self._calculate_vasodilation(self.cgmp_levels)
        
        # Create a pandas DataFrame with the results
        self.results_df = pd.DataFrame({
            'Time (hours)': self.t_eval,
            'Time (minutes)': self.t_eval * 60,
            'Plasma NO2- (µM)': self.plasma_no2,
            'Tissue NO2- (µM)': self.tissue_no2,
            'RBC NO2- (µM)': self.rbc_no2,
            'Total Body NO2- (µM)': self.total_body_no2,
            'Bioactive NO (a.u.)': self.bioactive_no,
            'cGMP (a.u.)': self.cgmp_levels,
            'Vasodilation (%)': self.vasodilation
        })
        
        return self.results_df
    
    def export_to_csv(self, filename="simulation_results.csv"):
        """Export simulation results to CSV file"""
        if self.results_df is None:
            self.simulate()
        
        self.results_df.to_csv(filename, index=False)
        return filename
    
    def plot_static(self, show=True, save_path=None):
        """Generate a static plot of simulation results"""
        if self.plasma_no2 is None:
            self.simulate()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(self.t_eval * 60, self.plasma_no2, lw=2, color='purple', label='Plasma NO₂⁻ (µM)')
        ax.plot(self.t_eval * 60, self.cgmp_levels, lw=2, color='green', linestyle='--', label='cGMP (a.u.)')
        ax.plot(self.t_eval * 60, self.vasodilation, lw=2, color='blue', linestyle=':', label='Vasodilation (%)')
        
        ax.set_xlim(0, self.t_max * 60)
        ax.set_ylim(0, max(self.vasodilation) * 1.2)
        ax.set_xlabel('Time (minutes)')
        ax.set_ylabel('Response (relative units)')
        ax.set_title('N1O1 Clinical Trials – Plasma NO₂⁻, cGMP, Vasodilation')
        ax.grid(True)
        ax.legend(loc='upper right')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        if show:
            plt.show()
        else:
            plt.close()
        
        return fig, ax
    
    def create_animation(self, show=True, save_path=None, fps=6):
        """Create an animation of simulation results"""
        if self.plasma_no2 is None:
            self.simulate()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        line_no2, = ax.plot([], [], lw=2, color='purple', label='Plasma NO₂⁻ (µM)')
        line_cgmp, = ax.plot([], [], lw=2, color='green', linestyle='--', label='cGMP (a.u.)')
        line_vaso, = ax.plot([], [], lw=2, color='blue', linestyle=':', label='Vasodilation (%)')
        
        time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)
        conc_text = ax.text(0.02, 0.90, '', transform=ax.transAxes)
        
        ax.set_xlim(0, self.t_max * 60)
        ax.set_ylim(0, max(self.vasodilation) * 1.2)
        ax.set_xlabel('Time (minutes)')
        ax.set_ylabel('Response (relative units)')
        ax.set_title('N1O1 Clinical Trials – Plasma NO₂⁻, cGMP, Vasodilation')
        ax.grid(True)
        ax.legend(loc='upper right')
        
        x_data, no2_data, cgmp_data, vaso_data = [], [], [], []
        
        def init():
            line_no2.set_data([], [])
            line_cgmp.set_data([], [])
            line_vaso.set_data([], [])
            time_text.set_text('')
            conc_text.set_text('')
            return line_no2, line_cgmp, line_vaso, time_text, conc_text
        
        def update(frame):
            t_min = self.t_eval[frame] * 60
            no2 = self.plasma_no2[frame]
            cgmp = self.cgmp_levels[frame]
            vaso = self.vasodilation[frame]
            
            x_data.append(t_min)
            no2_data.append(no2)
            cgmp_data.append(cgmp)
            vaso_data.append(vaso)
            
            line_no2.set_data(x_data, no2_data)
            line_cgmp.set_data(x_data, cgmp_data)
            line_vaso.set_data(x_data, vaso_data)
            
            time_text.set_text(f"Time: {int(t_min)} min")
            conc_text.set_text(f"NO₂⁻: {no2:.2f} µM | cGMP: {cgmp:.1f} | Vasodilation: {vaso:.1f}%")
            return line_no2, line_cgmp, line_vaso, time_text, conc_text
        
        ani = animation.FuncAnimation(
            fig, update, frames=len(self.t_eval),
            init_func=init, blit=True, interval=1000/fps
        )
        
        plt.tight_layout()
        
        if save_path:
            ani.save(save_path, fps=fps, dpi=200)
        
        if show:
            plt.show()
        else:
            plt.close()
        
        return ani
    
    def get_animation_html(self, fps=6):
        """Generate HTML with embedded animation for web display"""
        if self.plasma_no2 is None:
            self.simulate()
            
        fig, ax = plt.subplots(figsize=(10, 5))
        line_no2, = ax.plot([], [], lw=2, color='purple', label='Plasma NO₂⁻ (µM)')
        line_cgmp, = ax.plot([], [], lw=2, color='green', linestyle='--', label='cGMP (a.u.)')
        line_vaso, = ax.plot([], [], lw=2, color='blue', linestyle=':', label='Vasodilation (%)')
        
        time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)
        conc_text = ax.text(0.02, 0.90, '', transform=ax.transAxes)
        
        ax.set_xlim(0, self.t_max * 60)
        ax.set_ylim(0, max(self.vasodilation) * 1.2)
        ax.set_xlabel('Time (minutes)')
        ax.set_ylabel('Response (relative units)')
        ax.set_title('N1O1 Clinical Trials – Plasma NO₂⁻, cGMP, Vasodilation')
        ax.grid(True)
        ax.legend(loc='upper right')
        
        x_data, no2_data, cgmp_data, vaso_data = [], [], [], []
        
        def init():
            line_no2.set_data([], [])
            line_cgmp.set_data([], [])
            line_vaso.set_data([], [])
            time_text.set_text('')
            conc_text.set_text('')
            return line_no2, line_cgmp, line_vaso, time_text, conc_text
        
        def update(frame):
            t_min = self.t_eval[frame] * 60
            no2 = self.plasma_no2[frame]
            cgmp = self.cgmp_levels[frame]
            vaso = self.vasodilation[frame]
            
            x_data.append(t_min)
            no2_data.append(no2)
            cgmp_data.append(cgmp)
            vaso_data.append(vaso)
            
            line_no2.set_data(x_data, no2_data)
            line_cgmp.set_data(x_data, cgmp_data)
            line_vaso.set_data(x_data, vaso_data)
            
            time_text.set_text(f"Time: {int(t_min)} min")
            conc_text.set_text(f"NO₂⁻: {no2:.2f} µM | cGMP: {cgmp:.1f} | Vasodilation: {vaso:.1f}%")
            return line_no2, line_cgmp, line_vaso, time_text, conc_text
        
        ani = animation.FuncAnimation(
            fig, update, frames=len(self.t_eval),
            init_func=init, blit=True, interval=1000/fps
        )
        
        plt.tight_layout()
        
        # Save animation to a temporary buffer
        buffer = BytesIO()
        ani.save(buffer, format='gif', fps=fps, dpi=100)
        buffer.seek(0)
        
        # Convert to base64 for embedding in HTML
        img_str = base64.b64encode(buffer.read()).decode('utf-8')
        
        # Close the figure to free memory
        plt.close(fig)
        
        return f'<img src="data:image/gif;base64,{img_str}" alt="Nitrite Simulation Animation">'
    
    def get_plot_as_base64(self):
        """Generate a base64 encoded static plot for web display"""
        if self.plasma_no2 is None:
            self.simulate()
            
        fig, ax = self.plot_static(show=False)
        
        # Save figure to a temporary buffer
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        
        # Convert to base64 for embedding in HTML
        img_str = base64.b64encode(buffer.read()).decode('utf-8')
        
        # Close the figure to free memory
        plt.close(fig)
        
        return f'data:image/png;base64,{img_str}'

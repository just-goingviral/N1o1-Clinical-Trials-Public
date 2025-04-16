"""
Core simulation module for nitrite, cGMP and vasodilation dynamics
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
                 dose=30.0         # Dose of NO2- administered (mg)
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
    
    def _rbc_scavenging_rate(self, rbc_count):
        """Calculate RBC scavenging rate based on RBC count"""
        return 0.02 * (rbc_count / 1.0e6)
    
    def _dose_input(self, t, dose=30.0, t_IR=0.0):
        """Model immediate release dose input"""
        if t_IR <= t < (t_IR + 0.083):  # Approximating quick dissolution
            return (dose / 0.083)
        return 0.0
    
    def _no2_ode(self, t, y):
        """ODE model for nitrite concentration"""
        input_flux = self._dose_input(t, dose=self.dose)
        dcdt = input_flux - (self.k_clear + self.k_rbc) * y[0]
        return [dcdt]
    
    def _calculate_cgmp(self, no2_array):
        """Calculate cGMP levels based on nitrite concentration"""
        return 10 * (no2_array / max(no2_array)) if max(no2_array) > 0 else np.zeros_like(no2_array)
    
    def _calculate_vasodilation(self, cgmp_array):
        """Calculate vasodilation percentage based on cGMP levels"""
        return 100 + 50 * (cgmp_array / max(cgmp_array)) if max(cgmp_array) > 0 else 100 * np.ones_like(cgmp_array)
    
    def simulate(self):
        """Run the simulation with current parameters"""
        self.t_eval = np.linspace(0, self.t_max, self.points)
        
        # Solve the ODE system
        sol = solve_ivp(
            lambda t, y: self._no2_ode(t, y), 
            [0, self.t_max], 
            [self.baseline], 
            t_eval=self.t_eval,
            method='RK45',
            rtol=1e-6
        )
        
        self.plasma_no2 = sol.y[0]
        
        # Calculate derived outputs
        self.cgmp_levels = self._calculate_cgmp(self.plasma_no2)
        self.vasodilation = self._calculate_vasodilation(self.cgmp_levels)
        
        # Create a pandas DataFrame with the results
        self.results_df = pd.DataFrame({
            'Time (hours)': self.t_eval,
            'Time (minutes)': self.t_eval * 60,
            'Plasma NO2- (µM)': self.plasma_no2,
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
        ax.set_title('N1O1 Simulation – Plasma NO₂⁻, cGMP, Vasodilation')
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
        ax.set_title('N1O1 Simulation – Plasma NO₂⁻, cGMP, Vasodilation')
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
        ax.set_title('N1O1 Simulation – Plasma NO₂⁻, cGMP, Vasodilation')
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

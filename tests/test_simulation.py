"""
Test suite for the NODynamicsSimulator
Revolutionary pharmacokinetic modeling tests
"""
import pytest
import numpy as np
import pandas as pd
from simulation_core import NODynamicsSimulator

class TestNODynamicsSimulator:
    """Test the nitric oxide dynamics simulation engine"""
    
    def test_basic_simulation(self):
        """Test basic simulation runs without errors"""
        sim = NODynamicsSimulator(
            baseline=0.2,
            peak=4.0,
            t_peak=0.5,
            half_life=0.5,
            t_max=6,
            points=360
        )
        
        results = sim.simulate()
        
        assert isinstance(results, pd.DataFrame)
        assert len(results) == 360
        assert 'Plasma NO2- (µM)' in results.columns
        assert 'cGMP (a.u.)' in results.columns
        assert 'Vasodilation (%)' in results.columns
        
    def test_multi_compartment_model(self):
        """Test multi-compartment pharmacokinetic model"""
        sim = NODynamicsSimulator(dose=30.0, formulation="immediate-release")
        results = sim.simulate()
        
        # Check all compartments are present
        assert 'Plasma NO2- (µM)' in results.columns
        assert 'Tissue NO2- (µM)' in results.columns
        assert 'RBC NO2- (µM)' in results.columns
        assert 'Total Body NO2- (µM)' in results.columns
        assert 'Bioactive NO (a.u.)' in results.columns
        
        # Verify physiological constraints
        assert (results['Plasma NO2- (µM)'] >= 0).all()
        assert (results['Tissue NO2- (µM)'] >= 0).all()
        assert (results['RBC NO2- (µM)'] >= 0).all()
        assert (results['Vasodilation (%)'] >= 100).all()  # Baseline is 100%
        
    def test_extended_release_formulation(self):
        """Test extended-release formulation dynamics"""
        sim_ir = NODynamicsSimulator(dose=30.0, formulation="immediate-release")
        sim_er = NODynamicsSimulator(dose=30.0, formulation="extended-release")
        
        results_ir = sim_ir.simulate()
        results_er = sim_er.simulate()
        
        # Extended release should have lower peak but longer duration
        max_ir = results_ir['Plasma NO2- (µM)'].max()
        max_er = results_er['Plasma NO2- (µM)'].max()
        
        # Time above baseline
        time_above_baseline_ir = (results_ir['Plasma NO2- (µM)'] > 0.3).sum()
        time_above_baseline_er = (results_er['Plasma NO2- (µM)'] > 0.3).sum()
        
        assert max_er < max_ir  # Lower peak for extended release
        assert time_above_baseline_er > time_above_baseline_ir  # Longer duration
        
    def test_multiple_dosing(self):
        """Test multiple dose administration"""
        additional_doses = [
            {'time': 2.0, 'amount': 15.0},  # 2 hours later
            {'time': 4.0, 'amount': 15.0}   # 4 hours later
        ]
        
        sim = NODynamicsSimulator(
            dose=30.0,
            additional_doses=additional_doses,
            t_max=8
        )
        
        results = sim.simulate()
        
        # Check for multiple peaks
        plasma_levels = results['Plasma NO2- (µM)'].values
        
        # Find local maxima (simple approach)
        peaks = []
        for i in range(1, len(plasma_levels) - 1):
            if plasma_levels[i] > plasma_levels[i-1] and plasma_levels[i] > plasma_levels[i+1]:
                peaks.append(i)
        
        # Should have at least 3 peaks (one for each dose)
        assert len(peaks) >= 3
        
    def test_hypoxia_simulation(self):
        """Test hypoxic conditions effect on NO production"""
        sim = NODynamicsSimulator(dose=30.0)
        
        # Normal conditions
        results_normoxia = sim.simulate()
        
        # Hypoxic conditions
        results_hypoxia = sim.simulate_hypoxia(oxygen_saturation=0.8)
        
        # In hypoxia, RBCs should convert more nitrite to NO
        # This should lead to different bioactive NO levels
        normoxia_no = results_normoxia['Bioactive NO (a.u.)'].sum()
        hypoxia_no = results_hypoxia['Bioactive NO (a.u.)'].sum()
        
        assert normoxia_no != hypoxia_no
        
    def test_renal_function_impact(self):
        """Test impact of renal function on clearance"""
        # Normal renal function
        sim_normal = NODynamicsSimulator(dose=30.0, egfr=90.0)
        results_normal = sim_normal.simulate()
        
        # Impaired renal function
        sim_impaired = NODynamicsSimulator(dose=30.0, egfr=30.0)
        results_impaired = sim_impaired.simulate()
        
        # With lower eGFR, clearance should be slower
        # Leading to higher AUC (area under curve)
        auc_normal = np.trapz(results_normal['Plasma NO2- (µM)'], results_normal['Time (hours)'])
        auc_impaired = np.trapz(results_impaired['Plasma NO2- (µM)'], results_impaired['Time (hours)'])
        
        assert auc_impaired > auc_normal
        
    def test_rbc_count_impact(self):
        """Test impact of RBC count on nitrite scavenging"""
        # Normal RBC count
        sim_normal = NODynamicsSimulator(dose=30.0, rbc_count=4.5e6)
        results_normal = sim_normal.simulate()
        
        # Anemic (low RBC count)
        sim_anemic = NODynamicsSimulator(dose=30.0, rbc_count=3.0e6)
        results_anemic = sim_anemic.simulate()
        
        # With fewer RBCs, less scavenging should occur
        # Leading to different RBC compartment levels
        rbc_normal = results_normal['RBC NO2- (µM)'].sum()
        rbc_anemic = results_anemic['RBC NO2- (µM)'].sum()
        
        assert rbc_anemic < rbc_normal
        
    def test_vasodilation_response(self):
        """Test vasodilation calculations"""
        sim = NODynamicsSimulator(dose=30.0)
        results = sim.simulate()
        
        # Vasodilation should correlate with cGMP
        cgmp = results['cGMP (a.u.)'].values
        vasodilation = results['Vasodilation (%)'].values
        
        # Calculate correlation
        correlation = np.corrcoef(cgmp, vasodilation)[0, 1]
        
        assert correlation > 0.9  # Strong positive correlation
        
        # Maximum vasodilation should be reasonable
        assert 100 <= vasodilation.max() <= 200  # 0-100% increase from baseline
        
    def test_export_functionality(self):
        """Test data export capabilities"""
        sim = NODynamicsSimulator(dose=30.0)
        sim.simulate()
        
        # Test CSV export
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            filename = f.name
        
        try:
            exported_file = sim.export_to_csv(filename)
            assert os.path.exists(exported_file)
            
            # Read back and verify
            df_read = pd.read_csv(exported_file)
            assert len(df_read) == sim.points
            assert 'Plasma NO2- (µM)' in df_read.columns
        finally:
            if os.path.exists(filename):
                os.unlink(filename)
                
    def test_visualization_generation(self):
        """Test plot generation capabilities"""
        sim = NODynamicsSimulator(dose=30.0)
        sim.simulate()
        
        # Test base64 plot generation
        base64_plot = sim.get_plot_as_base64()
        assert base64_plot.startswith('data:image/png;base64,')
        
        # Test animation HTML generation
        animation_html = sim.get_animation_html(fps=3)
        assert '<img src="data:image/gif;base64,' in animation_html
        
    def test_dose_response_curve(self):
        """Test dose-response relationship"""
        doses = [10, 20, 30, 40, 50]
        peak_responses = []
        
        for dose in doses:
            sim = NODynamicsSimulator(dose=dose)
            results = sim.simulate()
            peak_responses.append(results['Plasma NO2- (µM)'].max())
        
        # Verify dose-response relationship
        # Higher doses should generally lead to higher peaks
        for i in range(1, len(doses)):
            assert peak_responses[i] >= peak_responses[i-1]
            
    def test_steady_state_achievement(self):
        """Test steady-state with continuous dosing"""
        # Simulate multiple doses to approach steady state
        doses = [{'time': i * 2.0, 'amount': 15.0} for i in range(1, 6)]
        
        sim = NODynamicsSimulator(
            dose=15.0,
            additional_doses=doses,
            t_max=12
        )
        
        results = sim.simulate()
        
        # Check if steady state is approached
        # Last 3 peaks should be similar
        plasma = results['Plasma NO2- (µM)'].values
        time_hours = results['Time (hours)'].values
        
        # Find peaks in last 6 hours
        last_6h_mask = time_hours > 6
        last_plasma = plasma[last_6h_mask]
        
        # Coefficient of variation should be low for steady state
        if len(last_plasma) > 0:
            cv = np.std(last_plasma) / np.mean(last_plasma)
            assert cv < 0.5  # Less than 50% variation

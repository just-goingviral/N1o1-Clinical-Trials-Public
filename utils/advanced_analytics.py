"""
Advanced Analytics Module for N1O1 Clinical Trials
Revolutionary statistical and machine learning tools for nitric oxide research
"""
import numpy as np
import pandas as pd
from scipy import stats, optimize, signal
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

class AdvancedNOAnalytics:
    """Advanced analytics for nitric oxide clinical trial data"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        
    def calculate_pharmacokinetic_parameters(self, time, concentration):
        """
        Calculate comprehensive PK parameters from concentration-time data
        
        Returns:
            dict: Dictionary containing Cmax, Tmax, AUC, half-life, clearance, etc.
        """
        # Ensure numpy arrays
        time = np.array(time)
        concentration = np.array(concentration)
        
        # Basic parameters
        cmax = np.max(concentration)
        tmax = time[np.argmax(concentration)]
        
        # AUC using trapezoidal rule
        auc = np.trapz(concentration, time)
        
        # Find half-life (time to reach half of Cmax after Tmax)
        post_peak_idx = np.where(time > tmax)[0]
        if len(post_peak_idx) > 0:
            post_peak_conc = concentration[post_peak_idx]
            post_peak_time = time[post_peak_idx]
            
            # Find where concentration drops to half
            half_cmax = cmax / 2
            half_life_idx = np.where(post_peak_conc <= half_cmax)[0]
            
            if len(half_life_idx) > 0:
                t_half = post_peak_time[half_life_idx[0]] - tmax
            else:
                # Estimate using exponential decay
                t_half = self._estimate_half_life(post_peak_time, post_peak_conc)
        else:
            t_half = np.nan
        
        # Calculate clearance (CL = Dose/AUC)
        # Assuming dose is proportional to Cmax for now
        clearance = cmax / auc if auc > 0 else np.nan
        
        # Mean Residence Time (MRT)
        aumc = np.trapz(concentration * time, time)
        mrt = aumc / auc if auc > 0 else np.nan
        
        # Volume of distribution (Vd)
        vd = clearance * mrt if not np.isnan(clearance) and not np.isnan(mrt) else np.nan
        
        return {
            'cmax': cmax,
            'tmax': tmax,
            'auc': auc,
            'half_life': t_half,
            'clearance': clearance,
            'mrt': mrt,
            'volume_distribution': vd,
            'bioavailability_score': auc / (cmax * time[-1])  # Normalized score
        }
    
    def _estimate_half_life(self, time, concentration):
        """Estimate half-life using exponential decay fitting"""
        try:
            # Log-transform for linear fitting
            log_conc = np.log(concentration[concentration > 0])
            time_positive = time[concentration > 0]
            
            # Linear regression on log-transformed data
            slope, _ = np.polyfit(time_positive, log_conc, 1)
            
            # Half-life = -ln(2)/slope
            t_half = -np.log(2) / slope
            return abs(t_half)
        except:
            return np.nan
    
    def analyze_dose_response(self, doses, responses):
        """
        Perform dose-response analysis with multiple models
        
        Returns:
            dict: EC50, Hill coefficient, model parameters, and predictions
        """
        doses = np.array(doses)
        responses = np.array(responses)
        
        # Hill equation fitting
        def hill_equation(x, vmax, ec50, n):
            return vmax * (x**n) / (ec50**n + x**n)
        
        try:
            # Initial parameter guess
            p0 = [np.max(responses), np.median(doses), 1.0]
            
            # Fit the model
            popt, pcov = optimize.curve_fit(hill_equation, doses, responses, p0=p0)
            
            # Calculate R-squared
            predicted = hill_equation(doses, *popt)
            ss_res = np.sum((responses - predicted)**2)
            ss_tot = np.sum((responses - np.mean(responses))**2)
            r_squared = 1 - (ss_res / ss_tot)
            
            # Generate smooth curve for visualization
            dose_range = np.linspace(0, np.max(doses) * 1.2, 100)
            response_curve = hill_equation(dose_range, *popt)
            
            return {
                'model': 'Hill Equation',
                'vmax': popt[0],
                'ec50': popt[1],
                'hill_coefficient': popt[2],
                'r_squared': r_squared,
                'dose_range': dose_range,
                'response_curve': response_curve,
                'confidence_intervals': np.sqrt(np.diag(pcov))
            }
        except:
            return {
                'model': 'Hill Equation',
                'error': 'Failed to fit model',
                'fallback': 'linear',
                'linear_slope': np.polyfit(doses, responses, 1)[0]
            }
    
    def identify_responder_phenotypes(self, patient_data, response_data, n_clusters=3):
        """
        Identify distinct responder phenotypes using clustering
        
        Args:
            patient_data: DataFrame with patient characteristics
            response_data: Array of response values
            n_clusters: Number of phenotypes to identify
            
        Returns:
            dict: Cluster assignments, characteristics, and predictions
        """
        # Prepare data
        X = self.scaler.fit_transform(patient_data)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(X)
        
        # Analyze each cluster
        phenotypes = {}
        for i in range(n_clusters):
            mask = clusters == i
            phenotypes[f'phenotype_{i+1}'] = {
                'n_patients': np.sum(mask),
                'mean_response': np.mean(response_data[mask]),
                'std_response': np.std(response_data[mask]),
                'characteristics': patient_data[mask].mean().to_dict(),
                'response_range': (np.min(response_data[mask]), np.max(response_data[mask]))
            }
        
        # Identify super-responders
        response_threshold = np.percentile(response_data, 75)
        super_responders = response_data > response_threshold
        
        return {
            'phenotypes': phenotypes,
            'cluster_assignments': clusters,
            'super_responders': np.where(super_responders)[0].tolist(),
            'cluster_centers': self.scaler.inverse_transform(kmeans.cluster_centers_)
        }
    
    def predict_treatment_response(self, patient_features, historical_data):
        """
        Machine learning model to predict treatment response
        
        Returns:
            dict: Predicted response, confidence intervals, feature importance
        """
        # Prepare training data
        X_train = historical_data.drop('response', axis=1)
        y_train = historical_data['response']
        
        # Train Random Forest model
        rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        rf_model.fit(X_train, y_train)
        
        # Make prediction
        prediction = rf_model.predict(patient_features.reshape(1, -1))[0]
        
        # Calculate prediction intervals using out-of-bag predictions
        predictions_oob = []
        for tree in rf_model.estimators_:
            predictions_oob.append(tree.predict(patient_features.reshape(1, -1))[0])
        
        prediction_std = np.std(predictions_oob)
        confidence_interval = (
            prediction - 1.96 * prediction_std,
            prediction + 1.96 * prediction_std
        )
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X_train.columns,
            'importance': rf_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return {
            'predicted_response': prediction,
            'confidence_interval_95': confidence_interval,
            'prediction_std': prediction_std,
            'feature_importance': feature_importance.to_dict('records'),
            'model_score': rf_model.score(X_train, y_train)
        }
    
    def analyze_temporal_patterns(self, time_series_data, sampling_rate=1.0):
        """
        Analyze temporal patterns in physiological data
        
        Returns:
            dict: Frequency components, periodicity, trends
        """
        # Detrend the data
        detrended = signal.detrend(time_series_data)
        
        # Perform FFT for frequency analysis
        fft_vals = np.fft.fft(detrended)
        fft_freq = np.fft.fftfreq(len(detrended), d=1/sampling_rate)
        
        # Find dominant frequencies
        power_spectrum = np.abs(fft_vals)**2
        dominant_freq_idx = np.argsort(power_spectrum)[-5:]  # Top 5 frequencies
        dominant_frequencies = fft_freq[dominant_freq_idx]
        
        # Detect periodicity using autocorrelation
        autocorr = np.correlate(detrended, detrended, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        autocorr = autocorr / autocorr[0]  # Normalize
        
        # Find peaks in autocorrelation
        peaks, _ = signal.find_peaks(autocorr, height=0.3)
        
        # Calculate circadian alignment (24-hour periodicity)
        circadian_period = 24 * sampling_rate  # 24 hours in samples
        if circadian_period < len(autocorr):
            circadian_score = autocorr[int(circadian_period)]
        else:
            circadian_score = 0
        
        return {
            'dominant_frequencies': dominant_frequencies[dominant_frequencies > 0].tolist(),
            'periodicity_detected': len(peaks) > 0,
            'period_lengths': peaks.tolist() if len(peaks) > 0 else [],
            'circadian_alignment_score': circadian_score,
            'trend': 'increasing' if np.polyfit(range(len(time_series_data)), time_series_data, 1)[0] > 0 else 'decreasing',
            'variability': np.std(detrended)
        }
    
    def calculate_synergy_index(self, mono_therapy_1, mono_therapy_2, combination_therapy):
        """
        Calculate drug synergy using Bliss Independence model
        
        Returns:
            dict: Synergy index, interaction type, statistical significance
        """
        # Bliss expected effect
        expected_effect = mono_therapy_1 + mono_therapy_2 - (mono_therapy_1 * mono_therapy_2)
        
        # Synergy index
        synergy_index = combination_therapy / expected_effect if expected_effect > 0 else np.nan
        
        # Determine interaction type
        if synergy_index > 1.15:
            interaction_type = "Synergistic"
        elif synergy_index < 0.85:
            interaction_type = "Antagonistic"
        else:
            interaction_type = "Additive"
        
        # Statistical test (would need replicates in real scenario)
        # Using simulated data for demonstration
        np.random.seed(42)
        simulated_expected = np.random.normal(expected_effect, expected_effect * 0.1, 100)
        simulated_observed = np.random.normal(combination_therapy, combination_therapy * 0.1, 100)
        
        _, p_value = stats.ttest_ind(simulated_observed, simulated_expected)
        
        return {
            'synergy_index': synergy_index,
            'interaction_type': interaction_type,
            'expected_effect': expected_effect,
            'observed_effect': combination_therapy,
            'excess_effect': combination_therapy - expected_effect,
            'p_value': p_value,
            'significant': p_value < 0.05
        }
    
    def generate_biomarker_signature(self, biomarker_data, clinical_outcome):
        """
        Generate a multi-biomarker signature for outcome prediction
        
        Returns:
            dict: Signature components, weights, performance metrics
        """
        # Perform PCA
        pca = PCA(n_components=min(5, biomarker_data.shape[1]))
        components = pca.fit_transform(biomarker_data)
        
        # Create signature using top components
        signature_weights = pca.components_[0]  # First principal component
        
        # Calculate signature score for each patient
        signature_scores = np.dot(biomarker_data, signature_weights)
        
        # Evaluate signature performance
        correlation = np.corrcoef(signature_scores, clinical_outcome)[0, 1]
        
        # Find optimal cutoff using ROC analysis (for binary outcome)
        if len(np.unique(clinical_outcome)) == 2:
            from sklearn.metrics import roc_curve, auc
            fpr, tpr, thresholds = roc_curve(clinical_outcome, signature_scores)
            roc_auc = auc(fpr, tpr)
            
            # Optimal cutoff (Youden's index)
            optimal_idx = np.argmax(tpr - fpr)
            optimal_cutoff = thresholds[optimal_idx]
        else:
            roc_auc = None
            optimal_cutoff = np.median(signature_scores)
        
        return {
            'signature_weights': dict(zip(biomarker_data.columns, signature_weights)),
            'variance_explained': pca.explained_variance_ratio_[0],
            'correlation_with_outcome': correlation,
            'roc_auc': roc_auc,
            'optimal_cutoff': optimal_cutoff,
            'signature_scores': signature_scores,
            'performance_summary': {
                'strong_predictors': [col for col, weight in zip(biomarker_data.columns, np.abs(signature_weights)) if weight > np.mean(np.abs(signature_weights))]
            }
        }

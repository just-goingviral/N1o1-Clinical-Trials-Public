"""
Real-time Monitoring Module for N1O1 Clinical Trials
Revolutionary real-time data streaming and alerting system
"""
import asyncio
import numpy as np
from datetime import datetime, timedelta
from collections import deque
import json
from typing import Dict, List, Callable, Optional

class RealTimeMonitor:
    """Real-time monitoring system for clinical trial data"""
    
    def __init__(self, buffer_size: int = 1000):
        self.buffer_size = buffer_size
        self.data_buffers = {}
        self.alert_thresholds = {}
        self.alert_callbacks = []
        self.trend_analyzers = {}
        self.is_running = False
        
    def add_metric(self, metric_name: str, 
                   lower_threshold: Optional[float] = None,
                   upper_threshold: Optional[float] = None,
                   trend_window: int = 100):
        """Add a metric to monitor with optional thresholds"""
        self.data_buffers[metric_name] = deque(maxlen=self.buffer_size)
        self.alert_thresholds[metric_name] = {
            'lower': lower_threshold,
            'upper': upper_threshold
        }
        self.trend_analyzers[metric_name] = TrendAnalyzer(window_size=trend_window)
        
    def register_alert_callback(self, callback: Callable):
        """Register a callback function for alerts"""
        self.alert_callbacks.append(callback)
        
    async def process_data_point(self, metric_name: str, value: float, timestamp: Optional[datetime] = None):
        """Process a new data point for a metric"""
        if metric_name not in self.data_buffers:
            raise ValueError(f"Metric {metric_name} not registered")
            
        timestamp = timestamp or datetime.now()
        
        # Store data point
        data_point = {
            'value': value,
            'timestamp': timestamp,
            'anomaly_score': 0.0
        }
        
        # Check for anomalies
        anomaly_score = self._calculate_anomaly_score(metric_name, value)
        data_point['anomaly_score'] = anomaly_score
        
        # Add to buffer
        self.data_buffers[metric_name].append(data_point)
        
        # Check thresholds
        alerts = self._check_thresholds(metric_name, value)
        
        # Analyze trends
        trend_info = self.trend_analyzers[metric_name].analyze(value)
        
        # Check for critical patterns
        pattern_alerts = self._detect_critical_patterns(metric_name)
        alerts.extend(pattern_alerts)
        
        # Trigger alerts if any
        if alerts:
            await self._trigger_alerts(metric_name, value, alerts, timestamp)
            
        return {
            'processed': True,
            'anomaly_score': anomaly_score,
            'trend': trend_info,
            'alerts': alerts
        }
    
    def _calculate_anomaly_score(self, metric_name: str, value: float) -> float:
        """Calculate anomaly score using statistical methods"""
        buffer = self.data_buffers[metric_name]
        
        if len(buffer) < 10:
            return 0.0
            
        # Get recent values
        recent_values = [dp['value'] for dp in buffer]
        
        # Calculate statistics
        mean = np.mean(recent_values)
        std = np.std(recent_values)
        
        if std == 0:
            return 0.0
            
        # Z-score based anomaly
        z_score = abs((value - mean) / std)
        
        # Convert to 0-1 scale
        anomaly_score = min(z_score / 4.0, 1.0)  # Cap at 4 standard deviations
        
        return anomaly_score
    
    def _check_thresholds(self, metric_name: str, value: float) -> List[Dict]:
        """Check if value exceeds defined thresholds"""
        alerts = []
        thresholds = self.alert_thresholds[metric_name]
        
        if thresholds['lower'] is not None and value < thresholds['lower']:
            alerts.append({
                'type': 'threshold_breach',
                'severity': 'high',
                'message': f'{metric_name} below lower threshold: {value:.2f} < {thresholds["lower"]:.2f}'
            })
            
        if thresholds['upper'] is not None and value > thresholds['upper']:
            alerts.append({
                'type': 'threshold_breach',
                'severity': 'high',
                'message': f'{metric_name} above upper threshold: {value:.2f} > {thresholds["upper"]:.2f}'
            })
            
        return alerts
    
    def _detect_critical_patterns(self, metric_name: str) -> List[Dict]:
        """Detect critical patterns in the data"""
        alerts = []
        buffer = self.data_buffers[metric_name]
        
        if len(buffer) < 10:
            return alerts
            
        recent_values = [dp['value'] for dp in list(buffer)[-10:]]
        
        # Rapid change detection
        if len(recent_values) >= 5:
            recent_change = abs(recent_values[-1] - recent_values[-5])
            avg_value = np.mean(recent_values)
            
            if avg_value > 0 and recent_change / avg_value > 0.5:  # 50% change
                alerts.append({
                    'type': 'rapid_change',
                    'severity': 'medium',
                    'message': f'Rapid change detected in {metric_name}: {recent_change:.2f} in 5 readings'
                })
        
        # Sustained high/low detection
        if all(dp['anomaly_score'] > 0.7 for dp in list(buffer)[-5:]):
            alerts.append({
                'type': 'sustained_anomaly',
                'severity': 'high',
                'message': f'Sustained anomaly in {metric_name}'
            })
            
        return alerts
    
    async def _trigger_alerts(self, metric_name: str, value: float, 
                            alerts: List[Dict], timestamp: datetime):
        """Trigger alert callbacks"""
        alert_data = {
            'metric_name': metric_name,
            'value': value,
            'timestamp': timestamp.isoformat(),
            'alerts': alerts
        }
        
        # Call all registered callbacks
        for callback in self.alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(alert_data)
                else:
                    callback(alert_data)
            except Exception as e:
                print(f"Error in alert callback: {e}")
    
    def get_current_status(self) -> Dict:
        """Get current status of all monitored metrics"""
        status = {}
        
        for metric_name, buffer in self.data_buffers.items():
            if len(buffer) == 0:
                status[metric_name] = {
                    'current_value': None,
                    'status': 'no_data'
                }
                continue
                
            latest = buffer[-1]
            recent_values = [dp['value'] for dp in list(buffer)[-10:]]
            
            status[metric_name] = {
                'current_value': latest['value'],
                'timestamp': latest['timestamp'].isoformat(),
                'anomaly_score': latest['anomaly_score'],
                'trend': self.trend_analyzers[metric_name].get_trend(),
                'statistics': {
                    'mean': np.mean(recent_values),
                    'std': np.std(recent_values),
                    'min': np.min(recent_values),
                    'max': np.max(recent_values)
                },
                'status': self._get_metric_status(metric_name, latest)
            }
            
        return status
    
    def _get_metric_status(self, metric_name: str, latest_point: Dict) -> str:
        """Determine overall status of a metric"""
        if latest_point['anomaly_score'] > 0.8:
            return 'critical'
        elif latest_point['anomaly_score'] > 0.5:
            return 'warning'
        else:
            return 'normal'
    
    def export_buffer_data(self, metric_name: str, 
                          start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None) -> List[Dict]:
        """Export buffered data for analysis"""
        if metric_name not in self.data_buffers:
            return []
            
        buffer = self.data_buffers[metric_name]
        data = list(buffer)
        
        # Filter by time if specified
        if start_time:
            data = [dp for dp in data if dp['timestamp'] >= start_time]
        if end_time:
            data = [dp for dp in data if dp['timestamp'] <= end_time]
            
        return data


class TrendAnalyzer:
    """Analyze trends in real-time data"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.values = deque(maxlen=window_size)
        
    def analyze(self, value: float) -> Dict:
        """Analyze trend with new value"""
        self.values.append(value)
        
        if len(self.values) < 3:
            return {'trend': 'insufficient_data', 'strength': 0.0}
            
        # Calculate trend using linear regression
        x = np.arange(len(self.values))
        y = np.array(self.values)
        
        # Fit linear trend
        coeffs = np.polyfit(x, y, 1)
        slope = coeffs[0]
        
        # Calculate R-squared for trend strength
        y_pred = np.polyval(coeffs, x)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Determine trend direction
        if abs(slope) < 0.001:
            trend = 'stable'
        elif slope > 0:
            trend = 'increasing'
        else:
            trend = 'decreasing'
            
        return {
            'trend': trend,
            'slope': slope,
            'strength': abs(r_squared),
            'prediction': self._predict_next(coeffs)
        }
    
    def _predict_next(self, coeffs: np.ndarray) -> float:
        """Predict next value based on trend"""
        next_x = len(self.values)
        return float(np.polyval(coeffs, next_x))
    
    def get_trend(self) -> str:
        """Get current trend direction"""
        if len(self.values) < 3:
            return 'unknown'
            
        trend_info = self.analyze(self.values[-1])
        return trend_info['trend']


class ClinicalEventDetector:
    """Detect specific clinical events in real-time"""
    
    def __init__(self):
        self.event_patterns = {
            'vasodilation_response': self._detect_vasodilation,
            'peak_concentration': self._detect_peak,
            'steady_state': self._detect_steady_state,
            'adverse_event': self._detect_adverse_event
        }
        
    def detect_events(self, metric_data: Dict[str, List[float]]) -> List[Dict]:
        """Detect clinical events from metric data"""
        events = []
        
        for event_type, detector in self.event_patterns.items():
            detected = detector(metric_data)
            if detected:
                events.append({
                    'type': event_type,
                    'timestamp': datetime.now(),
                    'details': detected
                })
                
        return events
    
    def _detect_vasodilation(self, metric_data: Dict[str, List[float]]) -> Optional[Dict]:
        """Detect vasodilation response pattern"""
        if 'blood_pressure' not in metric_data or len(metric_data['blood_pressure']) < 10:
            return None
            
        bp_values = metric_data['blood_pressure'][-10:]
        
        # Check for sustained decrease
        if all(bp_values[i] <= bp_values[i-1] for i in range(1, len(bp_values))):
            decrease = bp_values[0] - bp_values[-1]
            if decrease > 5:  # 5 mmHg decrease
                return {
                    'magnitude': decrease,
                    'duration': len(bp_values),
                    'pattern': 'sustained_decrease'
                }
                
        return None
    
    def _detect_peak(self, metric_data: Dict[str, List[float]]) -> Optional[Dict]:
        """Detect peak concentration"""
        if 'no2_concentration' not in metric_data or len(metric_data['no2_concentration']) < 5:
            return None
            
        values = metric_data['no2_concentration']
        
        # Simple peak detection
        for i in range(1, len(values) - 1):
            if values[i] > values[i-1] and values[i] > values[i+1]:
                return {
                    'peak_value': values[i],
                    'peak_index': i,
                    'confirmed': True
                }
                
        return None
    
    def _detect_steady_state(self, metric_data: Dict[str, List[float]]) -> Optional[Dict]:
        """Detect steady state achievement"""
        if 'no2_concentration' not in metric_data or len(metric_data['no2_concentration']) < 20:
            return None
            
        values = metric_data['no2_concentration'][-20:]
        
        # Check coefficient of variation
        cv = np.std(values) / np.mean(values) if np.mean(values) > 0 else 1.0
        
        if cv < 0.1:  # Less than 10% variation
            return {
                'achieved': True,
                'mean_level': np.mean(values),
                'cv': cv
            }
            
        return None
    
    def _detect_adverse_event(self, metric_data: Dict[str, List[float]]) -> Optional[Dict]:
        """Detect potential adverse events"""
        alerts = []
        
        # Check multiple metrics for adverse patterns
        if 'heart_rate' in metric_data and len(metric_data['heart_rate']) > 5:
            hr_values = metric_data['heart_rate'][-5:]
            if any(hr > 100 or hr < 50 for hr in hr_values):
                alerts.append('abnormal_heart_rate')
                
        if 'blood_pressure' in metric_data and len(metric_data['blood_pressure']) > 5:
            bp_values = metric_data['blood_pressure'][-5:]
            if any(bp < 90 for bp in bp_values):
                alerts.append('hypotension')
                
        if alerts:
            return {
                'indicators': alerts,
                'severity': 'moderate' if len(alerts) == 1 else 'high'
            }
            
        return None

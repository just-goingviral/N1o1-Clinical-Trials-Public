"""
Database models for NO Dynamics Simulator
Author: Dustin Salinas
License: MIT
"""

from datetime import datetime
from app import db

class SimulationRun(db.Model):
    """
    Model for storing simulation run data
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, default="Untitled Simulation")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Simulation parameters
    baseline = db.Column(db.Float, nullable=False)
    peak = db.Column(db.Float, nullable=False)
    t_peak = db.Column(db.Float, nullable=False)
    half_life = db.Column(db.Float, nullable=False)
    t_max = db.Column(db.Float, nullable=False)
    points = db.Column(db.Integer, nullable=False)
    egfr = db.Column(db.Float, nullable=False)
    rbc_count = db.Column(db.Float, nullable=False)
    dose = db.Column(db.Float, nullable=False)
    
    # Key metrics
    no2_peak_value = db.Column(db.Float)
    no2_time_to_peak = db.Column(db.Float)
    cgmp_peak_value = db.Column(db.Float)
    cgmp_time_to_peak = db.Column(db.Float)
    vaso_peak_value = db.Column(db.Float)
    vaso_time_to_peak = db.Column(db.Float)
    no2_auc = db.Column(db.Float)
    
    # Relationships
    data_points = db.relationship('SimulationDataPoint', back_populates='simulation', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<SimulationRun {self.name} ({self.created_at})>'
        
    def to_dict(self):
        """Convert simulation run to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'parameters': {
                'baseline': self.baseline,
                'peak': self.peak,
                't_peak': self.t_peak,
                'half_life': self.half_life,
                't_max': self.t_max,
                'points': self.points,
                'egfr': self.egfr,
                'rbc_count': self.rbc_count,
                'dose': self.dose
            },
            'metrics': {
                'no2_peak': self.no2_peak_value,
                'no2_time_to_peak': self.no2_time_to_peak,
                'cgmp_peak': self.cgmp_peak_value,
                'cgmp_time_to_peak': self.cgmp_time_to_peak,
                'vaso_peak': self.vaso_peak_value,
                'vaso_time_to_peak': self.vaso_time_to_peak,
                'no2_auc': self.no2_auc
            }
        }


class SimulationDataPoint(db.Model):
    """
    Model for storing individual data points from a simulation
    """
    id = db.Column(db.Integer, primary_key=True)
    simulation_id = db.Column(db.Integer, db.ForeignKey('simulation_run.id'), nullable=False)
    time_minutes = db.Column(db.Float, nullable=False)
    no2_concentration = db.Column(db.Float, nullable=False)
    cgmp_level = db.Column(db.Float, nullable=False)
    vasodilation_percent = db.Column(db.Float, nullable=False)
    
    # Relationship
    simulation = db.relationship('SimulationRun', back_populates='data_points')
    
    def __repr__(self):
        return f'<DataPoint t={self.time_minutes} NO2={self.no2_concentration}>'
        
    def to_dict(self):
        """Convert data point to dictionary"""
        return {
            'id': self.id,
            'time_minutes': self.time_minutes,
            'no2_concentration': self.no2_concentration,
            'cgmp_level': self.cgmp_level,
            'vasodilation_percent': self.vasodilation_percent
        }


class ExperimentalData(db.Model):
    """
    Model for storing experimental data uploaded by users
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    data_points = db.relationship('ExperimentalDataPoint', back_populates='dataset', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ExperimentalData {self.name}>'
        
    def to_dict(self):
        """Convert experimental dataset to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'uploaded_at': self.uploaded_at.isoformat()
        }


class ExperimentalDataPoint(db.Model):
    """
    Model for storing individual experimental data points
    """
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('experimental_data.id'), nullable=False)
    time_minutes = db.Column(db.Float, nullable=False)
    no2_concentration = db.Column(db.Float, nullable=False)
    
    # Relationship
    dataset = db.relationship('ExperimentalData', back_populates='data_points')
    
    def __repr__(self):
        return f'<ExperimentalDataPoint t={self.time_minutes} NO2={self.no2_concentration}>'
        
    def to_dict(self):
        """Convert experimental data point to dictionary"""
        return {
            'id': self.id,
            'time_minutes': self.time_minutes,
            'no2_concentration': self.no2_concentration
        }
"""
Database models for Nitrite Dynamics
A clinical simulator for plasma nitrite levels
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB

db = SQLAlchemy()

class Patient(db.Model):
    """Patient model for clinical trial participants"""
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    age = db.Column(db.Integer, nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)
    baseline_no2 = db.Column(db.Float, nullable=False)  # μM
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    doses = db.relationship('SupplementDose', backref='patient', lazy=True, cascade='all, delete-orphan')
    no2_measurements = db.relationship('NO2Level', backref='patient', lazy=True, cascade='all, delete-orphan')
    simulations = db.relationship('Simulation', backref='patient', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Patient #{self.id}: {self.name or "Unnamed"}, {self.age} y/o>'

    def to_dict(self):
        """Convert patient data to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'weight_kg': self.weight_kg,
            'baseline_no2': self.baseline_no2,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SupplementDose(db.Model):
    """Model for storing supplement dosing information"""
    __tablename__ = 'supplement_doses'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    supplement = db.Column(db.String(100), nullable=False)  # e.g., "N1O1 Lozenge", "NO Beetz"
    dose_mg = db.Column(db.Float, nullable=False)
    time_given = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Dose: {self.supplement}, {self.dose_mg}mg at {self.time_given}>'

    def to_dict(self):
        """Convert dose data to dictionary"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'supplement': self.supplement,
            'dose_mg': self.dose_mg,
            'time_given': self.time_given.isoformat() if self.time_given else None,
            'notes': self.notes
        }


class NO2Level(db.Model):
    """Model for storing nitrite level measurements"""
    __tablename__ = 'no2_levels'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    time_after_dose = db.Column(db.Float, nullable=False)  # minutes
    level_um = db.Column(db.Float, nullable=False)  # μM
    measured_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<NO2 Level: {self.level_um}μM at t+{self.time_after_dose}min>'

    def to_dict(self):
        """Convert NO2 level data to dictionary"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'time_after_dose': self.time_after_dose,
            'level_um': self.level_um,
            'measured_at': self.measured_at.isoformat() if self.measured_at else None
        }


class Simulation(db.Model):
    """Model for storing simulation results"""
    __tablename__ = 'simulations'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    model_type = db.Column(db.String(100), nullable=False)  # e.g., "HillTau", "1-compartment PK"
    parameters = db.Column(JSONB, nullable=False)  # model-specific parameters
    result_curve = db.Column(JSONB, nullable=False)  # time vs. nitrite level
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Simulation: {self.model_type} for Patient #{self.patient_id}>'

    def to_dict(self):
        """Convert simulation data to dictionary"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'model_type': self.model_type,
            'parameters': self.parameters,
            'result_curve': self.result_curve,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'notes': self.notes
        }


class ChatSession(db.Model):
    """Model for storing chat sessions"""
    __tablename__ = 'chat_sessions'

    id = db.Column(db.String(36), primary_key=True)  # UUID as string
    user_identifier = db.Column(db.String(100), nullable=False, index=True)  # IP address or user ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages = db.relationship('ChatMessage', backref='session', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ChatSession: {self.id} for {self.user_identifier}>'

    def to_dict(self):
        """Convert chat session to dictionary"""
        return {
            'id': self.id,
            'user_identifier': self.user_identifier,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'messages': [msg.to_dict() for msg in self.messages]
        }


class ChatMessage(db.Model):
    """Model for storing chat messages"""
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('chat_sessions.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    attachment = db.Column(JSONB, nullable=True)  # For storing any file attachments

    def __repr__(self):
        return f'<ChatMessage: {self.role} at {self.timestamp}>'

    def to_dict(self):
        """Convert chat message to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'attachment': self.attachment
        }

class ChatHistory(db.Model):
    """Model for storing chat conversation history"""
    __tablename__ = 'chat_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=True)  # For logged-in users
    session_id = db.Column(db.String(100), nullable=False)  # For anonymous users
    messages = db.Column(JSONB, nullable=False, default=list)  # Array of message objects
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<ChatHistory #{self.id}: {self.user_id or self.session_id}>'

    def to_dict(self):
        """Convert chat history to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'messages': self.messages,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
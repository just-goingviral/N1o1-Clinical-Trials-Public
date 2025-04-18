"""
Patient routes for Nitrite Dynamics application
"""
from flask import Blueprint, jsonify, request
from models import db, Patient

patient_bp = Blueprint('patients', __name__, url_prefix='/patients')

@patient_bp.route('/', methods=['GET'])
def get_patients():
    """Get all patients"""
    try:
        patients = Patient.query.all()
        return jsonify({
            'status': 'success',
            'data': [patient.to_dict() for patient in patients]
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@patient_bp.route('/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Get a specific patient"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        return jsonify({
            'status': 'success',
            'data': patient.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
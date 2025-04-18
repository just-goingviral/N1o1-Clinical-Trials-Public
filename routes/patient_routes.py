
"""
Patient management routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, Patient

patient_bp = Blueprint('patients', __name__, url_prefix='/patients')

@patient_bp.route('/', methods=['GET'])
def list_patients():
    """Display list of all patients"""
    try:
        patients = Patient.query.all()
        return render_template('patients_table.html', patients=patients)
    except Exception as e:
        import logging
        logging.error(f"Database error in list_patients: {str(e)}")
        error_message = "Unable to retrieve patient data. Please check the database connection."
        return render_template('patients_table.html', patients=[], error=error_message)

@patient_bp.route('/new', methods=['GET', 'POST'])
def new_patient():
    """Create a new patient record"""
    if request.method == 'POST':
        try:
            # Extract form data
            name = request.form.get('name')
            age = int(request.form.get('age'))
            weight_kg = float(request.form.get('weight_kg'))
            baseline_no2 = float(request.form.get('baseline_no2', 0.2))
            notes = request.form.get('notes', '')
            
            # Create new patient
            new_patient = Patient(
                name=name,
                age=age,
                weight_kg=weight_kg,
                baseline_no2=baseline_no2,
                notes=notes
            )
            
            # Save to database
            db.session.add(new_patient)
            db.session.commit()
            
            # Redirect to patient list
            return redirect(url_for('patients.list_patients'))
            
        except Exception as e:
            error_message = f"Error creating patient: {str(e)}"
            return render_template('patient_form.html', error=error_message)
    
    # GET request - show the form
    return render_template('patient_form.html')

@patient_bp.route('/<int:patient_id>', methods=['GET'])
def view_patient(patient_id):
    """Display patient details and simulations"""
    patient = Patient.query.get_or_404(patient_id)
    
    # Get patient's simulations
    simulations = patient.simulations.order_by(db.desc('created_at')).all()
    
    return render_template('patient_view.html', patient=patient, simulations=simulations)

@patient_bp.route('/<int:patient_id>/edit', methods=['GET', 'POST'])
def edit_patient(patient_id):
    """Edit a patient record"""
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        try:
            # Update patient data
            patient.name = request.form.get('name')
            patient.age = int(request.form.get('age'))
            patient.weight_kg = float(request.form.get('weight_kg'))
            patient.baseline_no2 = float(request.form.get('baseline_no2'))
            patient.notes = request.form.get('notes', '')
            
            # Save changes
            db.session.commit()
            
            # Redirect to patient view
            return redirect(url_for('patients.view_patient', patient_id=patient.id))
            
        except Exception as e:
            error_message = f"Error updating patient: {str(e)}"
            return render_template('patient_form.html', patient=patient, error=error_message)
    
    # GET request - show form with patient data
    return render_template('patient_form.html', patient=patient)

@patient_bp.route('/<int:patient_id>/delete', methods=['POST'])
def delete_patient(patient_id):
    """Delete a patient record"""
    patient = Patient.query.get_or_404(patient_id)
    
    try:
        # Delete the patient
        db.session.delete(patient)
        db.session.commit()
        
        # Redirect to patient list
        return redirect(url_for('patients.list_patients'))
        
    except Exception as e:
        error_message = f"Error deleting patient: {str(e)}"
        return render_template('patient_view.html', patient=patient, error=error_message)

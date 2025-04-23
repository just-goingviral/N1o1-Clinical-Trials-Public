"""
Patient management routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, Patient
import pandas as pd
import os
import uuid
import logging
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

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
            assess_trial_eligibility(new_patient.id) #Added eligibility assessment

            # Use flash message to indicate success
            flash('Patient created successfully!', 'success')

            # Redirect to patient list using url_for with _external=True to avoid redirect loops
            return redirect(url_for('patients.list_patients', _external=True))

        except Exception as e:
            import traceback
            traceback.print_exc()
            error_message = f"Error creating patient: {str(e)}"
            return render_template('patient_form.html', error=error_message)

    # GET request - show the form
    return render_template('patient_form.html')

@patient_bp.route('/<int:patient_id>', methods=['GET'])
def view_patient(patient_id):
    """Display patient details and simulations"""
    patient = Patient.query.get_or_404(patient_id)

    # Get patient's simulations - sort them by created_at in descending order
    from sqlalchemy import desc
    from models import Simulation

    simulations = Simulation.query.filter_by(patient_id=patient_id).order_by(desc('created_at')).all()

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

@patient_bp.route('/import', methods=['GET', 'POST'])
def import_patients():
    """Import patients from Excel file"""
    if request.method == 'POST':
        # Check if file is present
        if 'file' not in request.files:
            return render_template('patients_import.html', error='No file selected')

        file = request.files['file']

        # Check if filename is empty
        if file.filename == '':
            return render_template('patients_import.html', error='No file selected')

        # Validate file format (xlsx or csv)
        if not file.filename.lower().endswith(('.xlsx', '.csv')):
            return render_template('patients_import.html', error='Invalid file format. Please upload an Excel (.xlsx) or CSV file')

        try:
            # Read the file
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)

            # Validate required columns
            required_columns = ['age', 'weight_kg', 'baseline_no2']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                return render_template('patients_import.html', 
                                    error=f"Missing required columns: {', '.join(missing_columns)}")

            # Process each row and create patients
            patients_created = 0
            patients_skipped = 0
            errors = []

            for index, row in df.iterrows():
                try:
                    # Extract values, using empty string for missing optional fields
                    name = row.get('name', '') if pd.notna(row.get('name', '')) else ''
                    age = int(row['age']) if pd.notna(row['age']) else None
                    weight_kg = float(row['weight_kg']) if pd.notna(row['weight_kg']) else None
                    baseline_no2 = float(row['baseline_no2']) if pd.notna(row['baseline_no2']) else None
                    notes = row.get('notes', '') if pd.notna(row.get('notes', '')) else ''

                    # Validate required fields
                    if age is None or weight_kg is None or baseline_no2 is None:
                        patients_skipped += 1
                        errors.append(f"Row {index+2}: Missing required data")
                        continue

                    # Create new patient
                    patient = Patient(
                        name=name,
                        age=age,
                        weight_kg=weight_kg,
                        baseline_no2=baseline_no2,
                        notes=notes
                    )

                    # Add to database
                    db.session.add(patient)
                    patients_created += 1

                except Exception as e:
                    patients_skipped += 1
                    errors.append(f"Row {index+2}: {str(e)}")

            # Commit all changes at once
            if patients_created > 0:
                db.session.commit()

            # Prepare success message
            success_message = f"Successfully imported {patients_created} patient(s)"
            if patients_skipped > 0:
                success_message += f". Skipped {patients_skipped} row(s)"

            # Show errors if any
            if errors:
                error_message = "<br>".join(errors[:5])
                if len(errors) > 5:
                    error_message += f"<br>...and {len(errors) - 5} more errors"
                return render_template('patients_import.html', 
                                    success=success_message,
                                    error=f"Some rows had errors:<br>{error_message}")

            return render_template('patients_import.html', success=success_message)

        except Exception as e:
            logger.exception("Error importing patients")
            return render_template('patients_import.html', 
                                error=f"Error processing file: {str(e)}")

    # GET request - show the import form
    return render_template('patients_import.html')

@patient_bp.route('/<int:patient_id>/reassess', methods=['POST'])
def reassess_eligibility(patient_id):
    """Reassess patient eligibility for trial"""
    try:
        # Get patient
        patient = Patient.query.get_or_404(patient_id)

        # Reassess eligibility
        result = assess_trial_eligibility(patient_id)

        # Flash message and redirect
        flash(f'Eligibility reassessed: {"Eligible" if result else "Not eligible"} - {patient.eligibility_note}', 
              'success' if result else 'warning')

        return redirect(url_for('patients.view_patient', patient_id=patient_id))
    except Exception as e:
        flash(f'Error reassessing eligibility: {str(e)}', 'danger')
        return redirect(url_for('patients.view_patient', patient_id=patient_id))

from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Consent, Patient
from flask_login import login_required, current_user

consent_bp = Blueprint('consent', __name__, url_prefix='/consent')

@consent_bp.route('/', methods=['GET', 'POST'])
@login_required
def consent_form():
    """Display and process consent form"""
    if request.method == 'POST':
        signed_name = request.form.get('signed_name')
        understood_risks = bool(request.form.get('understood_risks'))
        agreed_to_terms = bool(request.form.get('agreed_to_terms'))
        patient_id = request.form.get('patient_id')
        
        if not patient_id:
            flash('Patient ID is required', 'danger')
            return redirect(url_for('consent.consent_form' _external=True))
            
        # Check if patient exists
        patient = Patient.query.get(patient_id)
        if not patient:
            flash('Invalid patient ID', 'danger')
            return redirect(url_for('consent.consent_form' _external=True))
            
        consent = Consent(
            patient_id=patient_id,
            signed_name=signed_name,
            understood_risks=understood_risks,
            agreed_to_terms=agreed_to_terms
        )
        db.session.add(consent)
        db.session.commit()
        
        flash('Consent successfully recorded', 'success')
        return redirect(url_for('patients.view_patient', patient_id=patient_id, _external=True))
        
    # For GET request, get patient list for dropdown
    patients = Patient.query.all()
    return render_template('consent_form.html', patients=patients)

@consent_bp.route('/patient/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def patient_consent(patient_id):
    """Consent form for a specific patient"""
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        signed_name = request.form.get('signed_name')
        understood_risks = bool(request.form.get('understood_risks'))
        agreed_to_terms = bool(request.form.get('agreed_to_terms'))
        
        consent = Consent(
            patient_id=patient_id,
            signed_name=signed_name,
            understood_risks=understood_risks,
            agreed_to_terms=agreed_to_terms
        )
        db.session.add(consent)
        db.session.commit()
        
        flash('Consent successfully recorded', 'success')
        return redirect(url_for('patients.view_patient', patient_id=patient_id, _external=True))
        
    return render_template('consent_form.html', patient=patient)

@consent_bp.route('/list', methods=['GET'])
@login_required
def list_consents():
    """List all consent records"""
    consents = Consent.query.all()
    patients = {p.id: p for p in Patient.query.all()}
    
    return render_template('consent_list.html', consents=consents, patients=patients)

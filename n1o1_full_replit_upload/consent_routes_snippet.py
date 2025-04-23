from flask import Blueprint, render_template, request, redirect, url_for
from models import db, Consent
from flask_login import login_required, current_user

consent_bp = Blueprint('consent', __name__, template_folder='../templates')

@consent_bp.route('/consent', methods=['GET', 'POST'])
@login_required
def consent_form():
    if request.method == 'POST':
        signed_name = request.form.get('signed_name')
        understood_risks = bool(request.form.get('understood_risks'))
        agreed_to_terms = bool(request.form.get('agreed_to_terms'))
        consent = Consent(
            patient_id=current_user.id,
            signed_name=signed_name,
            understood_risks=understood_risks,
            agreed_to_terms=agreed_to_terms
        )
        db.session.add(consent)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('consent_form.html')

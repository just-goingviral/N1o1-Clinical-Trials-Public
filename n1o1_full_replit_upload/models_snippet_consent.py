from app import db
from datetime import datetime

class Consent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    signed_name = db.Column(db.String(120))
    signed_date = db.Column(db.DateTime, default=datetime.utcnow)
    understood_risks = db.Column(db.Boolean)
    agreed_to_terms = db.Column(db.Boolean)

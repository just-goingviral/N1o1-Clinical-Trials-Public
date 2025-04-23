
"""
Patient eligibility assessment for N1O1 Clinical Trials
"""
from models import db, Patient, TrialCriteria
import logging

logger = logging.getLogger(__name__)

def assess_trial_eligibility(patient_id):
    """
    Assess if a patient is eligible for the N1O1 clinical trial
    
    Args:
        patient_id: ID of the patient to assess
        
    Returns:
        bool: True if eligible, False otherwise
    """
    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            logger.error(f"Patient with ID {patient_id} not found")
            return False
            
        # Get active trial criteria
        criteria = TrialCriteria.query.filter_by(is_active=True).first()
        if not criteria:
            logger.warning("No active trial criteria found")
            patient.is_eligible = True
            patient.eligibility_note = "Approved (no active criteria)"
            db.session.commit()
            return True
            
        # Assess eligibility based on age
        if criteria.min_age and patient.age < criteria.min_age:
            patient.is_eligible = False
            patient.eligibility_note = f"Patient age ({patient.age}) below minimum ({criteria.min_age})"
            db.session.commit()
            return False
            
        if criteria.max_age and patient.age > criteria.max_age:
            patient.is_eligible = False
            patient.eligibility_note = f"Patient age ({patient.age}) exceeds maximum ({criteria.max_age})"
            db.session.commit()
            return False
            
        # Assess eligibility based on baseline NO2
        if criteria.min_no2 and patient.baseline_no2 < criteria.min_no2:
            patient.is_eligible = False
            patient.eligibility_note = f"Baseline NO2 level ({patient.baseline_no2}) below minimum ({criteria.min_no2})"
            db.session.commit()
            return False
            
        if criteria.max_no2 and patient.baseline_no2 > criteria.max_no2:
            patient.is_eligible = False
            patient.eligibility_note = f"Baseline NO2 level ({patient.baseline_no2}) exceeds maximum ({criteria.max_no2})"
            db.session.commit()
            return False
            
        # Patient meets all criteria
        patient.is_eligible = True
        patient.eligibility_note = "Meets all criteria for trial participation"
        db.session.commit()
        return True
        
    except Exception as e:
        logger.exception(f"Error assessing eligibility for patient {patient_id}: {str(e)}")
        return False

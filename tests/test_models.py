"""
Test suite for database models
"""
import pytest
from datetime import datetime
from models import db, User, Patient, SupplementDose, NO2Level, Simulation, TrialCriteria, Consent, ClinicalNote, ChatSession, ChatMessage

class TestModels:
    """Test database models functionality"""
    
    def test_user_password_hashing(self):
        """Test password hashing and verification"""
        user = User(username="test_doctor", email="doctor@test.com", 
                   first_name="Test", last_name="Doctor", role="doctor")
        user.set_password("secure_password123")
        
        assert user.check_password("secure_password123")
        assert not user.check_password("wrong_password")
        assert user.password_hash != "secure_password123"
    
    def test_patient_creation(self):
        """Test patient model creation and serialization"""
        patient = Patient(
            name="John Doe",
            age=35,
            weight_kg=75.5,
            baseline_no2=0.2,
            notes="Healthy volunteer for nitric oxide study",
            is_eligible=True
        )
        
        patient_dict = patient.to_dict()
        assert patient_dict['name'] == "John Doe"
        assert patient_dict['age'] == 35
        assert patient_dict['weight_kg'] == 75.5
        assert patient_dict['baseline_no2'] == 0.2
    
    def test_trial_criteria(self):
        """Test trial criteria model with JSON fields"""
        criteria = TrialCriteria(
            name="N1O1 Phase II Trial",
            description="Testing nitric oxide supplementation effects",
            min_age=18,
            max_age=65,
            min_no2=0.1,
            max_no2=0.5,
            other_criteria={
                "exclusions": ["pregnancy", "hypertension"],
                "inclusions": ["healthy_volunteer"]
            }
        )
        
        criteria_dict = criteria.to_dict()
        assert criteria_dict['min_age'] == 18
        assert criteria_dict['max_age'] == 65
        assert "exclusions" in criteria_dict['other_criteria']
        assert len(criteria_dict['other_criteria']['exclusions']) == 2
    
    def test_supplement_dose_tracking(self):
        """Test supplement dose model"""
        dose = SupplementDose(
            patient_id=1,
            supplement="N1O1 Lozenge",
            dose_mg=30.0,
            time_given=datetime.utcnow(),
            notes="Administered under fasting conditions"
        )
        
        dose_dict = dose.to_dict()
        assert dose_dict['supplement'] == "N1O1 Lozenge"
        assert dose_dict['dose_mg'] == 30.0
        assert dose_dict['patient_id'] == 1
    
    def test_simulation_storage(self):
        """Test simulation model with JSON parameters"""
        simulation = Simulation(
            patient_id=1,
            model_type="Multi-compartment PK",
            parameters={
                "baseline": 0.2,
                "peak": 4.0,
                "t_peak": 0.5,
                "half_life": 0.5,
                "formulation": "immediate-release"
            },
            result_curve={
                "time": [0, 15, 30, 45, 60, 90, 120],
                "plasma_no2": [0.2, 2.1, 3.8, 3.2, 2.5, 1.5, 0.8],
                "cgmp": [1.0, 5.2, 9.5, 8.0, 6.2, 3.7, 2.0]
            },
            notes="Standard dose response simulation"
        )
        
        sim_dict = simulation.to_dict()
        assert sim_dict['model_type'] == "Multi-compartment PK"
        assert sim_dict['parameters']['baseline'] == 0.2
        assert len(sim_dict['result_curve']['time']) == 7
    
    def test_clinical_note_with_voice(self):
        """Test clinical note model with voice recording"""
        note = ClinicalNote(
            user_id=1,
            patient_id=1,
            title="Initial Assessment",
            text_content="Patient presents with normal vitals...",
            voice_recording_path="recordings/note_001.wav",
            voice_transcript="Automated transcript of voice note",
            is_private=False,
            tags=["assessment", "baseline", "nitric_oxide"]
        )
        
        note_dict = note.to_dict()
        assert note_dict['has_voice_recording'] is True
        assert "/static/voice_recordings/" in note_dict['voice_recording_url']
        assert len(note_dict['tags']) == 3
    
    def test_consent_record(self):
        """Test consent model"""
        consent = Consent(
            patient_id=1,
            signed_name="John Doe",
            understood_risks=True,
            agreed_to_terms=True
        )
        
        consent_dict = consent.to_dict()
        assert consent_dict['signed_name'] == "John Doe"
        assert consent_dict['understood_risks'] is True
        assert consent_dict['agreed_to_terms'] is True
    
    def test_chat_session_management(self):
        """Test chat session and message models"""
        session = ChatSession(
            id="test-session-uuid",
            user_identifier="192.168.1.1"
        )
        
        message = ChatMessage(
            session_id="test-session-uuid",
            role="user",
            content="What are the effects of nitric oxide on vasodilation?",
            attachment={
                "type": "image",
                "url": "/uploads/vasodilation_chart.png"
            }
        )
        
        session_dict = session.to_dict()
        message_dict = message.to_dict()
        
        assert session_dict['id'] == "test-session-uuid"
        assert message_dict['role'] == "user"
        assert message_dict['attachment']['type'] == "image"
    
    def test_model_relationships(self):
        """Test model relationships and cascading"""
        patient = Patient(name="Jane Doe", age=28, weight_kg=65.0, baseline_no2=0.25)
        
        # Test relationship setup
        dose1 = SupplementDose(supplement="N1O1", dose_mg=30.0, time_given=datetime.utcnow())
        dose2 = SupplementDose(supplement="NO Beetz", dose_mg=15.0, time_given=datetime.utcnow())
        
        patient.doses.append(dose1)
        patient.doses.append(dose2)
        
        assert len(patient.doses) == 2
        assert patient.doses[0].supplement == "N1O1"
        assert patient.doses[1].supplement == "NO Beetz"

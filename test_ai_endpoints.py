
"""
Test script for AI tools endpoints
"""
import requests
import json
import sys

BASE_URL = "http://localhost:5000"  # Adjust if using a different port

def test_endpoint(endpoint, payload):
    """Test an endpoint with a payload"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\nTesting endpoint: {url}")
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            print(f"✅ Success! Status code: {response.status_code}")
            data = response.json()
            # Print a truncated version of the response
            print("Response preview:")
            print(json.dumps(data, indent=2)[:500] + "..." if len(json.dumps(data, indent=2)) > 500 else json.dumps(data, indent=2))
            return True
        else:
            print(f"❌ Failed! Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def run_tests():
    """Run tests for all AI endpoints"""
    # Test data
    patient_data = {
        "id": 123,
        "name": "John Doe",
        "age": 45,
        "gender": "Male",
        "medical_history": "Hypertension, Type 2 Diabetes",
        "medications": ["Lisinopril", "Metformin"],
        "allergies": ["Penicillin"],
        "height_cm": 180,
        "weight_kg": 85
    }
    
    # Test pre-screening
    pre_screening_data = {
        "patient_data": patient_data,
        "trial_criteria": {
            "age_range": "18-65",
            "exclusion_conditions": ["Liver disease", "Kidney failure"],
            "required_tests": ["Blood pressure", "HbA1c"]
        }
    }
    test_endpoint("/api/ai-tools/pre-screening", pre_screening_data)
    
    # Test generate-note
    note_data = {
        "patient_data": patient_data,
        "observations": "Patient reports feeling dizzy after taking the trial medication. BP was slightly elevated at 145/90.",
        "metrics": {
            "blood_pressure": "145/90",
            "pulse": 75,
            "temperature_c": 37.2,
            "nitrite_level": 2.5
        }
    }
    test_endpoint("/api/ai-tools/generate-note", note_data)
    
    # Test patient-sentiment
    sentiment_data = {
        "feedback": "I've been feeling much better since starting this treatment. The headaches have stopped, but I'm still experiencing some fatigue in the afternoons.",
        "context": "Week 3 of nitric oxide trial, 10mg daily dose"
    }
    test_endpoint("/api/ai-tools/patient-sentiment", sentiment_data)
    
    # Test dynamic-consent
    consent_data = {
        "patient_data": patient_data,
        "trial_phase": "Phase 2 - Dose Escalation",
        "consent_type": "dose_change"
    }
    test_endpoint("/api/ai-tools/dynamic-consent", consent_data)
    
    # Test AI report writer
    report_data = {
        "trial_data": {
            "trial_id": "NO-2025-01",
            "title": "Effects of Nitric Oxide Supplementation on Cardiovascular Health",
            "participants": 65,
            "duration_weeks": 12,
            "primary_outcomes": ["Blood pressure reduction", "Endothelial function improvement"],
            "adverse_events": ["Mild headache (5 patients)", "Dizziness (3 patients)"],
            "efficacy_data": {
                "systolic_bp_change": -8.5,
                "diastolic_bp_change": -4.2,
                "plasma_nitrite_increase": "+65%"
            }
        },
        "report_type": "interim",
        "audience": "clinical"
    }
    test_endpoint("/api/ai-tools/ai-report-writer", report_data)

if __name__ == "__main__":
    print("Starting AI endpoints test...")
    run_tests()
    print("\nAll tests completed!")

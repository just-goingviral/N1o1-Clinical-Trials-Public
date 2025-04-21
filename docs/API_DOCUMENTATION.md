# N1O1 Clinical Trials Platform API Documentation

This document provides comprehensive documentation for the N1O1 Clinical Trials Platform API endpoints.

## Table of Contents
1. [Base URL](#base-url)
2. [Authentication](#authentication)
3. [Standard API](#standard-api)
   - [Patient Management](#patient-management)
   - [Simulation API](#simulation-api)
   - [Clinical Notes](#clinical-notes)
4. [AI Tools API](#ai-tools-api)
   - [Pre-screening Analysis](#pre-screening-analysis)
   - [Clinical Note Generator](#clinical-note-generator)
   - [Patient Sentiment Analysis](#patient-sentiment-analysis)
   - [Dynamic Consent Forms](#dynamic-consent-forms)
   - [AI Report Writer](#ai-report-writer)
5. [Error Handling](#error-handling)
6. [API Response Format](#api-response-format)

## Base URL

All API endpoints are relative to the base URL of your N1O1 Clinical Trials Platform instance.

For local development: `http://localhost:5000`

## Authentication

Most API endpoints require authentication. After logging in, include your session cookie with all requests.

## Standard API

### Patient Management

#### Create Patient
```
POST /api/patients
```

Request body:
```json
{
  "name": "John Doe",
  "age": 65,
  "weight_kg": 75.5,
  "baseline_no2": 0.3,
  "notes": "History of hypertension"
}
```

#### Get All Patients
```
GET /api/patients
```

#### Get Patient
```
GET /api/patients/{patient_id}
```

#### Update Patient
```
PUT /api/patients/{patient_id}
```

#### Delete Patient
```
DELETE /api/patients/{patient_id}
```

### Simulation API

#### Create Simulation
```
POST /api/simulations
```

Request body:
```json
{
  "patient_id": 12,
  "model_type": "HillTau",
  "parameters": {
    "baseline": 0.2,
    "peak": 4.0,
    "t_peak": 30,
    "half_life": 120
  },
  "notes": "Simulation for N1O1 lozenge"
}
```

#### Get Simulation
```
GET /api/simulations/{simulation_id}
```

#### Get Patient Simulations
```
GET /api/patients/{patient_id}/simulations
```

#### Run Simulation
```
POST /api/simulate
```

Request body:
```json
{
  "model_type": "HillTau",
  "parameters": {
    "baseline": 0.2,
    "peak": 4.0,
    "t_peak": 30,
    "half_life": 120
  },
  "time_points": [0, 15, 30, 60, 120, 180, 240, 300, 360]
}
```

### Clinical Notes

#### Create Note
```
POST /api/notes
```

Request body:
```json
{
  "patient_id": 12,
  "title": "Follow-up Visit",
  "text_content": "Patient reports improved symptoms...",
  "is_private": true,
  "tags": ["follow-up", "improvement"]
}
```

#### Get Notes
```
GET /api/notes
```

#### Get Patient Notes
```
GET /api/patients/{patient_id}/notes
```

#### Update Note
```
PUT /api/notes/{note_id}
```

#### Delete Note
```
DELETE /api/notes/{note_id}
```

## AI Tools API

All AI tool endpoints are prefixed with `/api/ai-tools/` and use Anthropic Claude for processing.

### Pre-screening Analysis

Analyzes patient data to determine eligibility for clinical trials based on inclusion/exclusion criteria.

```
POST /api/ai-tools/pre-screening
```

Request body:
```json
{
  "patient_data": {
    "age": 65,
    "medical_history": "Hypertension, Hyperlipidemia",
    "current_medications": ["Amlodipine 5mg", "Atorvastatin 20mg"],
    "vital_signs": {
      "blood_pressure": "135/85",
      "heart_rate": 78
    },
    "lab_results": {
      "lipid_panel": {
        "total_cholesterol": 190,
        "ldl": 110,
        "hdl": 45,
        "triglycerides": 150
      },
      "blood_glucose": 105
    }
  },
  "trial_criteria": {
    "inclusion": [
      "Age 50-75",
      "Documented cardiovascular disease",
      "Stable medication regimen for 3+ months"
    ],
    "exclusion": [
      "Active cancer",
      "Recent myocardial infarction (<3 months)",
      "Severe renal impairment"
    ]
  }
}
```

Response:
```json
{
  "status": "success",
  "result": {
    "eligibility_status": "potentially eligible with more information",
    "criteria_met": ["Age within required range (65 falls within 50-75)"],
    "criteria_not_met": [],
    "additional_info_needed": ["Documentation of cardiovascular disease"],
    "recommendations": ["Obtain complete medical records"]
  }
}
```

### Clinical Note Generator

Generates structured clinical notes based on visit data using the SOAP format.

```
POST /api/ai-tools/generate-note
```

Request body:
```json
{
  "patient_info": {
    "name": "John Smith",
    "age": 68,
    "gender": "Male"
  },
  "visit_data": {
    "visit_type": "Follow-up",
    "date": "2025-04-21",
    "chief_complaint": "Occasional chest discomfort",
    "vitals": {
      "bp": "138/84",
      "hr": 72,
      "resp": 16,
      "temp": 98.6,
      "spo2": 97
    },
    "observations": [
      "Slight shortness of breath on exertion",
      "Reports improved exercise tolerance with N1O1 lozenge",
      "No edema present",
      "Lung sounds clear"
    ]
  },
  "note_type": "progress"
}
```

Response:
```json
{
  "status": "success",
  "note": "PROGRESS NOTE\nDate: April 21, 2025\n\nSUBJECTIVE:\nMr. John Smith is a 68-year-old male presenting for follow-up evaluation..."
}
```

### Patient Sentiment Analysis

Analyzes patient feedback or comments for sentiment and key themes.

```
POST /api/ai-tools/patient-sentiment
```

Request body:
```json
{
  "patient_id": "PT-10045",
  "feedback_text": "I have been using the N1O1 lozenge for 3 weeks now and have noticed a significant improvement in my ability to walk up stairs without feeling winded. My chest pain has decreased from daily episodes to maybe once a week. The lozenges taste good, which makes them easy to take. The only issue I have is remembering to take them at the same time every day. The app reminders have been helpful, but sometimes I still forget. Overall, I am very pleased with the results so far.",
  "feedback_source": "follow-up interview",
  "feedback_date": "2025-04-15"
}
```

Response:
```json
{
  "status": "success",
  "analysis": {
    "sentiment": "positive",
    "sentiment_score": 0.8,
    "key_themes": ["Physical improvement", "Symptom reduction", "Treatment adherence"],
    "concerns": ["Difficulty maintaining consistent dosing schedule"],
    "positive_points": ["Significant improvement in exercise tolerance"],
    "suggestions": ["Consider implementing additional reminder methods"]
  }
}
```

### Dynamic Consent Forms

Generates personalized consent forms based on patient demographics and trial information.

```
POST /api/ai-tools/dynamic-consent
```

Request body:
```json
{
  "patient_demographics": {
    "age": 67,
    "education_level": "Bachelors degree",
    "language_preference": "English",
    "medical_literacy": "medium"
  },
  "trial_info": {
    "trial_name": "N1O1 Lozenge Efficacy Study",
    "treatment_description": "Daily N1O1 lozenges to improve nitric oxide levels and vascular function",
    "risks": ["Mild headache", "Temporary drop in blood pressure", "Dizziness when standing up quickly"],
    "benefits": ["Improved blood flow", "Better exercise capacity", "Potential reduction in angina symptoms"],
    "duration": "12 weeks",
    "procedures": ["Weekly blood draws", "Monthly exercise stress tests", "Daily symptom journaling"]
  },
  "format_type": "simplified"
}
```

Response:
```json
{
  "status": "success",
  "consent_form": "INFORMED CONSENT FORM\nN1O1 Lozenge Efficacy Study\n\n1. INTRODUCTION\nWe invite you to take part in a research study of N1O1 lozenges..."
}
```

### AI Report Writer

Generates structured research reports based on clinical trial data.

```
POST /api/ai-tools/ai-report-writer
```

Request body:
```json
{
  "trial_data": {
    "trial_name": "N1O1 Lozenge Phase 2b Trial",
    "trial_phase": "2b",
    "participants": 120,
    "treatment_groups": ["Placebo", "Low dose (5mg)", "High dose (10mg)"],
    "outcome_measures": ["Change in plasma nitrite levels", "Change in blood pressure", "Exercise capacity improvement", "Frequency of angina episodes"],
    "results_summary": {
      "plasma_nitrite": {
        "placebo": "+0.1 μM",
        "low_dose": "+1.8 μM",
        "high_dose": "+3.2 μM"
      },
      "blood_pressure_change": {
        "placebo": "-2/1 mmHg",
        "low_dose": "-8/4 mmHg",
        "high_dose": "-12/7 mmHg"
      },
      "exercise_capacity": {
        "placebo": "+4%",
        "low_dose": "+12%",
        "high_dose": "+18%"
      },
      "angina_reduction": {
        "placebo": "5%",
        "low_dose": "28%",
        "high_dose": "42%"
      }
    }
  },
  "report_type": "abstract",
  "audience": "researchers"
}
```

Response:
```json
{
  "status": "success",
  "report": "ABSTRACT\n\nBackground:\nNitric oxide (NO) bioavailability plays a crucial role in vascular function and cardiovascular health..."
}
```

## Error Handling

All API endpoints return appropriate HTTP status codes:

- 200: Success
- 400: Bad Request - Invalid input parameters
- 401: Unauthorized - Authentication required
- 403: Forbidden - Insufficient permissions
- 404: Not Found - Resource not found
- 500: Internal Server Error - Unexpected error

## API Response Format

All API responses follow a standard format:

Success:
```json
{
  "status": "success",
  "data": { ... } // Endpoint-specific data
}
```

Error:
```json
{
  "status": "error",
  "message": "Error description"
}
```
# N1O1 Clinical Trials API Documentation

## Overview

The N1O1 Clinical Trials API provides programmatic access to clinical trial data, simulations, and AI-powered analytics. All API endpoints are RESTful and return JSON responses.

## Base URL

```
http://localhost:5000/api
```

## Authentication

Most endpoints require authentication. Include the session cookie or use Flask-Login authentication.

## Endpoints

### Health Check

#### GET /system/health

Check system health and status.

**Response:**
```json
{
  "status": "online",
  "timestamp": "2025-01-14T10:30:00",
  "database": "connected",
  "session": "active",
  "port": "5000",
  "blueprints": {
    "analyzer": true,
    "api": true,
    "patient": true,
    "simulation": true
  }
}
```

### Patients

#### GET /api/patients

List all patients.

**Query Parameters:**
- `page` (integer): Page number for pagination
- `per_page` (integer): Items per page (default: 20)

**Response:**
```json
{
  "patients": [
    {
      "id": 1,
      "name": "John Doe",
      "age": 35,
      "weight_kg": 75.5,
      "baseline_no2": 0.2,
      "created_at": "2025-01-14T10:00:00"
    }
  ],
  "total": 50,
  "page": 1,
  "per_page": 20
}
```

#### POST /api/patients

Create a new patient.

**Request Body:**
```json
{
  "name": "Jane Smith",
  "age": 28,
  "weight_kg": 65.0,
  "baseline_no2": 0.25,
  "notes": "Healthy volunteer"
}
```

**Response:**
```json
{
  "status": "success",
  "patient": {
    "id": 2,
    "name": "Jane Smith",
    "age": 28,
    "weight_kg": 65.0,
    "baseline_no2": 0.25
  }
}
```

### Simulations

#### POST /api/simulations/run

Run a nitric oxide dynamics simulation.

**Request Body:**
```json
{
  "patient_id": 1,
  "dose": 30.0,
  "formulation": "immediate-release",
  "additional_doses": [
    {"time": 2.0, "amount": 15.0}
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "simulation_id": "sim_12345",
  "results": {
    "pk_parameters": {
      "cmax": 4.2,
      "tmax": 0.5,
      "auc": 8.5,
      "half_life": 0.45
    },
    "time_series": [
      {"time": 0, "plasma_no2": 0.2, "cgmp": 1.0},
      {"time": 15, "plasma_no2": 3.8, "cgmp": 8.5}
    ]
  }
}
```

### AI Tools

#### POST /api/ai-tools/pre-screening

AI-powered patient pre-screening for trial eligibility.

**Request Body:**
```json
{
  "patient_data": {
    "age": 45,
    "medical_history": "No significant history",
    "current_medications": ["aspirin"],
    "vital_signs": {"bp": "120/80", "hr": 72},
    "lab_results": {"hemoglobin": 14.5, "creatinine": 1.0}
  },
  "trial_criteria": {
    "inclusion": ["Age 18-65", "Healthy volunteer"],
    "exclusion": ["Pregnancy", "Severe hypertension"]
  }
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "eligibility_status": "eligible",
    "criteria_met": ["Age 18-65", "Healthy volunteer"],
    "criteria_not_met": [],
    "additional_info_needed": ["NO2 baseline levels"],
    "recommendations": ["Proceed with baseline testing"]
  }
}
```

#### POST /api/ai-tools/generate-note

Generate clinical notes using AI.

**Request Body:**
```json
{
  "patient_info": {
    "name": "John Doe",
    "age": 35,
    "gender": "Male"
  },
  "visit_data": {
    "visit_type": "Initial Assessment",
    "date": "2025-01-14",
    "chief_complaint": "Clinical trial enrollment",
    "vitals": {"bp": "118/76", "hr": 68, "temp": 98.6},
    "observations": ["Alert and oriented", "No acute distress"]
  },
  "note_type": "progress"
}
```

**Response:**
```json
{
  "status": "success",
  "note": "SUBJECTIVE:\nPatient presents for initial clinical trial enrollment...\n\nOBJECTIVE:\nVital signs: BP 118/76, HR 68, Temp 98.6°F...\n\nASSESSMENT:\nHealthy adult male suitable for trial participation...\n\nPLAN:\n1. Baseline NO2 testing\n2. Consent review..."
}
```

#### POST /api/ai-tools/research-insight

Generate research insights from trial data.

**Request Body:**
```json
{
  "research_data": {
    "trial_results": {
      "n_participants": 50,
      "mean_no2_increase": 3.2,
      "response_rate": 0.78
    },
    "simulation_data": [
      {"time": 0, "value": 0.2},
      {"time": 30, "value": 3.8}
    ],
    "observed_effects": ["Vasodilation", "Improved endothelial function"]
  },
  "focus_areas": ["mechanism of action", "clinical applications"],
  "insight_type": "comprehensive"
}
```

**Response:**
```json
{
  "status": "success",
  "insights": "Based on the trial data, several key insights emerge...",
  "visualization": "data:image/png;base64,iVBORw0KGgoAAAANS..."
}
```

### Analytics

#### POST /api/analytics/pk-parameters

Calculate pharmacokinetic parameters from concentration-time data.

**Request Body:**
```json
{
  "time": [0, 15, 30, 45, 60, 90, 120],
  "concentration": [0.2, 2.1, 3.8, 3.2, 2.5, 1.5, 0.8]
}
```

**Response:**
```json
{
  "status": "success",
  "parameters": {
    "cmax": 3.8,
    "tmax": 30,
    "auc": 245.5,
    "half_life": 28.5,
    "clearance": 0.015,
    "mrt": 52.3,
    "volume_distribution": 0.78
  }
}
```

#### POST /api/analytics/dose-response

Analyze dose-response relationships.

**Request Body:**
```json
{
  "doses": [10, 20, 30, 40, 50],
  "responses": [1.2, 2.5, 3.8, 4.5, 4.8]
}
```

**Response:**
```json
{
  "status": "success",
  "model": "Hill Equation",
  "parameters": {
    "vmax": 5.1,
    "ec50": 22.3,
    "hill_coefficient": 1.8,
    "r_squared": 0.98
  }
}
```

### Real-Time Monitoring

#### WebSocket /ws/monitoring

Connect to real-time monitoring stream.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:5000/ws/monitoring');
```

**Incoming Messages:**
```json
{
  "type": "metric_update",
  "metric": "plasma_no2",
  "value": 3.5,
  "timestamp": "2025-01-14T10:30:00",
  "anomaly_score": 0.1,
  "trend": "increasing"
}
```

**Alert Messages:**
```json
{
  "type": "alert",
  "metric": "blood_pressure",
  "severity": "high",
  "message": "Blood pressure below threshold: 85 < 90"
}
```

## Error Responses

All endpoints use consistent error formatting:

```json
{
  "status": "error",
  "error": "Validation error",
  "message": "Age must be between 18 and 100",
  "error_id": "err_12345"
}
```

### HTTP Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Rate Limiting

API requests are limited to:
- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated users

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1673789400
```

## Pagination

List endpoints support pagination:

```
GET /api/patients?page=2&per_page=50
```

Response includes pagination metadata:
```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "per_page": 50,
    "total": 234,
    "pages": 5
  }
}
```

## Data Formats

### Dates
All dates use ISO 8601 format: `YYYY-MM-DDTHH:MM:SS`

### Units
- Concentrations: µM (micromolar)
- Time: minutes or hours (specified in field name)
- Weight: kilograms
- Dose: milligrams

## SDK Examples

### Python
```python
import requests

# Get patient list
response = requests.get('http://localhost:5000/api/patients')
patients = response.json()

# Run simulation
sim_data = {
    'patient_id': 1,
    'dose': 30.0,
    'formulation': 'immediate-release'
}
response = requests.post('http://localhost:5000/api/simulations/run', json=sim_data)
```

### JavaScript
```javascript
// Using fetch API
const response = await fetch('http://localhost:5000/api/patients');
const patients = await response.json();

// Run AI pre-screening
const screeningData = {
  patient_data: {...},
  trial_criteria: {...}
};
const result = await fetch('http://localhost:5000/api/ai-tools/pre-screening', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify(screeningData)
});
```

## Webhooks

Configure webhooks for event notifications:

```json
POST /api/webhooks
{
  "url": "https://your-server.com/webhook",
  "events": ["simulation.completed", "patient.enrolled", "alert.triggered"]
}
```

## Support

For API support:
- Email: api-support@n1o1trials.com
- Documentation: https://docs.n1o1trials.com/api
- Status Page: https://status.n1o1trials.com

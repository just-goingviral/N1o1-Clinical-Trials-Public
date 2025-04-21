
"""
AI Tools for N1O1 Clinical Trials application
Provides endpoints for AI-assisted clinical trial tasks using Anthropic Claude
"""
from flask import Blueprint, jsonify, request
import os
from anthropic import Anthropic
import logging
import json
import time

ai_tools_bp = Blueprint('ai_tools', __name__, url_prefix='/api/ai-tools')

# Initialize Anthropic client
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
anthropic_client = None

if ANTHROPIC_API_KEY:
    anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
else:
    logging.warning("ANTHROPIC_API_KEY not found. AI tools will not function.")

@ai_tools_bp.route('/pre-screening', methods=['POST'])
def pre_screening():
    """
    Analyze patient data to determine eligibility for a clinical trial
    """
    if not anthropic_client:
        return jsonify({
            "status": "error",
            "message": "Anthropic API key not configured"
        }), 503
        
    try:
        data = request.json
        patient_data = data.get('patient_data', {})
        trial_criteria = data.get('trial_criteria', {})
        
        # Prepare the prompt for Claude
        prompt = f"""
        You are N1O1ai, a clinical trial assistant specializing in nitric oxide research.
        
        TASK: Assess whether the patient meets eligibility criteria for the clinical trial.
        
        PATIENT DATA:
        {json.dumps(patient_data, indent=2)}
        
        TRIAL CRITERIA:
        {json.dumps(trial_criteria, indent=2)}
        
        OUTPUT FORMAT:
        Provide a JSON response with the following structure:
        {{
            "eligible": true/false,
            "reasons": ["list of reasons why eligible or not"],
            "recommendations": ["list of recommendations if not eligible or special considerations if eligible"],
            "confidence_score": 0.0-1.0
        }}
        """
        
        # Call Claude API
        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1000
        )
        
        # Extract JSON from response
        result = response.content[0].text
        
        # Try to parse JSON from the response
        try:
            result_json = json.loads(result)
            return jsonify({
                "status": "success",
                "data": result_json
            })
        except json.JSONDecodeError:
            # If Claude didn't return valid JSON, do basic extraction
            eligible = "eligible\": true" in result.lower()
            return jsonify({
                "status": "success",
                "data": {
                    "eligible": eligible,
                    "reasons": ["See detailed response"],
                    "recommendations": ["See detailed response"],
                    "confidence_score": 0.7,
                    "raw_response": result
                }
            })
            
    except Exception as e:
        logging.error(f"Error in pre-screening endpoint: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ai_tools_bp.route('/generate-note', methods=['POST'])
def generate_note():
    """
    Generate a clinical note based on patient data and trial observations
    """
    if not anthropic_client:
        return jsonify({
            "status": "error",
            "message": "Anthropic API key not configured"
        }), 503
        
    try:
        data = request.json
        patient_data = data.get('patient_data', {})
        observations = data.get('observations', "")
        metrics = data.get('metrics', {})
        
        # Prepare the prompt for Claude
        prompt = f"""
        You are N1O1ai, a clinical trial assistant specializing in nitric oxide research.
        
        TASK: Generate a detailed clinical note based on the patient data and trial observations.
        
        PATIENT DATA:
        {json.dumps(patient_data, indent=2)}
        
        OBSERVATIONS:
        {observations}
        
        METRICS:
        {json.dumps(metrics, indent=2)}
        
        OUTPUT FORMAT:
        Generate a professional clinical note with the following sections:
        1. SUBJECTIVE: Patient's reported symptoms and experiences
        2. OBJECTIVE: Measurements, test results, and observations
        3. ASSESSMENT: Clinical interpretation of findings
        4. PLAN: Next steps for treatment or monitoring
        """
        
        # Call Claude API
        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1500
        )
        
        # Extract response
        result = response.content[0].text
        
        return jsonify({
            "status": "success",
            "data": {
                "clinical_note": result,
                "timestamp": time.time()
            }
        })
            
    except Exception as e:
        logging.error(f"Error in generate-note endpoint: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ai_tools_bp.route('/patient-sentiment', methods=['POST'])
def patient_sentiment():
    """
    Analyze patient feedback or communications to determine sentiment and concerns
    """
    if not anthropic_client:
        return jsonify({
            "status": "error",
            "message": "Anthropic API key not configured"
        }), 503
        
    try:
        data = request.json
        feedback = data.get('feedback', "")
        context = data.get('context', "")
        
        # Prepare the prompt for Claude
        prompt = f"""
        You are N1O1ai, a clinical trial assistant specializing in nitric oxide research.
        
        TASK: Analyze the patient's feedback to determine sentiment, concerns, and suggested actions.
        
        PATIENT FEEDBACK:
        {feedback}
        
        CONTEXT:
        {context}
        
        OUTPUT FORMAT:
        Provide a JSON response with the following structure:
        {{
            "sentiment": "positive/negative/neutral/mixed",
            "sentiment_score": -1.0 to 1.0,
            "main_concerns": ["list of main concerns extracted"],
            "suggested_actions": ["list of suggested actions to address concerns"],
            "key_phrases": ["notable phrases from the feedback"]
        }}
        """
        
        # Call Claude API
        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1000
        )
        
        # Extract JSON from response
        result = response.content[0].text
        
        # Try to parse JSON from the response
        try:
            result_json = json.loads(result)
            return jsonify({
                "status": "success",
                "data": result_json
            })
        except json.JSONDecodeError:
            # If Claude didn't return valid JSON, send raw response
            return jsonify({
                "status": "success",
                "data": {
                    "raw_response": result,
                    "sentiment": "mixed",  # Default fallback
                    "sentiment_score": 0,  # Neutral fallback
                }
            })
            
    except Exception as e:
        logging.error(f"Error in patient-sentiment endpoint: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ai_tools_bp.route('/dynamic-consent', methods=['POST'])
def dynamic_consent():
    """
    Generate dynamic consent materials based on patient profile and trial phase
    """
    if not anthropic_client:
        return jsonify({
            "status": "error",
            "message": "Anthropic API key not configured"
        }), 503
        
    try:
        data = request.json
        patient_data = data.get('patient_data', {})
        trial_phase = data.get('trial_phase', "")
        consent_type = data.get('consent_type', "standard")
        
        # Prepare the prompt for Claude
        prompt = f"""
        You are N1O1ai, a clinical trial assistant specializing in nitric oxide research.
        
        TASK: Generate dynamic consent information tailored to the patient profile and trial phase.
        
        PATIENT DATA:
        {json.dumps(patient_data, indent=2)}
        
        TRIAL PHASE:
        {trial_phase}
        
        CONSENT TYPE:
        {consent_type}
        
        OUTPUT FORMAT:
        Generate consent material with the following sections:
        1. OVERVIEW: Brief overview of what the patient is consenting to
        2. PROCEDURES: What procedures will be performed in this phase
        3. RISKS: Potential risks specific to this patient's profile
        4. BENEFITS: Potential benefits specific to this patient's profile
        5. ALTERNATIVES: Alternative options available
        6. CONTACT: Who to contact with questions
        
        Use clear, accessible language appropriate for the patient's background.
        """
        
        # Call Claude API
        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=2000
        )
        
        # Extract response
        result = response.content[0].text
        
        return jsonify({
            "status": "success",
            "data": {
                "consent_content": result,
                "consent_type": consent_type,
                "trial_phase": trial_phase,
                "timestamp": time.time()
            }
        })
            
    except Exception as e:
        logging.error(f"Error in dynamic-consent endpoint: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ai_tools_bp.route('/ai-report-writer', methods=['POST'])
def ai_report_writer():
    """
    Generate comprehensive trial reports based on accumulated data
    """
    if not anthropic_client:
        return jsonify({
            "status": "error",
            "message": "Anthropic API key not configured"
        }), 503
        
    try:
        data = request.json
        trial_data = data.get('trial_data', {})
        report_type = data.get('report_type', "interim")
        audience = data.get('audience', "clinical")
        
        # Prepare the prompt for Claude
        prompt = f"""
        You are N1O1ai, a clinical trial assistant specializing in nitric oxide research.
        
        TASK: Generate a {report_type} report for {audience} audience based on the trial data.
        
        TRIAL DATA:
        {json.dumps(trial_data, indent=2)}
        
        REPORT TYPE:
        {report_type}
        
        AUDIENCE:
        {audience}
        
        OUTPUT FORMAT:
        Generate a professional report with the following sections:
        1. EXECUTIVE SUMMARY: Brief overview of findings
        2. BACKGROUND: Context and purpose of the trial
        3. METHODOLOGY: How data was collected and analyzed
        4. RESULTS: Key findings and data presentation
        5. DISCUSSION: Interpretation of results
        6. CONCLUSION: Summary of implications
        7. RECOMMENDATIONS: Next steps
        
        Adjust the language and technical depth appropriate for the intended audience: 
        - If clinical: Include detailed medical terminology and specific biomarkers
        - If regulatory: Focus on protocol adherence and safety measures
        - If patient-facing: Use accessible language and focus on practical implications
        """
        
        # Call Claude API
        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=3000
        )
        
        # Extract response
        result = response.content[0].text
        
        return jsonify({
            "status": "success",
            "data": {
                "report_content": result,
                "report_type": report_type,
                "audience": audience,
                "timestamp": time.time()
            }
        })
            
    except Exception as e:
        logging.error(f"Error in ai-report-writer endpoint: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

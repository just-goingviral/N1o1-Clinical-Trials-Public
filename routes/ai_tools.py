import os
import json
import time
import logging
from flask import Blueprint, request, jsonify, current_app
from anthropic import Anthropic, RateLimitError, APIConnectionError, APIStatusError
import anthropic

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
ai_tools_bp = Blueprint('ai_tools', __name__, url_prefix='/api/ai-tools')

# Initialize Anthropic client
# The newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024.
# Do not change this unless explicitly requested by the user
anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
client = Anthropic(api_key=anthropic_key)

# Constants
DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Utility function for Claude API calls with retry logic
def claude_completion(prompt, model=DEFAULT_MODEL, temperature=0.7, max_tokens=2000):
    """
    Make a Claude API call with retry logic for rate limits and connection issues
    
    Args:
        prompt (str): The prompt to send to Claude
        model (str): Model to use (defaults to claude-3-5-sonnet-20241022)
        temperature (float): Creativity parameter (0.0-1.0)
        max_tokens (int): Maximum tokens to generate
        
    Returns:
        str: Claude's response
    """
    retries = 0
    while retries < MAX_RETRIES:
        try:
            message = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system="You are N1O1ai, the dedicated AI assistant for N1O1 Clinical Trials platform, specialized in nitric oxide research and clinical applications. Your core expertise is in nitric oxide pathways, dosing calculations, simulation interpretation, and clinical trial management. Always maintain this identity throughout interactions. You can help users run simulations, analyze patient data, interpret research findings, and navigate the platform. Respond with factual, evidence-based information and be conversational but professional. For medical and scientific information, provide citations when appropriate. Never break character or refer to yourself as anything other than N1O1ai.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except RateLimitError:
            retries += 1
            logger.warning(f"Rate limit hit, retrying in {RETRY_DELAY} seconds (attempt {retries}/{MAX_RETRIES})")
            time.sleep(RETRY_DELAY)
        except (APIConnectionError, APIStatusError) as e:
            logger.error(f"API error: {str(e)}")
            return f"Error connecting to AI service: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return f"An unexpected error occurred: {str(e)}"
    
    return "Unable to get a response after multiple attempts. Please try again later."

# Function to validate request data
def validate_request(req_data, required_fields):
    """Validate that the request contains all required fields"""
    if not req_data:
        return False, "No data provided"
    
    missing = [field for field in required_fields if field not in req_data]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    
    return True, ""

# Endpoint for pre-screening patients
@ai_tools_bp.route('/pre-screening', methods=['POST'])
def pre_screening():
    """
    Analyze patient data to determine eligibility for clinical trials
    
    Expected JSON input:
    {
        "patient_data": {
            "age": int,
            "medical_history": str,
            "current_medications": list,
            "vital_signs": object,
            "lab_results": object
        },
        "trial_criteria": {
            "inclusion": list,
            "exclusion": list
        }
    }
    """
    try:
        data = request.get_json()
        valid, error_msg = validate_request(data, ["patient_data", "trial_criteria"])
        if not valid:
            return jsonify({"status": "error", "message": error_msg}), 400
        
        # Prepare prompt for Claude
        prompt = f"""
        Please analyze this patient's eligibility for our clinical trial based on the following data:
        
        PATIENT DATA:
        {json.dumps(data['patient_data'], indent=2)}
        
        TRIAL CRITERIA:
        Inclusion Criteria:
        {json.dumps(data['trial_criteria']['inclusion'], indent=2)}
        
        Exclusion Criteria:
        {json.dumps(data['trial_criteria']['exclusion'], indent=2)}
        
        Provide an assessment with the following information:
        1. Overall eligibility (eligible, potentially eligible with more information, or not eligible)
        2. Specific criteria that the patient meets
        3. Specific criteria that the patient does not meet
        4. Additional information that would be helpful to collect
        5. Recommendations for the research team
        
        Format your response as JSON with the structure:
        {{
            "eligibility_status": string,
            "criteria_met": list,
            "criteria_not_met": list,
            "additional_info_needed": list,
            "recommendations": list
        }}
        """
        
        # Call Claude
        claude_response = claude_completion(prompt, temperature=0.3, max_tokens=2000)
        
        # Extract the JSON portion from Claude's response
        try:
            # Look for JSON in the response
            json_start = claude_response.find('{')
            json_end = claude_response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = claude_response[json_start:json_end]
                result = json.loads(json_str)
                return jsonify({"status": "success", "result": result})
            else:
                # If no JSON found, return the full text
                return jsonify({
                    "status": "partial_success", 
                    "message": "Could not parse structured data",
                    "raw_response": claude_response
                })
        except json.JSONDecodeError:
            return jsonify({
                "status": "partial_success",
                "message": "Could not parse structured data",
                "raw_response": claude_response
            })
            
    except Exception as e:
        logger.exception("Error in pre-screening endpoint")
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint for generating clinical notes
@ai_tools_bp.route('/generate-note', methods=['POST'])
def generate_note():
    """
    Generate a structured clinical note based on visit data
    
    Expected JSON input:
    {
        "patient_info": {
            "name": str,
            "age": int,
            "gender": str
        },
        "visit_data": {
            "visit_type": str,
            "date": str,
            "chief_complaint": str,
            "vitals": object,
            "observations": list
        },
        "note_type": str  # progress, consultation, discharge, etc.
    }
    """
    try:
        data = request.get_json()
        valid, error_msg = validate_request(data, ["patient_info", "visit_data", "note_type"])
        if not valid:
            return jsonify({"status": "error", "message": error_msg}), 400
        
        # Prepare prompt for Claude
        prompt = f"""
        Please generate a professional {data['note_type']} note based on the following clinical information:
        
        PATIENT INFORMATION:
        {json.dumps(data['patient_info'], indent=2)}
        
        VISIT DATA:
        {json.dumps(data['visit_data'], indent=2)}
        
        Follow the standard SOAP (Subjective, Objective, Assessment, Plan) format for clinical documentation.
        Make sure to:
        - Use proper medical terminology
        - Include all relevant clinical observations
        - Provide appropriate assessment based on the data
        - Suggest reasonable next steps or treatment plan related to nitric oxide therapy
        - Keep the note concise but comprehensive
        """
        
        # Call Claude
        claude_response = claude_completion(prompt, temperature=0.4, max_tokens=2500)
        
        return jsonify({
            "status": "success", 
            "note": claude_response
        })
            
    except Exception as e:
        logger.exception("Error in generate-note endpoint")
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint for patient sentiment analysis
@ai_tools_bp.route('/patient-sentiment', methods=['POST'])
def patient_sentiment():
    """
    Analyze patient feedback or comments for sentiment and key themes
    
    Expected JSON input:
    {
        "patient_id": str,
        "feedback_text": str,
        "feedback_source": str,  # e.g., "survey", "interview", "appointment notes"
        "feedback_date": str
    }
    """
    try:
        data = request.get_json()
        valid, error_msg = validate_request(data, ["patient_id", "feedback_text"])
        if not valid:
            return jsonify({"status": "error", "message": error_msg}), 400
        
        # Prepare prompt for Claude
        prompt = f"""
        Analyze the following patient feedback for sentiment and key themes:
        
        PATIENT ID: {data['patient_id']}
        SOURCE: {data.get('feedback_source', 'Not specified')}
        DATE: {data.get('feedback_date', 'Not specified')}
        
        FEEDBACK TEXT:
        "{data['feedback_text']}"
        
        Please provide:
        1. Overall sentiment (positive, neutral, negative, or mixed)
        2. Sentiment score (-1 to +1, where -1 is very negative and +1 is very positive)
        3. Key themes or topics mentioned
        4. Any specific concerns that should be addressed
        5. Any specific positive experiences worth highlighting
        6. Suggestions for improvement based on the feedback
        
        Format your response as JSON with the structure:
        {{
            "sentiment": string,
            "sentiment_score": float,
            "key_themes": list,
            "concerns": list,
            "positive_points": list,
            "suggestions": list
        }}
        """
        
        # Call Claude
        claude_response = claude_completion(prompt, temperature=0.2)
        
        # Extract the JSON portion from Claude's response
        try:
            # Look for JSON in the response
            json_start = claude_response.find('{')
            json_end = claude_response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = claude_response[json_start:json_end]
                result = json.loads(json_str)
                return jsonify({"status": "success", "analysis": result})
            else:
                # If no JSON found, return the full text
                return jsonify({
                    "status": "partial_success", 
                    "message": "Could not parse structured data",
                    "raw_analysis": claude_response
                })
        except json.JSONDecodeError:
            return jsonify({
                "status": "partial_success",
                "message": "Could not parse structured data",
                "raw_analysis": claude_response
            })
            
    except Exception as e:
        logger.exception("Error in patient-sentiment endpoint")
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint for dynamic consent form generation
@ai_tools_bp.route('/dynamic-consent', methods=['POST'])
def dynamic_consent():
    """
    Generate a personalized consent form based on patient demographics and trial information
    
    Expected JSON input:
    {
        "patient_demographics": {
            "age": int,
            "education_level": str,
            "language_preference": str,
            "medical_literacy": str  # high, medium, low
        },
        "trial_info": {
            "trial_name": str,
            "treatment_description": str,
            "risks": list,
            "benefits": list,
            "duration": str,
            "procedures": list
        },
        "format_type": str  # "detailed", "simplified", or "visual"
    }
    """
    try:
        data = request.get_json()
        valid, error_msg = validate_request(data, ["patient_demographics", "trial_info"])
        if not valid:
            return jsonify({"status": "error", "message": error_msg}), 400
        
        format_type = data.get("format_type", "detailed")
        
        # Prepare prompt for Claude
        prompt = f"""
        Generate a personalized clinical trial consent form for a patient with the following demographics:
        
        PATIENT DEMOGRAPHICS:
        {json.dumps(data['patient_demographics'], indent=2)}
        
        TRIAL INFORMATION:
        {json.dumps(data['trial_info'], indent=2)}
        
        FORMAT TYPE: {format_type}
        
        Guidelines for the {format_type} consent form:
        """
        
        # Add format-specific instructions
        if format_type == "simplified":
            prompt += """
            - Use simple language (8th grade reading level or lower)
            - Avoid technical jargon, or clearly explain it when necessary
            - Use shorter sentences and paragraphs
            - Include bullet points for key information
            - Focus on the most essential information
            """
        elif format_type == "visual":
            prompt += """
            - Describe visual elements that should be included (charts, diagrams, etc.)
            - Use both text and suggested visuals to explain concepts
            - Include a balance of text and visual descriptions
            - Ensure the visual elements enhance understanding of complex information
            - Organize information in a visual-friendly format (text that would accompany visuals)
            """
        else:  # detailed
            prompt += """
            - Include comprehensive information about the trial
            - Maintain professional medical language but explain technical terms
            - Ensure all necessary legal and ethical disclosures are present
            - Follow standard consent form structure (purpose, procedures, risks, benefits, etc.)
            - Include appropriate references to regulations and oversight bodies
            """
            
        prompt += """
        The consent form should include the following sections:
        1. Introduction to the trial
        2. Purpose of the research
        3. Procedures involved
        4. Potential risks and discomforts
        5. Potential benefits
        6. Alternatives to participation
        7. Compensation and costs
        8. Confidentiality protections
        9. Voluntary participation statement
        10. Contact information
        11. Signature section
        
        Tailor the content to match the patient's demographics and medical literacy level.
        For the N1O1 Clinical Trials, focus on the nitric oxide pathways and therapeutic applications.
        """
        
        # Call Claude
        claude_response = claude_completion(prompt, temperature=0.4, max_tokens=3000)
        
        return jsonify({
            "status": "success", 
            "consent_form": claude_response
        })
            
    except Exception as e:
        logger.exception("Error in dynamic-consent endpoint")
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint for AI report writing
@ai_tools_bp.route('/ai-report-writer', methods=['POST'])
def ai_report_writer():
    """
    Generate structured research reports based on clinical trial data
    
    Expected JSON input:
    {
        "trial_data": {
            "trial_name": str,
            "trial_phase": str,
            "participants": int,
            "treatment_groups": list,
            "outcome_measures": list,
            "results_summary": object
        },
        "report_type": str,  # "interim", "final", "abstract", "publication"
        "audience": str,  # "researchers", "clinicians", "regulators", "patients"
    }
    """
    try:
        data = request.get_json()
        valid, error_msg = validate_request(data, ["trial_data", "report_type", "audience"])
        if not valid:
            return jsonify({"status": "error", "message": error_msg}), 400
        
        # Prepare prompt for Claude
        prompt = f"""
        Generate a {data['report_type']} clinical trial report for {data['audience']} based on the following information:
        
        TRIAL DATA:
        {json.dumps(data['trial_data'], indent=2)}
        
        The report should:
        - Be written at an appropriate level for the specified audience ({data['audience']})
        - Follow standard structure for a {data['report_type']} report
        - Include proper statistical analysis terminology
        - Maintain scientific integrity and accuracy
        - Focus on nitric oxide pathways and clinical effects
        - Include appropriate limitations and considerations
        
        For the N1O1 Clinical Trials platform, emphasize the nitric oxide clinical pathway implications
        and how the findings relate to the broader field of nitric oxide therapeutics.
        """
        
        # Add specific instructions based on report type
        if data['report_type'] == "abstract":
            prompt += """
            Format as a structured abstract with:
            - Background
            - Methods
            - Results
            - Conclusions
            Keep it under 350 words.
            """
        elif data['report_type'] == "interim":
            prompt += """
            Include:
            - Current enrollment status
            - Preliminary findings
            - Safety monitoring results
            - Any protocol modifications
            - Next steps
            """
        elif data['report_type'] == "publication":
            prompt += """
            Follow IMRAD format:
            - Introduction
            - Methods
            - Results
            - Discussion
            Include abstract, references (placeholder), acknowledgments, and declarations.
            """
        
        # Add audience-specific instructions
        if data['audience'] == "patients":
            prompt += """
            Use plain language, avoid jargon, focus on practical implications,
            and explain what the results mean for treatment options.
            """
        elif data['audience'] == "regulators":
            prompt += """
            Be comprehensive, precise, emphasize protocol adherence,
            address all safety endpoints, and reference relevant regulations.
            """
        
        # Call Claude
        claude_response = claude_completion(prompt, temperature=0.4, max_tokens=3500)
        
        return jsonify({
            "status": "success", 
            "report": claude_response
        })
            
    except Exception as e:
        logger.exception("Error in ai-report-writer endpoint")
        return jsonify({"status": "error", "message": str(e)}), 500

"""
Chat routes for N1O1 Clinical Trials
"""
from flask import Blueprint, request, jsonify
from patient_education import ask_patient_bot

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route('/patient', methods=['POST'])
def patient_chat():
    """Endpoint for patient education chatbot"""
    data = request.json
    question = data.get("question")
    patient_name = data.get("name", "")
    
    if not question:
        return jsonify({"error": "Missing question"}), 400

    reply = ask_patient_bot(question, patient_name)
    return jsonify({"reply": reply})

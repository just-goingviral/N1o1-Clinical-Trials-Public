
from flask import Blueprint, request, jsonify
from patient_education import ask_patient_bot

# Create a blueprint for patient education routes
patient_edu_bp = Blueprint('patient_edu', __name__, url_prefix='/chat')

@patient_edu_bp.route('/patient', methods=['POST'])
def patient_chat():
    data = request.json
    question = data.get("question")
    patient_name = data.get("name", "")
    if not question:
        return jsonify({"error": "Missing question"}), 400

    reply = ask_patient_bot(question, patient_name)
    return jsonify({"reply": reply})

# To register in main.py:
# from routes.patient_edu_routes import patient_edu_bp
# app.register_blueprint(patient_edu_bp)

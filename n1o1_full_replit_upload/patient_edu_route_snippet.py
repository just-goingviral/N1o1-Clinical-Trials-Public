from flask import request, jsonify
from patient_education import ask_patient_bot

@app.route('/chat/patient', methods=['POST'])
def patient_chat():
    data = request.json
    question = data.get("question")
    patient_name = data.get("name", "")
    if not question:
        return jsonify({"error": "Missing question"}), 400

    reply = ask_patient_bot(question, patient_name)
    return jsonify({"reply": reply})

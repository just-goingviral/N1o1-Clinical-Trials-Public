
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load your OpenAI API key securely
openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_patient_bot(question, patient_name=""):
    try:
        system_prompt = (
            "You are a friendly health assistant named N1O1 Coach. "
            "Answer questions in plain language for patients with heart conditions. "
            "Encourage adherence, explain nitric oxide therapy simply, and avoid medical jargon. "
            f"Patient name is {patient_name} if known."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4",  # Or use "gpt-3.5-turbo" if limited
            messages=messages,
            temperature=0.7,
            max_tokens=400
        )

        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error reaching patient assistant: {str(e)}"

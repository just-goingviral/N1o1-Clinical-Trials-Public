"""
Test script for the N1O1ai assistant
"""
import requests
import json
import os

def test_assistant():
    """Test the N1O1ai assistant API"""
    print("\nTesting N1O1ai Assistant...")
    
    url = "http://localhost:5000/api/assistant"
    
    # Test questions
    questions = [
        "What is nitric oxide and how does it help with heart disease?",
        "Can you tell me about Dr. Nathan Bryan?",
        "What products are in the N1O1 lineup?",
        "How does the Nitrite Dynamics app work?",
        "Are you powered by OpenAI's ChatGPT?",  # This should trigger the rules about identity
        "Who created you?"  # This should also trigger identity rules
    ]
    
    for i, question in enumerate(questions):
        print(f"\nQuestion {i+1}: {question}")
        
        response = requests.post(url, json={"message": question})
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result['response'][:150]}...")  # Print first 150 chars
        else:
            print(f"Error: {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    test_assistant()
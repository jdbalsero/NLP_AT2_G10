"""
Test script for the chatbot application.
"""
import requests
import json

def test_chatbot():
    print("Testing chatbot application...")
    
    # Test questions
    test_questions = [
        "What are the main sources of greenhouse gas emissions in Australia?",
        "How are Scope 1 emissions defined?",
        "What are the reporting requirements for large emitters?"
    ]
    
    # Base URL
    base_url = "http://localhost:5000"
    
    # Test each question
    for question in test_questions:
        print(f"\nTesting question: {question}")
        try:
            response = requests.post(
                f"{base_url}/ask",
                json={"question": question}
            )
            
            if response.status_code == 200:
                answer = response.json()["answer"]
                print(f"Answer: {answer}")
            else:
                print(f"Error: {response.status_code}")
                print(response.json())
                
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_chatbot() 
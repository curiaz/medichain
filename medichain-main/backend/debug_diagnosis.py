import requests
import json

def test_diagnosis_detailed(symptoms, age=25, gender="male"):
    """Test the AI diagnosis API with detailed debugging"""
    url = "http://localhost:5001/predict"
    
    payload = {
        "symptoms": symptoms,
        "age": age,
        "gender": gender
    }
    
    try:
        response = requests.post(url, json=payload)
        result = response.json()
        
        print(f"\n=== DETAILED TEST: '{symptoms}' ===")
        print(f"Full Response: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"Error testing '{symptoms}': {e}")

if __name__ == "__main__":
    # Test the problematic case
    test_diagnosis_detailed("Fever and cough")

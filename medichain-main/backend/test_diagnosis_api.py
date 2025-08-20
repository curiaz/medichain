import requests
import json

def test_diagnosis(symptoms, age=25, gender="male"):
    """Test the AI diagnosis API with given symptoms"""
    url = "http://localhost:5001/predict"
    
    payload = {
        "symptoms": symptoms,
        "age": age,
        "gender": gender
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"\n=== Testing: '{symptoms}' ===")
            print(f"Status: {result.get('status', 'N/A')}")
            
            if 'analysis' in result:
                analysis = result['analysis']
                print(f"Primary Diagnosis: {analysis.get('primary_diagnosis', 'N/A')}")
                print(f"Confidence: {analysis.get('confidence', 'N/A')}%")
                print(f"Recommendations: {analysis.get('recommendations', [])}")
            else:
                print(f"Response: {result}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error testing '{symptoms}': {e}")

if __name__ == "__main__":
    # Test various symptoms
    test_cases = [
        "Fever",
        "Cough",
        "Headache",
        "Fever and cough",
        "Sore throat",
        "Shortness of breath",
        "Fatigue",
        "Fever, headache, and fatigue"
    ]
    
    for symptoms in test_cases:
        test_diagnosis(symptoms)

import requests
import json

def test_ai_diagnosis():
    """Test the AI diagnosis API"""
    
    base_url = "http://localhost:5001"
    
    # Test health check
    print("Testing health check...")
    response = requests.get(f"{base_url}/health")
    print(f"Health check: {response.json()}")
    
    # Test symptoms endpoint
    print("\nTesting symptoms endpoint...")
    response = requests.get(f"{base_url}/symptoms")
    symptoms = response.json()
    print(f"Available symptoms: {symptoms['symptoms']}")
    
    # Test diagnoses endpoint
    print("\nTesting diagnoses endpoint...")
    response = requests.get(f"{base_url}/diagnoses")
    diagnoses = response.json()
    print(f"Available diagnoses: {diagnoses['diagnoses']}")
    
    # Test prediction
    print("\nTesting prediction...")
    test_symptoms = {
        "fever": 1,
        "cough": 1,
        "fatigue": 1,
        "shortness_of_breath": 0,
        "headache": 1,
        "sore_throat": 1
    }
    
    response = requests.post(
        f"{base_url}/predict",
        json={"symptoms": test_symptoms}
    )
    
    result = response.json()
    print(f"Prediction result: {json.dumps(result, indent=2)}")
    
    # Test another case
    print("\nTesting another case...")
    test_symptoms2 = {
        "fever": 1,
        "cough": 0,
        "fatigue": 1,
        "shortness_of_breath": 1,
        "headache": 0,
        "sore_throat": 0
    }
    
    response = requests.post(
        f"{base_url}/predict",
        json={"symptoms": test_symptoms2}
    )
    
    result = response.json()
    print(f"Prediction result: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    test_ai_diagnosis()

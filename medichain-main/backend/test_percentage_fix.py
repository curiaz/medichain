import requests
import json

def test_percentage_formatting():
    """Test that percentage formatting is correct"""
    url = "http://localhost:5001/predict"
    
    payload = {
        "symptoms": "cough",
        "age": 15,
        "gender": "male"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            
            print("=== Testing Percentage Formatting ===")
            
            if 'analysis' in result:
                analysis = result['analysis']
                primary = analysis.get('primary_diagnosis', {})
                
                print(f"Condition: {primary.get('condition')}")
                print(f"Confidence: {primary.get('confidence')} (should be a number like 99.0)")
                print(f"Explanation: {primary.get('explanation')}")
                
            if 'model_info' in result:
                model_info = result['model_info']
                print(f"Model Accuracy: {model_info.get('accuracy')} (should be a number like 87.5)")
                
        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_percentage_formatting()

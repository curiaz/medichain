#!/usr/bin/env python3
"""
Test model info endpoint
"""

import requests
import json

def test_model_info():
    """Test the model info endpoint"""
    
    try:
        response = requests.get("http://localhost:5001/learning-stats", timeout=10)
        
        print(f"Model Info Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Model Info Response:")
            print(json.dumps(result, indent=2))
            
            # Check if model_info exists
            model_info = result.get('model_info', {})
            if model_info:
                print(f"\n✅ Model Name: {model_info.get('name')}")
                print(f"✅ Accuracy: {model_info.get('accuracy')}")
                print(f"✅ Version: {model_info.get('version')}")
            else:
                print("❌ No model_info found in response")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_model_info()

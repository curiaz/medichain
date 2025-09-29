#!/usr/bin/env python3
"""
Test API with Test Token
"""

import requests
import json

def test_api_with_token():
    """Test the patient profile API endpoint with test token"""
    print("Testing API with Test Token...")
    
    try:
        headers = {
            "Authorization": "Bearer test_token_123",
            "Content-Type": "application/json"
        }
        
        response = requests.get("http://localhost:5000/api/profile/patient", headers=headers, timeout=5)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("SUCCESS: Patient profile loaded!")
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"ERROR: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Main function"""
    print("Testing API with Test Token")
    print("=" * 30)
    
    test_api_with_token()
    print("\nDone!")

if __name__ == "__main__":
    main()


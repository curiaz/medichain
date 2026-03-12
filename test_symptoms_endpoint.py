#!/usr/bin/env python3
"""Test the /api/symptoms endpoint"""

import requests
import json

def test_symptoms_endpoint():
    """Test the symptoms endpoint"""
    try:
        print("Testing /api/symptoms endpoint...")
        response = requests.get("https://medichain.clinic/api/symptoms", timeout=5)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            data = response.json()
            print(f"Response Data:")
            print(json.dumps(data, indent=2))
            
            if data.get('success'):
                print(f"\n✅ Success! Found {data.get('count', 0)} symptoms")
                if data.get('symptoms'):
                    print(f"First 5 symptoms:")
                    for symptom in data['symptoms'][:5]:
                        print(f"  - {symptom['display']} (key: {symptom['key']})")
            else:
                print(f"\n❌ Error: {data.get('message', 'Unknown error')}")
                
        except json.JSONDecodeError:
            print(f"Response Text: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server at https://medichain.clinic")
        print("   Make sure the backend server is running!")
    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timed out")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_symptoms_endpoint()


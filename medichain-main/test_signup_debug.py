#!/usr/bin/env python3
"""
Debug script to test the signup API endpoint
"""

import requests
import json

def test_signup():
    """Test the signup endpoint with debug information"""
    
    url = "http://localhost:5000/api/auth/signup"
    
    test_data = {
        "email": "testuser@gmail.com",
        "password": "TestPass123!",
        "first_name": "John",
        "last_name": "Doe", 
        "role": "patient"
    }
    
    print("Testing signup endpoint...")
    print(f"URL: {url}")
    print(f"Data being sent: {json.dumps(test_data, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(
            url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Content: {response.text}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                response_json = response.json()
                print(f"Response JSON: {json.dumps(response_json, indent=2)}")
            except json.JSONDecodeError:
                print("Could not decode response as JSON")
                
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the server. Make sure the backend is running on port 5000.")
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out.")
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    test_signup()

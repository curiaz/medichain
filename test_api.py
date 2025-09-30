#!/usr/bin/env python3
"""
Test API Endpoint
"""

import requests
import json

def test_api_endpoint():
    """Test the patient profile API endpoint"""
    print("Testing API Endpoint...")
    
    try:
        # Test the endpoint (this will fail authentication but we can see if server is running)
        response = requests.get("http://localhost:5000/api/profile/patient", timeout=5)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 401:
            print("SUCCESS: Server is running and endpoint exists!")
            print("Authentication required (expected)")
            return True
        else:
            print("Unexpected response")
            return False
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server")
        print("Make sure the Flask server is running: cd backend && python app.py")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Main function"""
    print("Testing API Endpoint")
    print("=" * 25)
    
    test_api_endpoint()
    print("\nDone!")

if __name__ == "__main__":
    main()


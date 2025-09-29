#!/usr/bin/env python3
"""
Backend Integration Test for Patient Profile Management
This script tests the patient profile API endpoints
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api/profile"

def test_patient_profile_endpoints():
    """Test all patient profile endpoints"""
    print("🏥 Testing Patient Profile Management Backend Integration")
    print("=" * 60)
    
    # Mock token for testing (in production, this would be a real Firebase token)
    mock_token = "mock_firebase_token_123"
    headers = {
        "Authorization": f"Bearer {mock_token}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Get Patient Profile
    print("\n1️⃣ Testing GET /api/profile/patient")
    try:
        response = requests.get(f"{API_BASE}/patient", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('message', 'Profile retrieved')}")
            if data.get('data'):
                print(f"   📋 Patient: {data['data'].get('user_profile', {}).get('first_name', 'N/A')} {data['data'].get('user_profile', {}).get('last_name', 'N/A')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
    
    # Test 2: Update Patient Profile
    print("\n2️⃣ Testing PUT /api/profile/patient")
    try:
        update_data = {
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+1 (555) 123-4567"
        }
        response = requests.put(f"{API_BASE}/patient", 
                              headers=headers, 
                              json=update_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('message', 'Profile updated')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
    
    # Test 3: Update Medical Information
    print("\n3️⃣ Testing PUT /api/profile/patient/medical")
    try:
        medical_data = {
            "medical_conditions": ["Hypertension", "Diabetes Type 2"],
            "allergies": ["Penicillin", "Shellfish"],
            "current_medications": ["Metformin 500mg", "Lisinopril 10mg"],
            "blood_type": "O+",
            "medical_notes": "Regular checkups every 6 months"
        }
        response = requests.put(f"{API_BASE}/patient/medical", 
                              headers=headers, 
                              json=medical_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('message', 'Medical info updated')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
    
    # Test 4: Update Privacy Settings
    print("\n4️⃣ Testing PUT /api/profile/patient/privacy")
    try:
        privacy_data = {
            "profile_visibility": "private",
            "medical_info_visible_to_doctors": True,
            "medical_info_visible_to_hospitals": False,
            "allow_ai_analysis": True,
            "two_factor_enabled": False
        }
        response = requests.put(f"{API_BASE}/patient/privacy", 
                              headers=headers, 
                              json=privacy_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('message', 'Privacy settings updated')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
    
    # Test 5: Upload Document (Mock)
    print("\n5️⃣ Testing POST /api/profile/patient/documents")
    try:
        # Create a mock file
        mock_file = {
            'file': ('test_document.pdf', b'Mock PDF content', 'application/pdf')
        }
        form_data = {
            'document_type': 'health_document',
            'description': 'Test health document'
        }
        
        # Remove Content-Type header for multipart form data
        upload_headers = {"Authorization": f"Bearer {mock_token}"}
        
        response = requests.post(f"{API_BASE}/patient/documents", 
                               headers=upload_headers,
                               files=mock_file,
                               data=form_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('message', 'Document uploaded')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")

def test_server_connection():
    """Test if the Flask server is running"""
    print("\n🔍 Testing Server Connection...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Flask server is running!")
            return True
        else:
            print(f"⚠️  Server responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask server!")
        print("💡 Make sure the Flask server is running:")
        print("   cd backend && python app.py")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def main():
    """Main test function"""
    print("🏥 MediChain Patient Profile - Backend Integration Test")
    print("=" * 60)
    
    # Test server connection first
    if not test_server_connection():
        print("\n❌ Cannot proceed with API tests - server not running")
        return False
    
    # Test API endpoints
    test_patient_profile_endpoints()
    
    print("\n🎉 Backend integration test completed!")
    print("\n📋 Next steps:")
    print("1. Check the Flask server logs for any errors")
    print("2. Verify database connection and tables")
    print("3. Test with real Firebase authentication")
    print("4. Test frontend integration")
    
    return True

if __name__ == "__main__":
    main()


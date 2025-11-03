"""
Test script to diagnose signup flow issues
"""
import requests
import json

API_URL = "http://localhost:5000/api"

def test_patient_signup():
    """Test patient signup flow"""
    print("\n" + "="*60)
    print("🧪 Testing Patient Signup Flow")
    print("="*60)
    
    # Test data
    test_data = {
        "id_token": "fake_firebase_token_for_testing",
        "name": "Test Patient",
        "role": "patient",
        "password": "testpassword123"
    }
    
    print(f"\n📤 Sending POST request to: {API_URL}/auth/register")
    print(f"📦 Payload: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📨 Response Status: {response.status_code}")
        print(f"📨 Response Headers: {dict(response.headers)}")
        print(f"📨 Response Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200 or response.status_code == 201:
            print("\n✅ Signup endpoint is accessible!")
        else:
            print(f"\n⚠️  Unexpected status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend!")
        print("   Make sure the backend server is running on port 5000")
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")

def test_backend_health():
    """Test if backend is responding"""
    print("\n" + "="*60)
    print("🏥 Testing Backend Health")
    print("="*60)
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        print(f"\n✅ Backend is running!")
        print(f"📨 Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("\n❌ Backend is NOT running on port 5000!")
    except Exception as e:
        print(f"\n⚠️  Health check endpoint may not exist: {e}")

def check_firebase_config():
    """Check if Firebase is configured"""
    print("\n" + "="*60)
    print("🔥 Checking Firebase Configuration")
    print("="*60)
    
    try:
        import sys
        sys.path.append('./backend')
        from auth.firebase_auth import firebase_auth_service
        
        print("\n✅ Firebase auth service imported successfully!")
        print(f"   Service type: {type(firebase_auth_service)}")
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
    except Exception as e:
        print(f"\n⚠️  Error: {e}")

if __name__ == "__main__":
    print("\n🔍 MEDICHAIN SIGNUP DIAGNOSTICS")
    print("="*60)
    
    # Test 1: Backend health
    test_backend_health()
    
    # Test 2: Firebase config
    check_firebase_config()
    
    # Test 3: Patient signup
    test_patient_signup()
    
    print("\n" + "="*60)
    print("✅ Diagnostics Complete!")
    print("="*60 + "\n")

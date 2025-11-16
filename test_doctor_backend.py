"""
Quick test script to verify doctor profile backend endpoints
Run this after migration to ensure everything is working
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Test configuration
BASE_URL = 'http://localhost:5000'
TOKEN = None  # Will be set after login

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_doctor_update():
    """Test updating doctor profile"""
    print_section("TEST 1: Update Doctor Profile")
    
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'first_name': 'Test',
        'last_name': 'Doctor',
        'phone': '555-0123',
        'address': '123 Medical St',
        'city': 'Boston',
        'state': 'MA',
        'zip_code': '02101',
        'specialization': 'Cardiology',
        'license_number': 'TEST123',
        'years_of_experience': 5,
        'hospital_affiliation': 'Test Hospital'
    }
    
    response = requests.put(f'{BASE_URL}/api/profile/doctor/update', headers=headers, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.status_code == 200

def test_get_doctor_details():
    """Test fetching doctor details"""
    print_section("TEST 2: Get Doctor Details")
    
    headers = {'Authorization': f'Bearer {TOKEN}'}
    response = requests.get(f'{BASE_URL}/api/profile/doctor/details', headers=headers)
    
    print(f"Status: {response.status_code}")
    result = response.json()
    
    if result.get('success'):
        data = result.get('data', {})
        print(f"\n📋 Profile Data:")
        print(f"  Name: {data.get('first_name')} {data.get('last_name')}")
        print(f"  Specialization: {data.get('specialization')}")
        print(f"  License: {data.get('license_number')}")
        print(f"  Address: {data.get('address')}, {data.get('city')}, {data.get('state')} {data.get('zip_code')}")
    else:
        print(f"Response: {result}")
    
    return response.status_code == 200

def test_privacy_update():
    """Test updating privacy settings"""
    print_section("TEST 3: Update Privacy Settings")
    
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'profile_visibility': 'public',
        'show_email': True,
        'show_phone': False,
        'allow_patient_messages': True,
        'data_sharing': False
    }
    
    response = requests.put(f'{BASE_URL}/api/profile/doctor/privacy', headers=headers, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.status_code == 200

def test_activity_log():
    """Test fetching activity log"""
    print_section("TEST 4: Get Activity Log")
    
    headers = {'Authorization': f'Bearer {TOKEN}'}
    response = requests.get(f'{BASE_URL}/api/profile/doctor/activity', headers=headers)
    
    print(f"Status: {response.status_code}")
    result = response.json()
    
    if result.get('success'):
        activities = result.get('activities', [])
        print(f"\n📜 Recent Activities ({len(activities)}):")
        for activity in activities[:5]:  # Show last 5
            print(f"  • {activity.get('action')} - {activity.get('details')}")
            print(f"    {activity.get('timestamp')}")
    else:
        print(f"Response: {result}")
    
    return response.status_code == 200

def test_get_documents():
    """Test fetching documents"""
    print_section("TEST 5: Get Uploaded Documents")
    
    headers = {'Authorization': f'Bearer {TOKEN}'}
    response = requests.get(f'{BASE_URL}/api/profile/doctor/documents', headers=headers)
    
    print(f"Status: {response.status_code}")
    result = response.json()
    
    if result.get('success'):
        documents = result.get('documents', [])
        print(f"\n📄 Uploaded Documents ({len(documents)}):")
        for doc in documents:
            print(f"  • {doc.get('document_type')}: {doc.get('filename')}")
            print(f"    Status: {doc.get('status')} | Size: {doc.get('file_size')} bytes")
    else:
        print(f"Response: {result}")
    
    return response.status_code == 200

def run_tests():
    """Run all tests"""
    global TOKEN
    
    print("\n" + "=" * 60)
    print("  DOCTOR PROFILE BACKEND TEST SUITE")
    print("=" * 60)
    
    # Check if backend is running
    try:
        requests.get(BASE_URL, timeout=2)
    except:
        print("\n❌ Backend server is not running!")
        print("Please start it with: cd backend && python app.py")
        return
    
    print("\n✅ Backend server is running")
    
    # Get token from user
    print("\n🔑 Authentication Required")
    print("Please login as a doctor and provide your Firebase token.")
    print("You can get this from:")
    print("  1. Login to the app")
    print("  2. Open browser console")
    print("  3. Run: localStorage.getItem('medichain_token')")
    print()
    TOKEN = input("Enter your Firebase token: ").strip()
    
    if not TOKEN:
        print("\n❌ No token provided. Cannot run tests.")
        return
    
    # Run tests
    results = {
        'Update Profile': test_doctor_update(),
        'Get Details': test_get_doctor_details(),
        'Update Privacy': test_privacy_update(),
        'Get Activity': test_activity_log(),
        'Get Documents': test_get_documents()
    }
    
    # Summary
    print_section("TEST RESULTS SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n📊 Score: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Doctor profile backend is fully functional!")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")

if __name__ == '__main__':
    run_tests()

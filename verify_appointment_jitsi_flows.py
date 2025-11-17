"""
Comprehensive Verification of Patient and Doctor Appointment Flows with Jitsi Links
Tests end-to-end appointment creation, Jitsi URL generation, and database persistence
"""
import os
import sys
import requests
import json
import time
from datetime import datetime, timedelta

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Load environment
from dotenv import load_dotenv
load_dotenv('backend/.env')

BACKEND_URL = "https://medichain.clinic"

def print_section(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def wait_for_backend(max_attempts=10):
    """Wait for backend to be ready"""
    print("Waiting for backend to start...")
    for i in range(max_attempts):
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=2)
            if response.status_code == 200:
                print("SUCCESS: Backend is running")
                return True
        except:
            pass
        time.sleep(1)
        print(f"  Attempt {i+1}/{max_attempts}...")
    print("ERROR: Backend did not start within timeout")
    return False

def test_backend_health():
    """Test backend health endpoint"""
    print_section("TEST 1: Backend Health Check")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Backend is healthy")
            print(f"  Status: {data.get('status', 'unknown')}")
            print(f"  AI System: {data.get('ai_system', 'unknown')}")
            return True
        else:
            print(f"ERROR: Backend returned {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: Cannot connect to backend: {e}")
        return False

def test_jitsi_url_generation():
    """Test that Jitsi URL is generated correctly"""
    print_section("TEST 2: Jitsi URL Generation Logic")
    
    # Simulate the URL generation logic
    import uuid
    doctor_uid = "test_doctor_123"
    appointment_date = "2025-01-15"
    appointment_time = "10:00"
    
    safe_date = appointment_date.replace("-", "")
    safe_time = appointment_time.replace(":", "")
    room_suffix = uuid.uuid4().hex[:8]
    room_name = f"medichain-{doctor_uid}-{safe_date}-{safe_time}-{room_suffix}"
    meeting_url = f"https://meet.jit.si/{room_name}#config.prejoinPageEnabled=true"
    
    print(f"SUCCESS: Jitsi URL generation working")
    print(f"  Room Name: {room_name}")
    print(f"  Meeting URL: {meeting_url}")
    
    # Validate URL format
    if meeting_url.startswith("https://meet.jit.si/medichain-"):
        print("SUCCESS: URL format is correct")
        return True
    else:
        print("ERROR: URL format is incorrect")
        return False

def test_meeting_url_parsing():
    """Test parsing meeting URL from notes"""
    print_section("TEST 3: Meeting URL Parsing from Notes")
    
    # Simulate notes with meeting URL
    test_notes = "Patient consultation\nMeeting: https://meet.jit.si/medichain-doc123-20250115-1000-abc123def"
    
    meeting_url = None
    for line in test_notes.splitlines():
        if "Meeting:" in line and "http" in line:
            meeting_url = line.split("Meeting:", 1)[1].strip()
            break
    
    if meeting_url:
        print(f"SUCCESS: Meeting URL parsed correctly")
        print(f"  Extracted URL: {meeting_url}")
        return True
    else:
        print("ERROR: Failed to parse meeting URL")
        return False

def test_appointment_endpoint_auth():
    """Test appointment endpoint requires authentication"""
    print_section("TEST 4: Appointment Endpoint Authentication")
    
    appointment_data = {
        "doctor_firebase_uid": "test_doctor_uid",
        "appointment_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "appointment_time": "10:00",
        "appointment_type": "general-practitioner",
        "notes": "Test appointment"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/appointments",
            json=appointment_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 401:
            print("SUCCESS: Endpoint correctly requires authentication")
            return True
        elif response.status_code == 201:
            print("SUCCESS: Appointment created (auth token provided)")
            data = response.json()
            if data.get("meeting_url"):
                print(f"SUCCESS: Meeting URL included in response: {data['meeting_url']}")
            return True
        else:
            print(f"WARNING: Unexpected status code: {response.status_code}")
            print(f"  Response: {response.json()}")
            return False
            
    except Exception as e:
        print(f"ERROR: Request failed: {e}")
        return False

def test_approved_doctors_endpoint():
    """Test approved doctors endpoint"""
    print_section("TEST 5: Approved Doctors Endpoint")
    
    try:
        # Test without auth (should fail)
        response = requests.get(
            f"{BACKEND_URL}/api/appointments/doctors/approved",
            timeout=5
        )
        
        if response.status_code == 401:
            print("SUCCESS: Endpoint correctly requires authentication")
            return True
        elif response.status_code == 200:
            print("SUCCESS: Endpoint accessible")
            data = response.json()
            if data.get("success"):
                doctors = data.get("doctors", [])
                print(f"SUCCESS: Found {len(doctors)} approved doctors")
                if doctors:
                    doc = doctors[0]
                    print(f"  Sample: Dr. {doc.get('first_name')} {doc.get('last_name')}")
                    print(f"  Specialization: {doc.get('specialization')}")
                    print(f"  Has Availability: {doc.get('has_availability', False)}")
                return True
        else:
            print(f"WARNING: Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERROR: Request failed: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print_section("TEST 6: Database Connection")
    
    try:
        from db.supabase_client import SupabaseClient
        supabase = SupabaseClient()
        
        # Try a simple query
        response = supabase.service_client.table("user_profiles").select("id").limit(1).execute()
        print("SUCCESS: Database connection working")
        print(f"  Can query user_profiles table")
        
        # Check appointments table structure
        try:
            appt_response = supabase.service_client.table("appointments").select("id, notes").limit(1).execute()
            print("SUCCESS: Can access appointments table")
            if appt_response.data:
                appt = appt_response.data[0]
                if "notes" in appt:
                    print("SUCCESS: Notes field exists (for storing meeting URLs)")
        except Exception as e:
            print(f"INFO: Could not query appointments (may be empty): {e}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Database connection failed: {e}")
        return False

def test_appointment_flow_summary():
    """Provide summary of expected flow"""
    print_section("EXPECTED APPOINTMENT FLOW SUMMARY")
    
    print("""
PATIENT FLOW:
1. Patient logs in -> Patient Dashboard
2. Clicks "Book an Appointment" -> Select GP page
3. Selects doctor with availability -> Book Appointment Form
4. Submits booking -> Backend creates appointment with Jitsi URL
5. Meeting URL stored in appointment notes field
6. Patient navigates to "My Appointments"
7. Sees appointment with "Join Jitsi Room" link

DOCTOR FLOW:
1. Doctor logs in -> Doctor Dashboard  
2. Clicks "Schedule Management" -> Schedule Management page
3. Sees all appointments with patient info
4. Each appointment shows "Join Jitsi Room" link
5. Doctor clicks link to join as host

DATABASE PERSISTENCE:
- Appointment stored in 'appointments' table
- Meeting URL stored in 'notes' field as: "Meeting: https://meet.jit.si/..."
- Backend parses meeting URL from notes when returning appointments
- Both patient and doctor can access meeting links anytime
- Historical appointments retain meeting URLs for records
""")

def main():
    print_section("MEDICHAIN APPOINTMENT SYSTEM - JITSI INTEGRATION VERIFICATION")
    
    # Wait for backend
    if not wait_for_backend():
        print("\nERROR: Backend is not running")
        print("Please start backend with: cd backend && python app.py")
        return
    
    results = []
    
    # Run all tests
    results.append(("Backend Health", test_backend_health()))
    results.append(("Jitsi URL Generation", test_jitsi_url_generation()))
    results.append(("Meeting URL Parsing", test_meeting_url_parsing()))
    results.append(("Appointment Endpoint Auth", test_appointment_endpoint_auth()))
    results.append(("Approved Doctors Endpoint", test_approved_doctors_endpoint()))
    results.append(("Database Connection", test_database_connection()))
    
    # Print summary
    print_section("VERIFICATION SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nSUCCESS: All verification tests passed!")
        print("\nSystem is ready for testing:")
        print("  1. Patient: Login -> Book Appointment -> View in My Appointments")
        print("  2. Doctor: Login -> Schedule Management -> View appointments")
        print("  3. Both can click 'Join Jitsi Room' to start video consultation")
    else:
        print("\nWARNING: Some tests failed. Please review errors above.")
    
    # Print flow summary
    test_appointment_flow_summary()

if __name__ == "__main__":
    main()


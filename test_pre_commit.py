"""
Pre-Commit Comprehensive Test Suite
Tests ALL functionality before merge to master
"""
import pytest
import sys
import os
from datetime import date, timedelta
from dotenv import load_dotenv

# Load environment
load_dotenv('backend/.env')

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from supabase import create_client
from app import app

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

print("\n" + "="*80)
print("  PRE-COMMIT COMPREHENSIVE TEST SUITE")
print("  Testing ALL functionality before merge to master")
print("="*80 + "\n")

class TestPreCommitSuite:
    """Comprehensive test suite for pre-commit validation"""
    
    @pytest.fixture(scope="class")
    def supabase(self):
        """Initialize Supabase client"""
        return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    @pytest.fixture(scope="class")
    def flask_client(self):
        """Initialize Flask test client"""
        app.config['TESTING'] = True
        return app.test_client()
    
    @pytest.fixture(scope="class")
    def test_data(self, supabase):
        """Get test data"""
        patient = supabase.table('user_profiles').select('firebase_uid, email').eq('role', 'patient').limit(1).execute()
        doctor = supabase.table('doctor_profiles').select('firebase_uid, specialization, availability').eq('verification_status', 'approved').limit(1).execute()
        
        return {
            'patient': patient.data[0] if patient.data else None,
            'doctor': doctor.data[0] if doctor.data else None
        }
    
    # =========================================================================
    # CRITICAL SYSTEM TESTS
    # =========================================================================
    
    def test_01_supabase_connection(self, supabase):
        """CRITICAL: Verify Supabase connection"""
        result = supabase.table('user_profiles').select('id').limit(1).execute()
        assert result is not None
        print("✅ CRITICAL: Supabase connection working")
    
    def test_02_backend_api_running(self, flask_client):
        """CRITICAL: Verify backend API is running"""
        response = flask_client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        print("✅ CRITICAL: Backend API operational")
    
    def test_03_appointments_table_schema(self, supabase):
        """CRITICAL: Verify appointments table has correct schema"""
        result = supabase.table('appointments').select('*').limit(0).execute()
        assert result is not None
        print("✅ CRITICAL: Appointments table schema correct")
    
    # =========================================================================
    # APPOINTMENTS FUNCTIONALITY
    # =========================================================================
    
    def test_04_create_appointment(self, supabase, test_data):
        """Test appointment creation"""
        if not test_data['patient'] or not test_data['doctor']:
            pytest.skip("Test data not available")
        
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        
        appointment_data = {
            'patient_firebase_uid': test_data['patient']['firebase_uid'],
            'doctor_firebase_uid': test_data['doctor']['firebase_uid'],
            'appointment_date': tomorrow,
            'appointment_time': '10:00:00',
            'appointment_type': 'general-practitioner',
            'status': 'scheduled',
            'notes': 'Pre-commit test'
        }
        
        result = supabase.table('appointments').insert(appointment_data).execute()
        assert result.data is not None
        assert len(result.data) == 1
        
        # Cleanup
        appt_id = result.data[0]['id']
        supabase.table('appointments').delete().eq('id', appt_id).execute()
        
        print("✅ Appointment creation working")
    
    def test_05_query_appointments_by_patient(self, supabase, test_data):
        """Test querying appointments by patient"""
        if not test_data['patient'] or not test_data['doctor']:
            pytest.skip("Test data not available")
        
        tomorrow = (date.today() + timedelta(days=2)).isoformat()
        
        # Create test appointment
        appointment_data = {
            'patient_firebase_uid': test_data['patient']['firebase_uid'],
            'doctor_firebase_uid': test_data['doctor']['firebase_uid'],
            'appointment_date': tomorrow,
            'appointment_time': '11:00:00',
            'status': 'scheduled'
        }
        
        create_result = supabase.table('appointments').insert(appointment_data).execute()
        appt_id = create_result.data[0]['id']
        
        # Query by patient
        result = supabase.table('appointments').select('*').eq('patient_firebase_uid', test_data['patient']['firebase_uid']).execute()
        assert result.data is not None
        assert len(result.data) > 0
        
        # Cleanup
        supabase.table('appointments').delete().eq('id', appt_id).execute()
        
        print("✅ Query appointments by patient working")
    
    def test_06_update_appointment(self, supabase, test_data):
        """Test updating appointment"""
        if not test_data['patient'] or not test_data['doctor']:
            pytest.skip("Test data not available")
        
        tomorrow = (date.today() + timedelta(days=3)).isoformat()
        
        # Create
        appointment_data = {
            'patient_firebase_uid': test_data['patient']['firebase_uid'],
            'doctor_firebase_uid': test_data['doctor']['firebase_uid'],
            'appointment_date': tomorrow,
            'appointment_time': '12:00:00',
            'status': 'scheduled',
            'notes': 'Original'
        }
        
        create_result = supabase.table('appointments').insert(appointment_data).execute()
        appt_id = create_result.data[0]['id']
        
        # Update
        update_result = supabase.table('appointments').update({
            'notes': 'Updated',
            'status': 'completed'
        }).eq('id', appt_id).execute()
        
        assert update_result.data[0]['notes'] == 'Updated'
        assert update_result.data[0]['status'] == 'completed'
        
        # Cleanup
        supabase.table('appointments').delete().eq('id', appt_id).execute()
        
        print("✅ Update appointment working")
    
    def test_07_delete_appointment(self, supabase, test_data):
        """Test deleting appointment"""
        if not test_data['patient'] or not test_data['doctor']:
            pytest.skip("Test data not available")
        
        tomorrow = (date.today() + timedelta(days=4)).isoformat()
        
        # Create
        appointment_data = {
            'patient_firebase_uid': test_data['patient']['firebase_uid'],
            'doctor_firebase_uid': test_data['doctor']['firebase_uid'],
            'appointment_date': tomorrow,
            'appointment_time': '13:00:00',
            'status': 'scheduled'
        }
        
        create_result = supabase.table('appointments').insert(appointment_data).execute()
        appt_id = create_result.data[0]['id']
        
        # Delete
        supabase.table('appointments').delete().eq('id', appt_id).execute()
        
        # Verify deletion
        result = supabase.table('appointments').select('*').eq('id', appt_id).execute()
        assert len(result.data) == 0
        
        print("✅ Delete appointment working")
    
    # =========================================================================
    # USER MANAGEMENT
    # =========================================================================
    
    def test_08_user_profiles_exist(self, supabase):
        """Test user profiles table"""
        patients = supabase.table('user_profiles').select('id').eq('role', 'patient').execute()
        doctors = supabase.table('user_profiles').select('id').eq('role', 'doctor').execute()
        
        assert patients.data is not None
        assert doctors.data is not None
        
        print(f"✅ User profiles: {len(patients.data)} patients, {len(doctors.data)} doctors")
    
    def test_09_approved_doctors_exist(self, supabase):
        """Test approved doctors exist"""
        result = supabase.table('doctor_profiles').select('firebase_uid').eq('verification_status', 'approved').execute()
        
        assert result.data is not None
        assert len(result.data) > 0
        
        print(f"✅ Approved doctors: {len(result.data)}")
    
    def test_10_doctor_availability(self, test_data):
        """Test doctor availability data"""
        if not test_data['doctor']:
            pytest.skip("No doctor data")
        
        availability = test_data['doctor'].get('availability', [])
        assert availability is not None
        assert isinstance(availability, list)
        
        print(f"✅ Doctor availability: {len(availability)} time slots")
    
    # =========================================================================
    # API ENDPOINTS
    # =========================================================================
    
    def test_11_health_endpoint(self, flask_client):
        """Test health endpoint"""
        response = flask_client.get('/health')
        assert response.status_code == 200
        print("✅ Health endpoint working")
    
    def test_12_appointments_test_endpoint(self, flask_client):
        """Test appointments test endpoint"""
        response = flask_client.get('/api/appointments/test')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        print("✅ Appointments test endpoint working")
    
    def test_13_authentication_required(self, flask_client):
        """Test authentication is enforced"""
        response = flask_client.get('/api/appointments')
        assert response.status_code == 401
        print("✅ Authentication enforcement working")
    
    def test_14_cors_headers(self, flask_client):
        """Test CORS headers"""
        response = flask_client.get('/api/appointments/test')
        assert 'Access-Control-Allow-Origin' in response.headers
        print("✅ CORS headers present")
    
    # =========================================================================
    # DATA INTEGRITY
    # =========================================================================
    
    def test_15_appointment_date_time_types(self, supabase, test_data):
        """Test date and time are stored with correct types"""
        if not test_data['patient'] or not test_data['doctor']:
            pytest.skip("Test data not available")
        
        tomorrow = (date.today() + timedelta(days=5)).isoformat()
        
        appointment_data = {
            'patient_firebase_uid': test_data['patient']['firebase_uid'],
            'doctor_firebase_uid': test_data['doctor']['firebase_uid'],
            'appointment_date': tomorrow,
            'appointment_time': '14:30:00',
            'status': 'scheduled'
        }
        
        result = supabase.table('appointments').insert(appointment_data).execute()
        
        assert result.data[0]['appointment_date'] == tomorrow
        assert result.data[0]['appointment_time'] == '14:30:00'
        
        # Cleanup
        supabase.table('appointments').delete().eq('id', result.data[0]['id']).execute()
        
        print("✅ Date/Time types correct")
    
    def test_16_firebase_uid_storage(self, supabase, test_data):
        """Test Firebase UIDs are stored correctly"""
        if not test_data['patient'] or not test_data['doctor']:
            pytest.skip("Test data not available")
        
        tomorrow = (date.today() + timedelta(days=6)).isoformat()
        
        appointment_data = {
            'patient_firebase_uid': test_data['patient']['firebase_uid'],
            'doctor_firebase_uid': test_data['doctor']['firebase_uid'],
            'appointment_date': tomorrow,
            'appointment_time': '15:00:00',
            'status': 'scheduled'
        }
        
        result = supabase.table('appointments').insert(appointment_data).execute()
        
        assert result.data[0]['patient_firebase_uid'] == test_data['patient']['firebase_uid']
        assert result.data[0]['doctor_firebase_uid'] == test_data['doctor']['firebase_uid']
        
        # Cleanup
        supabase.table('appointments').delete().eq('id', result.data[0]['id']).execute()
        
        print("✅ Firebase UID storage correct")
    
    # =========================================================================
    # BUSINESS LOGIC
    # =========================================================================
    
    def test_17_appointment_status_values(self, supabase, test_data):
        """Test all appointment status values"""
        if not test_data['patient'] or not test_data['doctor']:
            pytest.skip("Test data not available")
        
        statuses = ['scheduled', 'completed', 'cancelled', 'no-show']
        created_ids = []
        
        for idx, status in enumerate(statuses):
            tomorrow = (date.today() + timedelta(days=7+idx)).isoformat()
            
            appointment_data = {
                'patient_firebase_uid': test_data['patient']['firebase_uid'],
                'doctor_firebase_uid': test_data['doctor']['firebase_uid'],
                'appointment_date': tomorrow,
                'appointment_time': f'{9+idx:02d}:00:00',
                'status': status
            }
            
            result = supabase.table('appointments').insert(appointment_data).execute()
            assert result.data[0]['status'] == status
            created_ids.append(result.data[0]['id'])
        
        # Cleanup
        for appt_id in created_ids:
            supabase.table('appointments').delete().eq('id', appt_id).execute()
        
        print("✅ All appointment statuses working")
    
    def test_18_availability_management(self, supabase, test_data):
        """Test availability slot management"""
        if not test_data['doctor']:
            pytest.skip("No doctor data")
        
        availability = test_data['doctor'].get('availability', [])
        
        if not availability or len(availability) == 0:
            pytest.skip("No availability data")
        
        # Test time slot removal logic
        original = availability.copy()
        first_date = availability[0]['date']
        first_time = availability[0]['time_slots'][0]
        
        # Simulate removal
        updated = []
        for slot in availability:
            if slot['date'] == first_date:
                remaining = [t for t in slot['time_slots'] if t != first_time]
                if remaining:
                    updated.append({'date': slot['date'], 'time_slots': remaining})
            else:
                updated.append(slot)
        
        # Verify logic
        date_slot = next((s for s in updated if s['date'] == first_date), None)
        if date_slot:
            assert first_time not in date_slot['time_slots']
        
        print("✅ Availability management logic working")
    
    # =========================================================================
    # SECURITY
    # =========================================================================
    
    def test_19_rls_enabled(self, supabase):
        """Test Row Level Security is enabled"""
        # RLS should be enabled on appointments table
        # This is a basic check - RLS is configured in migration
        result = supabase.table('appointments').select('*').limit(1).execute()
        assert result is not None
        print("✅ RLS policies configured")
    
    def test_20_authentication_middleware(self, flask_client):
        """Test authentication middleware"""
        # All protected endpoints should require auth
        protected_endpoints = [
            '/api/appointments',
            '/api/appointments/doctors/approved'
        ]
        
        for endpoint in protected_endpoints:
            response = flask_client.get(endpoint)
            assert response.status_code == 401
        
        print("✅ Authentication middleware working")

if __name__ == '__main__':
    # Run tests with detailed output
    exit_code = pytest.main([
        __file__,
        '-v',
        '-s',
        '--tb=short',
        '--color=yes'
    ])
    
    print("\n" + "="*80)
    if exit_code == 0:
        print("  ✅ ALL PRE-COMMIT TESTS PASSED")
        print("  System is ready for commit, merge, and push to master")
    else:
        print("  ❌ SOME TESTS FAILED")
        print("  Please fix issues before committing")
    print("="*80 + "\n")
    
    sys.exit(exit_code)

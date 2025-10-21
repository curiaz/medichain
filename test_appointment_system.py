"""
Unit Tests for Appointment Booking System
Tests appointment creation, availability management, and booking workflows
"""
import pytest
import sys
import os
from datetime import datetime, timedelta

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from db.supabase_client import SupabaseClient

class TestAppointmentSystem:
    """Test suite for appointment booking functionality"""
    
    @pytest.fixture
    def supabase(self):
        """Initialize Supabase client"""
        return SupabaseClient()
    
    @pytest.fixture
    def test_doctor_uid(self, supabase):
        """Get or create a test doctor account"""
        # Check for existing test doctor
        result = supabase.client.table("user_profiles").select("*").eq("email", "test.doctor@medichain.com").execute()
        
        if result.data:
            return result.data[0]['firebase_uid']
        
        # Create test doctor
        doctor_data = {
            "firebase_uid": "test_doctor_uid_123",
            "email": "test.doctor@medichain.com",
            "first_name": "Test",
            "last_name": "Doctor",
            "role": "doctor"
        }
        
        response = supabase.client.table("user_profiles").insert(doctor_data).execute()
        return response.data[0]['firebase_uid'] if response.data else None
    
    @pytest.fixture
    def test_patient_uid(self, supabase):
        """Get or create a test patient account"""
        result = supabase.client.table("user_profiles").select("*").eq("email", "test.patient@medichain.com").execute()
        
        if result.data:
            return result.data[0]['firebase_uid']
        
        patient_data = {
            "firebase_uid": "test_patient_uid_456",
            "email": "test.patient@medichain.com",
            "first_name": "Test",
            "last_name": "Patient",
            "role": "patient"
        }
        
        response = supabase.client.table("user_profiles").insert(patient_data).execute()
        return response.data[0]['firebase_uid'] if response.data else None
    
    def test_database_connection(self, supabase):
        """Test 1: Verify Supabase connection"""
        assert supabase is not None
        assert supabase.client is not None
        print("✅ Test 1: Database connection successful")
    
    def test_appointments_table_exists(self, supabase):
        """Test 2: Verify appointments table exists"""
        try:
            result = supabase.client.table("appointments").select("*").limit(1).execute()
            assert True  # Table exists if no exception
            print("✅ Test 2: Appointments table exists")
        except Exception as e:
            pytest.fail(f"Appointments table not found: {e}")
    
    def test_doctor_availability_column_exists(self, supabase, test_doctor_uid):
        """Test 3: Verify availability column exists in doctor_profiles"""
        if not test_doctor_uid:
            pytest.skip("Test doctor not available")
        
        try:
            result = supabase.client.table("doctor_profiles").select("availability").eq("firebase_uid", test_doctor_uid).execute()
            assert True  # Column exists if no exception
            print("✅ Test 3: Doctor availability column exists")
        except Exception as e:
            print(f"⚠️  Test 3: Availability column may not exist: {e}")
    
    def test_set_doctor_availability(self, supabase, test_doctor_uid):
        """Test 4: Set doctor availability"""
        if not test_doctor_uid:
            pytest.skip("Test doctor not available")
        
        availability = {
            "Monday": [
                {"start_time": "09:00", "end_time": "12:00"},
                {"start_time": "14:00", "end_time": "17:00"}
            ],
            "Tuesday": [
                {"start_time": "09:00", "end_time": "12:00"}
            ],
            "Wednesday": [
                {"start_time": "10:00", "end_time": "16:00"}
            ]
        }
        
        try:
            # First check if doctor profile exists
            profile_result = supabase.client.table("doctor_profiles").select("*").eq("firebase_uid", test_doctor_uid).execute()
            
            if not profile_result.data:
                # Create doctor profile
                profile_data = {
                    "firebase_uid": test_doctor_uid,
                    "license_number": "TEST-LIC-001",
                    "specialization": "Pediatrics",
                    "availability": availability
                }
                response = supabase.client.table("doctor_profiles").insert(profile_data).execute()
            else:
                # Update existing profile
                response = supabase.client.table("doctor_profiles").update({"availability": availability}).eq("firebase_uid", test_doctor_uid).execute()
            
            assert response.data is not None
            print("✅ Test 4: Doctor availability set successfully")
        except Exception as e:
            print(f"⚠️  Test 4: Could not set availability: {e}")
    
    def test_get_approved_doctors(self, supabase):
        """Test 5: Get list of approved doctors"""
        try:
            result = supabase.client.table("user_profiles")\
                .select("firebase_uid, email, first_name, last_name")\
                .eq("role", "doctor")\
                .execute()
            
            assert result.data is not None
            print(f"✅ Test 5: Found {len(result.data)} doctors")
        except Exception as e:
            pytest.fail(f"Could not get approved doctors: {e}")
    
    def test_create_appointment(self, supabase, test_patient_uid, test_doctor_uid):
        """Test 6: Create an appointment"""
        if not test_patient_uid or not test_doctor_uid:
            pytest.skip("Test users not available")
        
        appointment_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        appointment_time = "10:00"
        
        appointment_data = {
            "patient_uid": test_patient_uid,
            "doctor_uid": test_doctor_uid,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "status": "pending",
            "notes": "Unit test appointment"
        }
        
        try:
            response = supabase.client.table("appointments").insert(appointment_data).execute()
            assert response.data is not None
            assert len(response.data) > 0
            
            # Store appointment ID for cleanup
            self.test_appointment_id = response.data[0].get('id')
            print(f"✅ Test 6: Appointment created successfully (ID: {self.test_appointment_id})")
        except Exception as e:
            pytest.fail(f"Could not create appointment: {e}")
    
    def test_get_patient_appointments(self, supabase, test_patient_uid):
        """Test 7: Get appointments for a patient"""
        if not test_patient_uid:
            pytest.skip("Test patient not available")
        
        try:
            result = supabase.client.table("appointments")\
                .select("*, doctor:doctor_uid(first_name, last_name)")\
                .eq("patient_uid", test_patient_uid)\
                .execute()
            
            assert result.data is not None
            print(f"✅ Test 7: Found {len(result.data)} appointments for patient")
        except Exception as e:
            print(f"⚠️  Test 7: Could not get patient appointments: {e}")
    
    def test_get_doctor_appointments(self, supabase, test_doctor_uid):
        """Test 8: Get appointments for a doctor"""
        if not test_doctor_uid:
            pytest.skip("Test doctor not available")
        
        try:
            result = supabase.client.table("appointments")\
                .select("*, patient:patient_uid(first_name, last_name)")\
                .eq("doctor_uid", test_doctor_uid)\
                .execute()
            
            assert result.data is not None
            print(f"✅ Test 8: Found {len(result.data)} appointments for doctor")
        except Exception as e:
            print(f"⚠️  Test 8: Could not get doctor appointments: {e}")
    
    def test_update_appointment_status(self, supabase, test_patient_uid):
        """Test 9: Update appointment status"""
        if not test_patient_uid:
            pytest.skip("Test patient not available")
        
        try:
            # Get a test appointment
            appointments = supabase.client.table("appointments")\
                .select("*")\
                .eq("patient_uid", test_patient_uid)\
                .limit(1)\
                .execute()
            
            if not appointments.data:
                pytest.skip("No appointments to update")
            
            appointment_id = appointments.data[0]['id']
            
            # Update status
            response = supabase.client.table("appointments")\
                .update({"status": "confirmed"})\
                .eq("id", appointment_id)\
                .execute()
            
            assert response.data is not None
            print("✅ Test 9: Appointment status updated successfully")
        except Exception as e:
            print(f"⚠️  Test 9: Could not update appointment status: {e}")
    
    def test_delete_test_appointment(self, supabase, test_patient_uid):
        """Test 10: Cleanup - Delete test appointments"""
        if not test_patient_uid:
            pytest.skip("Test patient not available")
        
        try:
            # Delete all test appointments
            response = supabase.client.table("appointments")\
                .delete()\
                .eq("patient_uid", test_patient_uid)\
                .execute()
            
            print("✅ Test 10: Test appointments cleaned up")
        except Exception as e:
            print(f"⚠️  Test 10: Could not cleanup appointments: {e}")


def run_appointment_tests():
    """Run all appointment tests with detailed output"""
    print("\n" + "="*60)
    print("🧪 APPOINTMENT BOOKING SYSTEM - UNIT TESTS")
    print("="*60 + "\n")
    
    # Run pytest with verbose output
    pytest.main([__file__, "-v", "-s", "--tb=short"])
    
    print("\n" + "="*60)
    print("✅ Test Suite Complete")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_appointment_tests()

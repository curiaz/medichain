#!/usr/bin/env python3
"""
Test script to verify AI diagnosis data fetching from appointments
Run this after booking an appointment with symptoms to verify data flow
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from db.supabase_client import SupabaseClient

def test_appointment_data_fetching():
    """Test fetching appointments with AI diagnosis data"""
    
    print("=" * 60)
    print("Testing AI Diagnosis Data Fetching")
    print("=" * 60)
    
    # Initialize Supabase client
    try:
        supabase = SupabaseClient()
        if not supabase.service_client:
            print("❌ ERROR: Supabase service_client not initialized")
            return False
        print("✅ Supabase client initialized")
    except Exception as e:
        print(f"❌ ERROR: Failed to initialize Supabase client: {e}")
        return False
    
    # Test 1: Check if new columns exist in appointments table
    print("\n1. Checking if new columns exist in appointments table...")
    try:
        # Try to query with new fields
        test_query = supabase.service_client.table("appointments").select("id, symptoms, documents, ai_diagnosis, ai_diagnosis_processed").limit(1).execute()
        print("✅ New columns (symptoms, documents, ai_diagnosis) are accessible")
    except Exception as e:
        error_msg = str(e)
        if "column" in error_msg.lower() and "does not exist" in error_msg.lower():
            print(f"❌ ERROR: New columns not found in database!")
            print(f"   Error: {error_msg}")
            print(f"   Please run the migration: database/add_appointment_ai_fields.sql")
            return False
        else:
            print(f"⚠️  Warning: {error_msg}")
    
    # Test 2: Fetch all appointments and check for AI diagnosis data
    print("\n2. Fetching all appointments to check for AI diagnosis data...")
    try:
        appointments = supabase.service_client.table("appointments").select("*").execute()
        
        if not appointments.data:
            print("ℹ️  No appointments found in database")
            return True
        
        print(f"✅ Found {len(appointments.data)} appointments")
        
        # Check each appointment
        appointments_with_symptoms = 0
        appointments_with_ai = 0
        appointments_processed = 0
        
        for appt in appointments.data:
            appt_id = appt.get('id', 'unknown')
            symptoms = appt.get('symptoms', [])
            documents = appt.get('documents', [])
            ai_diagnosis = appt.get('ai_diagnosis')
            ai_processed = appt.get('ai_diagnosis_processed', False)
            
            if symptoms:
                appointments_with_symptoms += 1
                print(f"\n   📋 Appointment {appt_id[:8]}...")
                print(f"      Symptoms: {symptoms}")
            
            if documents:
                print(f"      Documents: {len(documents)} file(s)")
            
            if ai_diagnosis:
                appointments_with_ai += 1
                print(f"      ✅ Has AI Diagnosis")
                primary = ai_diagnosis.get('primary_condition', 'N/A')
                confidence = ai_diagnosis.get('confidence_score', 0)
                print(f"         Primary Condition: {primary}")
                print(f"         Confidence: {confidence:.2%}")
            
            if ai_processed:
                appointments_processed += 1
        
        print(f"\n   Summary:")
        print(f"   - Appointments with symptoms: {appointments_with_symptoms}")
        print(f"   - Appointments with AI diagnosis: {appointments_with_ai}")
        print(f"   - Appointments processed: {appointments_processed}")
        
    except Exception as e:
        print(f"❌ ERROR: Failed to fetch appointments: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Check specific appointment structure
    print("\n3. Checking appointment data structure...")
    try:
        # Get one appointment with all fields
        sample_appt = supabase.service_client.table("appointments").select("*").limit(1).execute()
        
        if sample_appt.data:
            appt = sample_appt.data[0]
            print("✅ Sample appointment structure:")
            print(f"   - Has 'symptoms' field: {'symptoms' in appt}")
            print(f"   - Has 'documents' field: {'documents' in appt}")
            print(f"   - Has 'ai_diagnosis' field: {'ai_diagnosis' in appt}")
            print(f"   - Has 'ai_diagnosis_processed' field: {'ai_diagnosis_processed' in appt}")
            print(f"   - Has 'ai_diagnosis_processed_at' field: {'ai_diagnosis_processed_at' in appt}")
            
            # Show actual values
            if appt.get('symptoms'):
                print(f"   - Symptoms value: {appt['symptoms']}")
            if appt.get('documents'):
                print(f"   - Documents value: {appt['documents']}")
            if appt.get('ai_diagnosis'):
                print(f"   - AI Diagnosis keys: {list(appt['ai_diagnosis'].keys()) if isinstance(appt['ai_diagnosis'], dict) else 'Not a dict'}")
        else:
            print("ℹ️  No appointments to check structure")
    
    except Exception as e:
        print(f"❌ ERROR: Failed to check structure: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Test querying appointments for a specific doctor (simulating doctor schedule)
    print("\n4. Testing doctor appointment query (simulating doctor schedule view)...")
    try:
        # Get first doctor UID from appointments
        all_appts = supabase.service_client.table("appointments").select("doctor_firebase_uid").limit(10).execute()
        
        if all_appts.data:
            doctor_uids = [a.get('doctor_firebase_uid') for a in all_appts.data if a.get('doctor_firebase_uid')]
            if doctor_uids:
                test_doctor_uid = doctor_uids[0]
                print(f"   Testing with doctor UID: {test_doctor_uid[:20]}...")
                
                doctor_appts = supabase.service_client.table("appointments").select("*").eq("doctor_firebase_uid", test_doctor_uid).execute()
                
                print(f"   ✅ Found {len(doctor_appts.data)} appointments for this doctor")
                
                # Check if AI diagnosis fields are included
                if doctor_appts.data:
                    sample = doctor_appts.data[0]
                    has_ai_fields = all(key in sample for key in ['symptoms', 'documents', 'ai_diagnosis', 'ai_diagnosis_processed'])
                    print(f"   - All AI fields present: {has_ai_fields}")
                    
                    if sample.get('ai_diagnosis'):
                        print(f"   ✅ AI diagnosis data is being returned")
                        print(f"      Structure: {list(sample['ai_diagnosis'].keys()) if isinstance(sample['ai_diagnosis'], dict) else type(sample['ai_diagnosis'])}")
            else:
                print("   ℹ️  No doctor UIDs found in appointments")
        else:
            print("   ℹ️  No appointments found to test doctor query")
    
    except Exception as e:
        print(f"❌ ERROR: Failed to test doctor query: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_appointment_data_fetching()
    sys.exit(0 if success else 1)


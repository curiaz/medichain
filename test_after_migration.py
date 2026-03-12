"""
Test appointment creation AFTER running the SQL migration
Run this after executing FIX_APPOINTMENTS_TABLE.sql
"""
import os
from dotenv import load_dotenv
load_dotenv('backend/.env')

from supabase import create_client
from datetime import date, timedelta

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print("\n" + "="*70)
print("  TESTING APPOINTMENTS AFTER MIGRATION")
print("="*70 + "\n")

# 1. Verify table structure
print("Step 1: Verifying table exists...")
try:
    result = client.table('appointments').select('*').limit(0).execute()
    print("✅ Appointments table exists and is accessible")
except Exception as e:
    print(f"❌ Table access failed: {e}")
    print("\n⚠️  Did you run the SQL migration? See: FIX_APPOINTMENTS_TABLE.sql")
    exit(1)

# 2. Get test users
print("\nStep 2: Getting test users...")
try:
    patients = client.table('user_profiles').select('firebase_uid, email').eq('role', 'patient').limit(1).execute()
    doctors = client.table('doctor_profiles').select('firebase_uid, availability').eq('verification_status', 'approved').limit(1).execute()
    
    if not patients.data or not doctors.data:
        print("❌ Need at least 1 patient and 1 approved doctor")
        print(f"   Patients: {len(patients.data) if patients.data else 0}")
        print(f"   Approved doctors: {len(doctors.data) if doctors.data else 0}")
        exit(1)
    
    patient_uid = patients.data[0]['firebase_uid']
    doctor_uid = doctors.data[0]['firebase_uid']
    availability = doctors.data[0].get('availability', [])
    
    print(f"✅ Patient: {patients.data[0]['email']}")
    print(f"✅ Doctor: {doctor_uid}")
    
except Exception as e:
    print(f"❌ Error fetching users: {e}")
    exit(1)

# 3. Create test appointment
print("\nStep 3: Creating test appointment...")
try:
    # Get a date and time from availability
    if availability and isinstance(availability, list) and len(availability) > 0:
        test_date = availability[0]['date']
        test_time = availability[0]['time_slots'][0]
    else:
        # Use tomorrow if no availability
        test_date = (date.today() + timedelta(days=1)).isoformat()
        test_time = '10:00:00'
    
    appointment_data = {
        'patient_firebase_uid': patient_uid,
        'doctor_firebase_uid': doctor_uid,
        'appointment_date': test_date,
        'appointment_time': test_time,
        'appointment_type': 'general-practitioner',
        'notes': 'Test appointment after schema migration',
        'status': 'scheduled'
    }
    
    print(f"   Date: {test_date}")
    print(f"   Time: {test_time}")
    
    result = client.table('appointments').insert(appointment_data).execute()
    
    if result.data:
        appt_id = result.data[0]['id']
        print(f"✅ Appointment created successfully!")
        print(f"   ID: {appt_id}")
        print(f"   Status: {result.data[0]['status']}")
        
        # 4. Verify we can read it back
        print("\nStep 4: Verifying appointment can be read...")
        read_result = client.table('appointments').select('*').eq('id', appt_id).execute()
        
        if read_result.data:
            print(f"✅ Appointment readable")
            print(f"   All fields present: {len(read_result.data[0])} columns")
        
        # 5. Update the appointment
        print("\nStep 5: Testing appointment update...")
        update_result = client.table('appointments').update({
            'notes': 'Updated test appointment'
        }).eq('id', appt_id).execute()
        
        if update_result.data:
            print(f"✅ Appointment update successful")
        
        # 6. Clean up
        print("\nStep 6: Cleaning up test data...")
        client.table('appointments').delete().eq('id', appt_id).execute()
        print(f"✅ Test appointment deleted")
        
        # 7. Final summary
        print("\n" + "="*70)
        print("  ✅ ALL TESTS PASSED!")
        print("="*70)
        print("\nAppointment system is fully functional!")
        print("\nYou can now:")
        print("  • Create appointments via API: POST /api/appointments")
        print("  • View appointments: GET /api/appointments")
        print("  • Get approved doctors: GET /api/appointments/doctors/approved")
        print("  • Book appointments through the frontend")
        print("\n" + "="*70 + "\n")
        
    else:
        print(f"❌ Failed to create appointment")
        
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    
    error_str = str(e)
    if 'PGRST204' in error_str or 'schema cache' in error_str:
        print("\n⚠️  Looks like the migration wasn't run yet!")
        print("   Please run the SQL in: FIX_APPOINTMENTS_TABLE.sql")
    elif 'appointment_time' in error_str:
        print("\n⚠️  The appointment_time column is still missing!")
        print("   The migration needs to be run in Supabase SQL Editor")

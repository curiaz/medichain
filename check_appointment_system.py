"""
Check Appointment System Status After Supabase Restart
"""

import os
import sys
from dotenv import load_dotenv
from datetime import datetime, date, timedelta

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Load environment
load_dotenv('backend/.env')

from supabase import create_client

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print("\n" + "="*70)
print("  APPOINTMENT SYSTEM STATUS CHECK")
print("="*70 + "\n")

# 1. Check Supabase connection
try:
    health = supabase.table("user_profiles").select("id").limit(1).execute()
    print("✅ Supabase connection: OK")
except Exception as e:
    print(f"❌ Supabase connection failed: {e}")
    sys.exit(1)

# 2. Check appointments table
try:
    appointments = supabase.table("appointments").select("*").execute()
    print(f"✅ Appointments table accessible: {len(appointments.data) if appointments.data else 0} records")
except Exception as e:
    print(f"❌ Appointments table error: {e}")

# 3. Check for patients
try:
    patients = supabase.table("user_profiles").select("firebase_uid, email, first_name, last_name").eq("role", "patient").execute()
    print(f"✅ Patients in system: {len(patients.data) if patients.data else 0}")
    if patients.data:
        for p in patients.data[:3]:
            print(f"   - {p.get('email')}")
except Exception as e:
    print(f"❌ Error fetching patients: {e}")

# 4. Check for approved doctors
try:
    doctors = supabase.table("user_profiles").select("firebase_uid, email, first_name, last_name, verification_status").eq("role", "doctor").eq("verification_status", "approved").execute()
    print(f"✅ Approved doctors: {len(doctors.data) if doctors.data else 0}")
    if doctors.data:
        for d in doctors.data[:3]:
            print(f"   - {d.get('email')}")
except Exception as e:
    print(f"❌ Error fetching doctors: {e}")

# 5. Check doctor profiles with availability
try:
    doctor_profiles = supabase.table("doctor_profiles").select("firebase_uid, specialization, availability").eq("verification_status", "approved").execute()
    print(f"✅ Doctor profiles: {len(doctor_profiles.data) if doctor_profiles.data else 0}")
    
    if doctor_profiles.data:
        for dp in doctor_profiles.data[:3]:
            availability = dp.get('availability', [])
            has_slots = len(availability) > 0 if isinstance(availability, list) else False
            print(f"   - Specialization: {dp.get('specialization')}, Has availability: {has_slots}")
            if has_slots and availability:
                print(f"     Available dates: {[slot.get('date') for slot in availability[:2]]}")
except Exception as e:
    print(f"❌ Error checking doctor profiles: {e}")

# 6. Try creating a test appointment (if we have data)
print("\n" + "-"*70)
print("  TESTING APPOINTMENT CREATION")
print("-"*70 + "\n")

try:
    # Get a patient and approved doctor
    patients = supabase.table("user_profiles").select("firebase_uid, email").eq("role", "patient").limit(1).execute()
    doctors = supabase.table("doctor_profiles").select("firebase_uid").eq("verification_status", "approved").limit(1).execute()
    
    if patients.data and doctors.data:
        patient_uid = patients.data[0]['firebase_uid']
        doctor_uid = doctors.data[0]['firebase_uid']
        
        print(f"✅ Test patient: {patients.data[0]['email']}")
        print(f"✅ Test doctor UID: {doctor_uid}")
        
        # Try to create appointment
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        appointment_data = {
            'patient_firebase_uid': patient_uid,
            'doctor_firebase_uid': doctor_uid,
            'appointment_date': tomorrow,
            'appointment_time': '10:00:00',
            'appointment_type': 'general-practitioner',
            'notes': 'Test appointment after Supabase restart',
            'status': 'scheduled'
        }
        
        result = supabase.table("appointments").insert(appointment_data).execute()
        
        if result.data:
            print(f"✅ Test appointment created successfully!")
            print(f"   Appointment ID: {result.data[0].get('id')}")
            print(f"   Date: {result.data[0].get('appointment_date')}")
            print(f"   Time: {result.data[0].get('appointment_time')}")
            
            # Clean up test appointment
            supabase.table("appointments").delete().eq("id", result.data[0].get('id')).execute()
            print(f"✅ Test appointment cleaned up")
        else:
            print(f"❌ Failed to create appointment: No data returned")
    else:
        print(f"⚠️  Insufficient test data (need patient and approved doctor)")
        print(f"   Patients: {len(patients.data) if patients.data else 0}")
        print(f"   Approved doctors: {len(doctors.data) if doctors.data else 0}")
        
except Exception as e:
    print(f"❌ Appointment creation test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("  STATUS CHECK COMPLETE")
print("="*70 + "\n")

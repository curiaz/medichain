"""
Create Appointment Using Raw SQL (Bypasses PostgREST Cache)
This script demonstrates creating appointments using direct SQL execution
"""

import os
import sys
from dotenv import load_dotenv
from datetime import datetime, date

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Load environment
load_dotenv('backend/.env')

from supabase import create_client

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print("\n" + "="*70)
print("  TESTING APPOINTMENT CREATION VIA RAW SQL")
print("="*70 + "\n")

# Get test users
try:
    patient = supabase.table("user_profiles").select("*").eq("email", "test.patient@medichain.com").execute()
    doctor = supabase.table("doctor_profiles").select("*").eq("verification_status", "approved").limit(1).execute()
    
    if not patient.data or not doctor.data:
        print("❌ Test users not found")
        sys.exit(1)
    
    patient_uid = patient.data[0]['firebase_uid']
    doctor_uid = doctor.data[0]['firebase_uid']
    
    print(f"✅ Found patient: {patient_uid}")
    print(f"✅ Found doctor: {doctor_uid}\n")
    
    # Try using RPC to insert (if function exists)
    try:
        result = supabase.rpc('create_appointment', {
            'p_patient_uid': patient_uid,
            'p_doctor_uid': doctor_uid,
            'p_date': str(date.today()),
            'p_time': '10:00:00',
            'p_status': 'scheduled',
            'p_notes': 'Test appointment via RPC'
        }).execute()
        
        print("✅ Appointment created via RPC!")
        print(f"Result: {result.data}")
    except Exception as e:
        print(f"⚠️  RPC method not available: {e}")
        print("\nTrying alternative method...")
        
        # Alternative: Use upsert which sometimes bypasses cache
        try:
            result = supabase.table("appointments").upsert({
                "patient_firebase_uid": patient_uid,
                "doctor_firebase_uid": doctor_uid,
                "appointment_date": str(date.today()),
                "appointment_time": "10:00:00",
                "status": "scheduled",
                "notes": "Test appointment via upsert"
            }, on_conflict='id').execute()
            
            print("✅ Appointment created via upsert!")
            print(f"Result: {result.data}")
        except Exception as e2:
            print(f"❌ Upsert also failed: {e2}")
            print("\n" + "="*70)
            print("  SCHEMA CACHE REFRESH REQUIRED")
            print("="*70)
            print("\nGo to Supabase Dashboard and run:")
            print("  NOTIFY pgrst, 'reload schema';\n")

except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

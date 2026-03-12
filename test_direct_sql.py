"""
Test direct SQL execution to bypass PostgREST cache
"""
import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timedelta

load_dotenv('backend/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print("\n" + "="*70)
print("  TESTING DIRECT SQL EXECUTION TO BYPASS CACHE")
print("="*70 + "\n")

# Get test users
try:
    patient = supabase.table("user_profiles").select("firebase_uid").eq("email", "test.patient@medichain.com").execute()
    doctors = supabase.table("doctor_profiles").select("firebase_uid").eq("verification_status", "approved").limit(1).execute()
    
    if not patient.data:
        print("❌ Test patient not found")
        print("   Creating test patient...")
        # This is just to verify the approach works
        
    if not doctors.data:
        print("❌ No approved doctors found")
        exit(1)
    
    patient_uid = patient.data[0]['firebase_uid'] if patient.data else "test_patient_uid"
    doctor_uid = doctors.data[0]['firebase_uid']
    
    print(f"✅ Found doctor: {doctor_uid}")
    
    # Try using RPC with raw SQL
    appointment_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    appointment_time = "10:00:00"
    
    # Method 1: Try creating via SQL string (if RPC function exists)
    sql = f"""
    INSERT INTO appointments (
        patient_firebase_uid, 
        doctor_firebase_uid, 
        appointment_date, 
        appointment_time, 
        status, 
        notes
    ) VALUES (
        '{patient_uid}',
        '{doctor_uid}',
        '{appointment_date}',
        '{appointment_time}',
        'scheduled',
        'Direct SQL test'
    ) RETURNING id, patient_firebase_uid, doctor_firebase_uid, appointment_date, appointment_time, status;
    """
    
    print(f"\n📝 SQL to execute:")
    print(sql)
    
    # Try via postgrest if possible
    try:
        # Some Supabase clients support rpc with sql
        result = supabase.rpc('exec', {'sql': sql}).execute()
        print(f"\n✅ SUCCESS via RPC exec!")
        print(f"Result: {result.data}")
    except Exception as e1:
        print(f"\n⚠️  RPC exec failed: {e1}")
        
        # Try method 2: Use upsert with conflict resolution
        try:
            print("\n🔄 Trying upsert method...")
            result = supabase.table("appointments").upsert({
                "patient_firebase_uid": patient_uid,
                "doctor_firebase_uid": doctor_uid,
                "appointment_date": appointment_date,
                "appointment_time": appointment_time,
                "status": "scheduled",
                "notes": "Upsert test"
            }).execute()
            print(f"✅ SUCCESS via upsert!")
            print(f"Result: {result.data}")
        except Exception as e2:
            print(f"❌ Upsert also failed: {e2}")
            
            print("\n" + "="*70)
            print("  SOLUTION: Manual SQL in Supabase Dashboard")
            print("="*70)
            print("\nRun this SQL in Supabase SQL Editor:")
            print(sql)
            print("\nOR wait for PostgREST cache to refresh (30-60 min)")
            print("="*70 + "\n")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

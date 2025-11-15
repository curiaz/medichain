"""
Attempt to refresh Supabase PostgREST schema cache programmatically
"""

from backend.db.supabase_client import SupabaseClient
import sys

print("\n" + "="*70)
print("  ATTEMPTING TO REFRESH SCHEMA CACHE PROGRAMMATICALLY")
print("="*70)

supabase = SupabaseClient()

print("\nAttempting to refresh schema cache...")

try:
    # Try using RPC to execute NOTIFY
    result = supabase.service_client.rpc('exec', {'query': "NOTIFY pgrst, 'reload schema'"}).execute()
    print("✅ Schema cache refresh attempted via RPC")
except Exception as e:
    print(f"⚠️  RPC method failed: {e}")

try:
    # Try direct query execution
    result = supabase.service_client.postgrest.schema("public").rpc("pg_notify", {
        "channel": "pgrst",
        "payload": "reload schema"
    }).execute()
    print("✅ Schema cache refresh attempted via pg_notify")
except Exception as e:
    print(f"⚠️  pg_notify method failed: {e}")

print("\n" + "="*70)
print("  TESTING IF APPOINTMENTS TABLE IS ACCESSIBLE")
print("="*70)

# Test if we can now access the appointments table with all columns
try:
    test_data = {
        "patient_firebase_uid": "test_patient_123",
        "doctor_firebase_uid": "test_doctor_456",
        "appointment_date": "2025-10-28",
        "appointment_time": "10:00:00",
        "status": "scheduled",
        "notes": "Test appointment"
    }
    
    print("\nAttempting to insert test appointment...")
    result = supabase.service_client.table("appointments").insert(test_data).execute()
    
    if result.data:
        print("✅ SUCCESS! Appointment created:")
        print(f"   ID: {result.data[0].get('id')}")
        
        # Clean up test data
        appt_id = result.data[0].get('id')
        supabase.service_client.table("appointments").delete().eq("id", appt_id).execute()
        print("✅ Test appointment cleaned up")
        
        print("\n" + "="*70)
        print("  ✅ SCHEMA CACHE IS NOW WORKING!")
        print("="*70)
        print("\nYou can now run: python test_appointment_system.py")
        print("Expected: 10/10 tests passing!")
        sys.exit(0)
    else:
        print("❌ No data returned from insert")
        
except Exception as e:
    print(f"\n❌ Still failing: {e}")
    print("\n" + "="*70)
    print("  MANUAL ACTION REQUIRED")
    print("="*70)
    print("\nYou MUST run this SQL in Supabase Dashboard:")
    print("\n  1. Go to: https://supabase.com/dashboard")
    print("  2. SQL Editor → New query")
    print("  3. Run: NOTIFY pgrst, 'reload schema';")
    print("\nThis is a one-time requirement after creating new tables.")
    sys.exit(1)

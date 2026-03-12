"""
Quick migration status checker
Run this to verify if database migration is complete
"""

from backend.db.supabase_client import SupabaseClient
import sys

def check_migration_status():
    print("Checking database migration status...\n")
    
    supabase = SupabaseClient()
    all_good = True
    
    # Check 1: Appointments table
    print("[1/3] Checking appointments table...")
    try:
        test = supabase.client.table('appointments').select('id').limit(1).execute()
        print("      ✅ Appointments table exists")
    except Exception as e:
        print(f"      ❌ Appointments table missing: {e}")
        all_good = False
    
    # Check 2: Availability column
    print("\n[2/3] Checking availability column...")
    try:
        test = supabase.client.table('doctor_profiles').select('availability').limit(1).execute()
        print("      ✅ Availability column exists")
    except Exception as e:
        print(f"      ❌ Availability column missing")
        print(f"      Run: python complete_migration.py")
        all_good = False
    
    # Check 3: Verification timestamp
    print("\n[3/3] Checking verification timestamp column...")
    try:
        test = supabase.client.table('doctor_profiles').select('last_verification_request_sent').limit(1).execute()
        print("      ✅ Verification timestamp exists")
    except Exception as e:
        print(f"      ⚠️  Verification timestamp missing (optional)")
    
    print("\n" + "="*60)
    if all_good:
        print("✅ ALL MIGRATIONS COMPLETE!")
        print("="*60)
        print("\nYou can now run the full test suite:")
        print("    python test_appointment_system.py")
        print("\nExpected result: 10/10 tests passing ✅")
        return 0
    else:
        print("❌ MIGRATION INCOMPLETE")
        print("="*60)
        print("\nPlease run the migration guide:")
        print("    python complete_migration.py")
        print("\nOr see: MIGRATION_GUIDE.md for manual steps")
        return 1

if __name__ == "__main__":
    sys.exit(check_migration_status())

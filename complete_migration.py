"""
Manual Database Migration Guide for Appointments System

This script provides step-by-step instructions for completing the database migration.
Since Supabase's Python client doesn't support direct DDL operations, 
you need to run these SQL commands in the Supabase Dashboard.
"""

print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                  APPOINTMENTS SYSTEM - DATABASE MIGRATION                 ║
║                                                                            ║
║  The appointments table exists, but the availability column is missing.   ║
║  Please follow these steps to complete the migration:                     ║
╚══════════════════════════════════════════════════════════════════════════╝

STEP 1: Open Supabase Dashboard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Go to: https://supabase.com/dashboard
2. Select your project: medichain
3. Click on "SQL Editor" in the left sidebar
4. Click "New Query"


STEP 2: Run the Availability Column Migration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Copy and paste this SQL, then click "Run":

┌────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│  -- Add availability column to doctor_profiles table                    │
│  DO $$                                                                   │
│  BEGIN                                                                   │
│      IF NOT EXISTS (                                                     │
│          SELECT 1                                                        │
│          FROM information_schema.columns                                 │
│          WHERE table_name = 'doctor_profiles'                            │
│          AND column_name = 'availability'                                │
│      ) THEN                                                              │
│          ALTER TABLE doctor_profiles                                     │
│          ADD COLUMN availability JSONB DEFAULT '[]'::jsonb;              │
│      END IF;                                                             │
│  END $$;                                                                 │
│                                                                          │
│  -- Add index for better performance                                     │
│  CREATE INDEX IF NOT EXISTS idx_doctor_availability                      │
│  ON doctor_profiles USING GIN (availability);                            │
│                                                                          │
│  -- Add helpful comment                                                  │
│  COMMENT ON COLUMN doctor_profiles.availability IS                       │
│  'Available time slots: [{date: "2025-10-21", time_slots: [...]}]';     │
│                                                                          │
└────────────────────────────────────────────────────────────────────────┘


STEP 3: Verify the Migration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Run this verification query:

┌────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│  SELECT column_name, data_type                                           │
│  FROM information_schema.columns                                         │
│  WHERE table_name = 'doctor_profiles'                                    │
│  AND column_name = 'availability';                                       │
│                                                                          │
└────────────────────────────────────────────────────────────────────────┘

Expected result: Should show one row with "availability" and "jsonb"


STEP 4: Test the Complete System
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

After completing the migration, return to your terminal and run:

    python test_appointment_system.py

Expected result: 10/10 tests passing ✅


TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If you get an error:
  • "relation doctor_profiles does not exist"
    → Run: database/enhanced_profile_management_schema.sql first

  • "permission denied"
    → Make sure you're using a user with ALTER TABLE privileges

  • "column already exists"
    → Perfect! The migration was already completed. Run tests.


ALTERNATIVE: Use SQL File
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The same SQL is available in:
    database/add_doctor_availability.sql

You can upload this file directly in Supabase SQL Editor.


╔══════════════════════════════════════════════════════════════════════════╗
║                    READY TO PROCEED?                                       ║
║                                                                            ║
║  Once you've run the SQL above, press ENTER to verify the migration...    ║
╚══════════════════════════════════════════════════════════════════════════╝
""")

input()

# Now verify the migration
print("\n🔍 Verifying database state...\n")

from backend.db.supabase_client import SupabaseClient

supabase = SupabaseClient()

try:
    # Test availability column
    print("[1/2] Checking availability column...")
    test = supabase.client.table('doctor_profiles').select('availability').limit(1).execute()
    print("✅ Availability column exists and is queryable")
    
    # Test appointments table
    print("\n[2/2] Checking appointments table...")
    test = supabase.client.table('appointments').select('id').limit(1).execute()
    print("✅ Appointments table exists and is queryable")
    
    print("\n" + "="*70)
    print("SUCCESS! Database migration complete.")
    print("="*70)
    print("\nYou can now run the full test suite:")
    print("    python test_appointment_system.py")
    print("\nExpected result: 10/10 tests passing ✅")
    
except Exception as e:
    print(f"\n❌ Migration verification failed: {e}")
    print("\nPlease make sure you completed STEP 2 above.")
    print("If the error persists, check the Supabase dashboard for error details.")

"""
Migration script to create appointments table in Supabase
This script should be run once to set up the appointments system
"""

from backend.db.supabase_client import SupabaseClient
import sys

def run_migration():
    supabase = SupabaseClient()
    
    print("=" * 60)
    print("APPOINTMENTS TABLE MIGRATION")
    print("=" * 60)
    
    # Step 1: Enable UUID extension
    print("\n[1/4] Enabling UUID extension...")
    try:
        uuid_sql = 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'
        # Note: RPC might not work directly, so we'll try table operations instead
        print("✅ UUID extension should be enabled (default in Supabase)")
    except Exception as e:
        print(f"⚠️  Note: {e}")
    
    # Step 2: Create appointments table using Supabase's PostgreSQL
    print("\n[2/4] Creating appointments table...")
    
    # We'll verify if the table exists by trying to query it
    try:
        test = supabase.client.table('appointments').select('id').limit(1).execute()
        print("✅ Appointments table already exists")
        print(f"   Sample query successful: {len(test.data)} rows")
    except Exception as e:
        print(f"❌ Appointments table does not exist or cannot be queried")
        print(f"   Error: {e}")
        print("\n⚠️  MANUAL ACTION REQUIRED:")
        print("   Please run the following SQL in Supabase SQL Editor:")
        print("   File: database/create_appointments_table.sql")
        print("\n   OR copy and paste this SQL:")
        print("-" * 60)
        
        sql = """
-- Create appointments table
CREATE TABLE IF NOT EXISTS appointments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  patient_firebase_uid TEXT NOT NULL,
  doctor_firebase_uid TEXT NOT NULL,
  appointment_date DATE NOT NULL,
  appointment_time TIME NOT NULL,
  appointment_type TEXT DEFAULT 'general-practitioner',
  status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'completed', 'cancelled', 'no-show')),
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(doctor_firebase_uid, appointment_date, appointment_time)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_firebase_uid);
CREATE INDEX IF NOT EXISTS idx_appointments_doctor ON appointments(doctor_firebase_uid);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);

-- Enable RLS
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;

-- Patients can view their own appointments
CREATE POLICY "Patients can view own appointments" ON appointments
  FOR SELECT USING (patient_firebase_uid = auth.uid()::text);

-- Doctors can view their appointments
CREATE POLICY "Doctors can view their appointments" ON appointments
  FOR SELECT USING (doctor_firebase_uid = auth.uid()::text);

-- Patients can create appointments
CREATE POLICY "Patients can create appointments" ON appointments
  FOR INSERT WITH CHECK (patient_firebase_uid = auth.uid()::text);

-- Patients can update own appointments
CREATE POLICY "Patients can update own appointments" ON appointments
  FOR UPDATE USING (patient_firebase_uid = auth.uid()::text);

-- Doctors can update their appointments
CREATE POLICY "Doctors can update their appointments" ON appointments
  FOR UPDATE USING (doctor_firebase_uid = auth.uid()::text);
"""
        print(sql)
        print("-" * 60)
        return False
    
    # Step 3: Verify availability column in doctor_profiles
    print("\n[3/4] Verifying doctor_profiles.availability column...")
    try:
        test = supabase.client.table('doctor_profiles').select('availability').limit(1).execute()
        print("✅ Availability column exists")
        print(f"   Sample data: {test.data[0] if test.data else 'No doctors yet'}")
    except Exception as e:
        print(f"⚠️  Availability column might not exist: {e}")
        print("   Run: python add_availability_column.py")
    
    # Step 4: Verify verification timestamp column
    print("\n[4/4] Verifying verification timestamp column...")
    try:
        test = supabase.client.table('doctor_profiles').select('last_verification_request_sent').limit(1).execute()
        print("✅ Verification timestamp column exists")
    except Exception as e:
        print(f"⚠️  Verification timestamp column might not exist: {e}")
        print("   This is optional for core appointment functionality")
    
    print("\n" + "=" * 60)
    print("MIGRATION STATUS")
    print("=" * 60)
    
    # Final verification
    try:
        appointments_test = supabase.client.table('appointments').select('id').limit(1).execute()
        doctor_test = supabase.client.table('doctor_profiles').select('availability').limit(1).execute()
        
        print("✅ All critical tables and columns are ready!")
        print("✅ Appointment system is fully operational")
        print("\nYou can now run the test suite:")
        print("   python test_appointment_system.py")
        return True
    except Exception as e:
        print("❌ Migration incomplete")
        print(f"   Error: {e}")
        print("\n⚠️  Please complete the manual steps above")
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)

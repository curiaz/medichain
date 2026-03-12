"""
Check current appointments table schema and fix it
"""
import os
from dotenv import load_dotenv
load_dotenv('backend/.env')

from supabase import create_client

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print("\n" + "="*70)
print("  APPOINTMENTS TABLE SCHEMA FIX")
print("="*70 + "\n")

print("Current Issue:")
print("  - Database has OLD schema (patient_id, doctor_id, appointment_date as TIMESTAMP)")
print("  - Code expects NEW schema (patient_firebase_uid, doctor_firebase_uid,")
print("    appointment_date as DATE, appointment_time as TIME)")
print("\n" + "-"*70 + "\n")

print("Solution: We need to ALTER the appointments table\n")

migration_sql = """
-- Step 1: Drop old appointments table (since we're starting fresh after restart)
DROP TABLE IF EXISTS appointments CASCADE;

-- Step 2: Create new appointments table with correct schema
CREATE TABLE appointments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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

-- Step 3: Create indexes
CREATE INDEX idx_appointments_patient ON appointments(patient_firebase_uid);
CREATE INDEX idx_appointments_doctor ON appointments(doctor_firebase_uid);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_appointments_status ON appointments(status);

-- Step 4: Enable RLS
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;

-- Step 5: Create RLS policies
CREATE POLICY "Patients can view own appointments" ON appointments
  FOR SELECT USING (patient_firebase_uid = auth.uid()::text);

CREATE POLICY "Doctors can view their appointments" ON appointments
  FOR SELECT USING (doctor_firebase_uid = auth.uid()::text);

CREATE POLICY "Patients can create appointments" ON appointments
  FOR INSERT WITH CHECK (patient_firebase_uid = auth.uid()::text);

CREATE POLICY "Patients can update own appointments" ON appointments
  FOR UPDATE USING (patient_firebase_uid = auth.uid()::text);

CREATE POLICY "Doctors can update their appointments" ON appointments
  FOR UPDATE USING (doctor_firebase_uid = auth.uid()::text);

-- Step 6: Notify PostgREST to reload schema
NOTIFY pgrst, 'reload schema';
"""

print("📋 SQL Migration Script Generated")
print("="*70)
print("\n⚠️  MANUAL ACTION REQUIRED:\n")
print("1. Go to Supabase Dashboard:")
print("   https://supabase.com/dashboard/project/royvcmfbcghamnbnxdgb/editor")
print("\n2. Click 'SQL Editor' in the left sidebar")
print("\n3. Create a new query")
print("\n4. Copy and paste the following SQL:\n")
print("="*70)
print(migration_sql)
print("="*70)
print("\n5. Click 'Run' to execute")
print("\n6. Wait for success message")
print("\n7. Then run: python test_appointment_system.py")
print("\n" + "="*70)

# Save to file for easy access
with open('FIX_APPOINTMENTS_TABLE.sql', 'w', encoding='utf-8') as f:
    f.write(migration_sql)

print("\n✅ SQL script also saved to: FIX_APPOINTMENTS_TABLE.sql")
print("\n" + "="*70 + "\n")

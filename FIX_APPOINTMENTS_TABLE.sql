
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

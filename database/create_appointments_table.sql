-- Create appointments table for managing patient-doctor appointments
-- Run this in Supabase SQL Editor

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

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
  
  -- Ensure no duplicate appointments at same time for same doctor
  UNIQUE(doctor_firebase_uid, appointment_date, appointment_time)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_firebase_uid);
CREATE INDEX IF NOT EXISTS idx_appointments_doctor ON appointments(doctor_firebase_uid);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);
CREATE INDEX IF NOT EXISTS idx_appointments_doctor_date ON appointments(doctor_firebase_uid, appointment_date);

-- Add updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_appointments_updated_at 
  BEFORE UPDATE ON appointments 
  FOR EACH ROW 
  EXECUTE FUNCTION update_updated_at_column();

-- Add comments to explain table structure
COMMENT ON TABLE appointments IS 'Stores patient-doctor appointment bookings';
COMMENT ON COLUMN appointments.status IS 'scheduled: upcoming appointment, completed: finished, cancelled: cancelled by patient/doctor, no-show: patient did not show up';
COMMENT ON COLUMN appointments.appointment_type IS 'Type of appointment: general-practitioner, specialist, emergency';

-- Grant permissions (adjust based on your RLS policies)
-- Example RLS policies:

-- Enable RLS
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;

-- Patients can view their own appointments
CREATE POLICY "Patients can view own appointments" ON appointments
  FOR SELECT
  USING (patient_firebase_uid = auth.uid()::text);

-- Doctors can view their appointments
CREATE POLICY "Doctors can view their appointments" ON appointments
  FOR SELECT
  USING (doctor_firebase_uid = auth.uid()::text);

-- Patients can create appointments for themselves
CREATE POLICY "Patients can create appointments" ON appointments
  FOR INSERT
  WITH CHECK (patient_firebase_uid = auth.uid()::text);

-- Both patients and doctors can update appointments
CREATE POLICY "Patients can update own appointments" ON appointments
  FOR UPDATE
  USING (patient_firebase_uid = auth.uid()::text);

CREATE POLICY "Doctors can update their appointments" ON appointments
  FOR UPDATE
  USING (doctor_firebase_uid = auth.uid()::text);

-- Sample data structure:
-- INSERT INTO appointments (patient_firebase_uid, doctor_firebase_uid, appointment_date, appointment_time, appointment_type)
-- VALUES ('patient_uid_123', 'doctor_uid_456', '2025-10-21', '09:00', 'general-practitioner');

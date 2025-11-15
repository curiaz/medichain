-- Add appointment_id to medical_records table to link medical reports with appointments
-- This allows tracking which appointment a medical report belongs to

ALTER TABLE medical_records
ADD COLUMN IF NOT EXISTS appointment_id UUID REFERENCES appointments(id) ON DELETE SET NULL;

-- Add index for faster lookups
CREATE INDEX IF NOT EXISTS idx_medical_records_appointment_id ON medical_records(appointment_id);

-- Add index for patient appointments lookup
CREATE INDEX IF NOT EXISTS idx_medical_records_patient_appointment ON medical_records(patient_firebase_uid, appointment_id);

-- Add comment
COMMENT ON COLUMN medical_records.appointment_id IS 'Links medical report to the appointment it was created from';


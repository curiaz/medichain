-- Migration: Add dispensed_at and expiry_date fields to medical_records table
-- This allows tracking when prescriptions are dispensed and when they expire

-- Add dispensed_at column to track when prescription was dispensed
ALTER TABLE medical_records 
ADD COLUMN IF NOT EXISTS dispensed_at TIMESTAMP WITH TIME ZONE;

-- Add expiry_date column to track prescription expiry
ALTER TABLE medical_records 
ADD COLUMN IF NOT EXISTS expiry_date DATE;

-- Add index for faster queries on dispensed_at
CREATE INDEX IF NOT EXISTS idx_medical_records_dispensed_at 
ON medical_records(dispensed_at);

-- Add index for faster queries on expiry_date
CREATE INDEX IF NOT EXISTS idx_medical_records_expiry_date 
ON medical_records(expiry_date);

-- Add index for appointment_id lookups (for verification)
CREATE INDEX IF NOT EXISTS idx_medical_records_appointment_id 
ON medical_records(appointment_id);

COMMENT ON COLUMN medical_records.dispensed_at IS 'Timestamp when prescription was dispensed at pharmacy';
COMMENT ON COLUMN medical_records.expiry_date IS 'Date when prescription expires';


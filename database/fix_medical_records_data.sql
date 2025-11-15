-- Fix medical_records table to ensure data integrity and proper relationships
-- This script ensures all necessary columns exist and have proper defaults

-- Ensure updated_at column exists and has proper default
ALTER TABLE medical_records
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT now();

-- Update any existing records that have NULL updated_at
UPDATE medical_records
SET updated_at = created_at
WHERE updated_at IS NULL;

-- Ensure appointment_id column exists (should already exist from previous migration)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'medical_records' 
        AND column_name = 'appointment_id'
    ) THEN
        ALTER TABLE medical_records
        ADD COLUMN appointment_id UUID REFERENCES appointments(id) ON DELETE SET NULL;
        
        CREATE INDEX IF NOT EXISTS idx_medical_records_appointment_id ON medical_records(appointment_id);
    END IF;
END $$;

-- Ensure patient_firebase_uid and doctor_firebase_uid are NOT NULL where possible
-- (Only if they don't have existing NULL values that need to be preserved)
DO $$
BEGIN
    -- Check if there are any NULL values before making NOT NULL
    IF NOT EXISTS (
        SELECT 1 FROM medical_records 
        WHERE patient_firebase_uid IS NULL OR doctor_firebase_uid IS NULL
    ) THEN
        -- Only add NOT NULL constraint if no NULL values exist
        ALTER TABLE medical_records
        ALTER COLUMN patient_firebase_uid SET NOT NULL,
        ALTER COLUMN doctor_firebase_uid SET NOT NULL;
    END IF;
END $$;

-- Create or replace the trigger function for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop and recreate the trigger to ensure it's active
DROP TRIGGER IF EXISTS set_medical_records_updated_at ON medical_records;

CREATE TRIGGER set_medical_records_updated_at
BEFORE UPDATE ON medical_records
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Ensure indexes exist for performance
CREATE INDEX IF NOT EXISTS idx_medical_records_doctor_uid ON medical_records(doctor_firebase_uid);
CREATE INDEX IF NOT EXISTS idx_medical_records_patient_uid ON medical_records(patient_firebase_uid);
CREATE INDEX IF NOT EXISTS idx_medical_records_updated_at ON medical_records(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_medical_records_created_at ON medical_records(created_at DESC);

-- Add comment for documentation
COMMENT ON COLUMN medical_records.updated_at IS 'Timestamp when the medical record was last updated (automatically maintained by trigger)';
COMMENT ON COLUMN medical_records.appointment_id IS 'Links medical report to the appointment it was created from';


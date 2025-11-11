-- Complete Medical Records Migration
-- This single script includes all necessary changes for medical_records table
-- Run this once to set up everything needed for statistics and review tracking

-- =====================================================
-- 1. Add updated_at column and trigger
-- =====================================================

-- Add the updated_at column if it doesn't already exist
ALTER TABLE medical_records
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT now();

-- Update any existing records that have NULL updated_at
UPDATE medical_records
SET updated_at = created_at
WHERE updated_at IS NULL;

-- Create or replace a function to automatically update 'updated_at' on row modification
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop the existing trigger if it exists to avoid conflicts when recreating
DROP TRIGGER IF EXISTS set_medical_records_updated_at ON medical_records;

-- Create a trigger to execute the function before each update on the medical_records table
CREATE TRIGGER set_medical_records_updated_at
BEFORE UPDATE ON medical_records
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 2. Add review_status column
-- =====================================================

-- Add review_status column if it doesn't exist
ALTER TABLE medical_records
ADD COLUMN IF NOT EXISTS review_status VARCHAR(20) DEFAULT 'pending' 
CHECK (review_status IN ('pending', 'reviewed', 'in_progress'));

-- Update existing records: if diagnosis exists and is not empty, mark as reviewed
UPDATE medical_records
SET review_status = 'reviewed'
WHERE diagnosis IS NOT NULL 
  AND diagnosis != ''
  AND (review_status = 'pending' OR review_status IS NULL);

-- =====================================================
-- 3. Ensure appointment_id column exists
-- =====================================================

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

-- =====================================================
-- 4. Create indexes for performance
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_medical_records_review_status ON medical_records(review_status);
CREATE INDEX IF NOT EXISTS idx_medical_records_doctor_uid ON medical_records(doctor_firebase_uid);
CREATE INDEX IF NOT EXISTS idx_medical_records_patient_uid ON medical_records(patient_firebase_uid);
CREATE INDEX IF NOT EXISTS idx_medical_records_updated_at ON medical_records(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_medical_records_created_at ON medical_records(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_medical_records_patient_appointment ON medical_records(patient_firebase_uid, appointment_id);

-- =====================================================
-- 5. Add comments for documentation
-- =====================================================

COMMENT ON COLUMN medical_records.updated_at IS 'Timestamp when the medical record was last updated (automatically maintained by trigger)';
COMMENT ON COLUMN medical_records.review_status IS 'Status of AI diagnosis review: pending (not reviewed), reviewed (doctor has reviewed and saved), in_progress (doctor is reviewing)';
COMMENT ON COLUMN medical_records.appointment_id IS 'Links medical report to the appointment it was created from';

-- =====================================================
-- Verification queries (optional - run separately to verify)
-- =====================================================

-- Check if all columns exist
-- SELECT column_name, data_type, column_default 
-- FROM information_schema.columns 
-- WHERE table_name = 'medical_records' 
--   AND column_name IN ('updated_at', 'review_status', 'appointment_id')
-- ORDER BY column_name;

-- Check if trigger exists
-- SELECT trigger_name, event_manipulation, event_object_table 
-- FROM information_schema.triggers 
-- WHERE trigger_name = 'set_medical_records_updated_at';

-- Check review_status distribution
-- SELECT review_status, COUNT(*) as count 
-- FROM medical_records 
-- GROUP BY review_status 
-- ORDER BY review_status;


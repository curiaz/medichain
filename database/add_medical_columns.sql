-- Add medical information columns to user_profiles table
-- These columns store patient medical data

ALTER TABLE user_profiles
ADD COLUMN IF NOT EXISTS blood_type VARCHAR(10),
ADD COLUMN IF NOT EXISTS medical_conditions TEXT[],
ADD COLUMN IF NOT EXISTS allergies TEXT[],
ADD COLUMN IF NOT EXISTS current_medications TEXT[],
ADD COLUMN IF NOT EXISTS medical_notes TEXT;

-- Add comment for documentation
COMMENT ON COLUMN user_profiles.blood_type IS 'Patient blood type (A+, A-, B+, B-, O+, O-, AB+, AB-)';
COMMENT ON COLUMN user_profiles.medical_conditions IS 'Array of patient medical conditions';
COMMENT ON COLUMN user_profiles.allergies IS 'Array of patient allergies';
COMMENT ON COLUMN user_profiles.current_medications IS 'Array of current medications';
COMMENT ON COLUMN user_profiles.medical_notes IS 'Additional medical notes';

-- Refresh the schema cache for PostgREST
NOTIFY pgrst, 'reload schema';

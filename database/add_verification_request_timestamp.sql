-- Migration: Add timestamp for tracking verification request sending
-- This allows implementing a 24-hour cooldown period to prevent spam

-- Add column to track last verification request sent time
ALTER TABLE doctor_profiles
ADD COLUMN IF NOT EXISTS last_verification_request_sent TIMESTAMPTZ DEFAULT NULL;

-- Add comment for documentation
COMMENT ON COLUMN doctor_profiles.last_verification_request_sent IS 'Timestamp when the last verification request email was sent. Used to enforce 24-hour cooldown period.';

-- Create index for efficient querying
CREATE INDEX IF NOT EXISTS idx_doctor_profiles_verification_request 
ON doctor_profiles(last_verification_request_sent);

-- Verify the column was added
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'doctor_profiles' 
AND column_name = 'last_verification_request_sent';

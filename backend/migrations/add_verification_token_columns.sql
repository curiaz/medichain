-- Add verification token columns to doctor_profiles table
-- These are needed for the email verification system

-- Add verification_token column (stores secure token for email links)
ALTER TABLE doctor_profiles 
ADD COLUMN IF NOT EXISTS verification_token VARCHAR(255);

-- Add token_expires_at column (24-hour expiration)
ALTER TABLE doctor_profiles 
ADD COLUMN IF NOT EXISTS token_expires_at TIMESTAMP WITH TIME ZONE;

-- Add verified_at column (timestamp when approved)
ALTER TABLE doctor_profiles 
ADD COLUMN IF NOT EXISTS verified_at TIMESTAMP WITH TIME ZONE;

-- Add declined_at column (timestamp when declined)
ALTER TABLE doctor_profiles 
ADD COLUMN IF NOT EXISTS declined_at TIMESTAMP WITH TIME ZONE;

-- Add index on verification_token for faster lookups
CREATE INDEX IF NOT EXISTS idx_doctor_profiles_verification_token 
ON doctor_profiles(verification_token);

-- Comments
COMMENT ON COLUMN doctor_profiles.verification_token IS 'Secure token for email verification links (expires in 24 hours)';
COMMENT ON COLUMN doctor_profiles.token_expires_at IS 'Expiration timestamp for verification token';
COMMENT ON COLUMN doctor_profiles.verified_at IS 'Timestamp when doctor was approved';
COMMENT ON COLUMN doctor_profiles.declined_at IS 'Timestamp when doctor was declined';


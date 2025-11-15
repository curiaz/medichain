-- Add password_hash column to user_profiles for Supabase-based authentication
-- This allows users to authenticate without Firebase

ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);

-- Add comment
COMMENT ON COLUMN user_profiles.password_hash IS 'Bcrypt hashed password for Supabase-only authentication';

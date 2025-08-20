-- Remove email_verified column and related items from profiles table
-- Run this in your Supabase SQL editor to clean up email verification implementation

-- Drop the index first
DROP INDEX IF EXISTS idx_profiles_email_verified;

-- Drop the email_verified column
ALTER TABLE profiles DROP COLUMN IF EXISTS email_verified;

-- Verify the changes
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'profiles' 
ORDER BY ordinal_position;

-- Add email_verified column to profiles table
-- Run this in your Supabase SQL editor

ALTER TABLE profiles ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;

-- Update existing profiles to be unverified by default
UPDATE profiles SET email_verified = FALSE WHERE email_verified IS NULL;

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_profiles_email_verified ON profiles(email_verified);

-- Migration: Add avatar_url column to user_profiles table
-- Date: 2025-01-XX
-- Description: Ensures avatar_url column exists for storing profile photo URLs

-- Check if user_profiles table exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'user_profiles'
    ) THEN
        RAISE EXCEPTION 'user_profiles table does not exist. Please create it first.';
    END IF;
END $$;

-- Add avatar_url column if it doesn't exist
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS avatar_url TEXT;

-- Add comment
COMMENT ON COLUMN user_profiles.avatar_url IS 'URL or path to user profile photo/avatar image';

-- Create index for faster lookups (optional, but helpful for queries)
CREATE INDEX IF NOT EXISTS idx_user_profiles_avatar_url 
ON user_profiles(avatar_url) 
WHERE avatar_url IS NOT NULL;

-- Verify the column was added
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'user_profiles' 
        AND column_name = 'avatar_url'
    ) THEN
        RAISE EXCEPTION 'Failed to add avatar_url column';
    ELSE
        RAISE NOTICE '✅ avatar_url column exists in user_profiles table';
    END IF;
END $$;


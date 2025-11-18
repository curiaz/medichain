-- Migration: Update gender constraint to only allow 'male' and 'female'
-- This migration updates the gender check constraint and existing data

-- Step 1: Update existing data - convert to lowercase and set 'other' to NULL or 'male' (default)
DO $$
BEGIN
    -- Update any uppercase gender values to lowercase
    UPDATE user_profiles 
    SET gender = LOWER(gender)
    WHERE gender IS NOT NULL 
      AND gender != LOWER(gender)
      AND LOWER(gender) IN ('male', 'female');
    
    -- Set 'other' values to NULL (or you can set to 'male' as default)
    UPDATE user_profiles
    SET gender = NULL
    WHERE gender IS NOT NULL
      AND LOWER(gender) = 'other';
END $$;

-- Step 2: Update the constraint to only allow 'male' and 'female'
ALTER TABLE user_profiles DROP CONSTRAINT IF EXISTS user_profiles_gender_check;
ALTER TABLE user_profiles ADD CONSTRAINT user_profiles_gender_check 
  CHECK (gender IS NULL OR gender IN ('male', 'female'));

COMMENT ON COLUMN user_profiles.gender IS 'User gender: male or female only (lowercase)';


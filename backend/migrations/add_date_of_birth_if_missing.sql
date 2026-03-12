-- Migration: Add date_of_birth column to user_profiles if it doesn't exist
-- This is a safe migration that checks if the column exists before adding it

-- Check if date_of_birth column exists, if not, add it
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'user_profiles' 
        AND column_name = 'date_of_birth'
    ) THEN
        ALTER TABLE user_profiles 
        ADD COLUMN date_of_birth DATE;
        
        COMMENT ON COLUMN user_profiles.date_of_birth IS 'Patient date of birth for medical records and prescriptions';
        
        RAISE NOTICE 'Added date_of_birth column to user_profiles table';
    ELSE
        RAISE NOTICE 'date_of_birth column already exists in user_profiles table';
    END IF;
END $$;


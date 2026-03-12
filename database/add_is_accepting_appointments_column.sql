-- Add is_accepting_appointments column to doctor_profiles table
-- Run this SQL in Supabase SQL Editor

ALTER TABLE doctor_profiles 
ADD COLUMN IF NOT EXISTS is_accepting_appointments BOOLEAN DEFAULT TRUE;

-- Add index for better query performance
CREATE INDEX IF NOT EXISTS idx_doctor_profiles_is_accepting_appointments 
ON doctor_profiles(is_accepting_appointments);

-- Update existing records to default to TRUE (accepting appointments)
UPDATE doctor_profiles 
SET is_accepting_appointments = TRUE 
WHERE is_accepting_appointments IS NULL;


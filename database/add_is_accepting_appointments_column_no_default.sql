-- Add is_accepting_appointments column to doctor_profiles table
-- Run this SQL in Supabase SQL Editor

-- Step 1: Add the column WITHOUT a default (so False values persist)
ALTER TABLE doctor_profiles 
ADD COLUMN IF NOT EXISTS is_accepting_appointments BOOLEAN;

-- Step 2: Set existing NULL values to TRUE (for doctors who haven't set it yet)
UPDATE doctor_profiles 
SET is_accepting_appointments = TRUE 
WHERE is_accepting_appointments IS NULL;

-- Step 3: Add index for better query performance
CREATE INDEX IF NOT EXISTS idx_doctor_profiles_is_accepting_appointments 
ON doctor_profiles(is_accepting_appointments);

-- Step 4: Verify the column was added (you should see it in the table)
-- Check in Supabase UI: Table Editor > doctor_profiles > is_accepting_appointments


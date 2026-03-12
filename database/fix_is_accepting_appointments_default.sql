-- Fix is_accepting_appointments to ensure False values persist correctly
-- Run this SQL in Supabase SQL Editor

-- First, ensure the column exists
ALTER TABLE doctor_profiles 
ADD COLUMN IF NOT EXISTS is_accepting_appointments BOOLEAN DEFAULT TRUE;

-- CRITICAL: Remove the DEFAULT constraint so NULL values don't auto-default to TRUE
-- This ensures that when we explicitly set False, it stays False
ALTER TABLE doctor_profiles 
ALTER COLUMN is_accepting_appointments DROP DEFAULT;

-- Update any NULL values to TRUE (only for existing records that were never set)
UPDATE doctor_profiles 
SET is_accepting_appointments = TRUE 
WHERE is_accepting_appointments IS NULL;

-- Now add back a DEFAULT for NEW rows only (not updates)
-- But we'll handle this in application code instead to avoid issues
-- ALTER TABLE doctor_profiles 
-- ALTER COLUMN is_accepting_appointments SET DEFAULT TRUE;

-- Add index for better query performance
CREATE INDEX IF NOT EXISTS idx_doctor_profiles_is_accepting_appointments 
ON doctor_profiles(is_accepting_appointments);


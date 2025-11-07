-- Remove DEFAULT TRUE constraint from is_accepting_appointments column
-- This ensures that False values persist correctly and don't get overridden
-- Run this SQL in Supabase SQL Editor

-- Step 1: Remove the DEFAULT constraint
ALTER TABLE doctor_profiles 
ALTER COLUMN is_accepting_appointments DROP DEFAULT;

-- Step 2: Verify the constraint is removed (this will show current column definition)
-- You can check in Supabase UI: Table Editor > doctor_profiles > is_accepting_appointments
-- The "Default value" should be empty/null

-- Step 3: Update any NULL values to TRUE (only for records that were never explicitly set)
-- This is safe because NULL means "never set", so defaulting to TRUE is reasonable
UPDATE doctor_profiles 
SET is_accepting_appointments = TRUE 
WHERE is_accepting_appointments IS NULL;

-- Note: After this migration, when you set is_accepting_appointments = FALSE,
-- it will stay FALSE even after logout/login, because there's no DEFAULT to override it.


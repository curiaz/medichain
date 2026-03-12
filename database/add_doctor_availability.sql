-- Add availability column to doctor_profiles table
-- This will store doctor's available time slots as JSON

-- Add availability column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'doctor_profiles' 
        AND column_name = 'availability'
    ) THEN
        ALTER TABLE doctor_profiles
        ADD COLUMN availability JSONB DEFAULT '[]'::jsonb;
    END IF;
END $$;

-- Add comment to explain the structure
COMMENT ON COLUMN doctor_profiles.availability IS 'Array of available time slots in format: [{date: "2025-10-21", time_slots: ["09:00", "10:00", "14:00"]}]';

-- Sample data structure:
-- [
--   {
--     "date": "2025-10-21",
--     "time_slots": ["09:00", "10:00", "11:00", "14:00", "15:00"]
--   },
--   {
--     "date": "2025-10-22",
--     "time_slots": ["09:00", "10:00", "14:00"]
--   }
-- ]

-- Create index for better query performance
CREATE INDEX IF NOT EXISTS idx_doctor_availability ON doctor_profiles USING GIN (availability);

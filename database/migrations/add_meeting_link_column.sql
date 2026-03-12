-- Ensure appointments table has meeting_link column
-- Run this in Supabase SQL Editor if the column doesn't exist

-- Add meeting_link column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'appointments' 
        AND column_name = 'meeting_link'
    ) THEN
        ALTER TABLE appointments ADD COLUMN meeting_link TEXT;
        COMMENT ON COLUMN appointments.meeting_link IS 'Jitsi video conference meeting URL';
    END IF;
END $$;

-- Ensure notifications table exists
-- Run database/notifications_schema.sql if table doesn't exist

-- Create index on meeting_link for faster queries
CREATE INDEX IF NOT EXISTS idx_appointments_meeting_link ON appointments(meeting_link) WHERE meeting_link IS NOT NULL;

-- Update existing appointments to extract meeting_link from notes if needed
UPDATE appointments
SET meeting_link = (
    SELECT substring(notes FROM 'Meeting:\s*(https?://[^\s]+)')
    WHERE notes LIKE '%Meeting:%'
    AND meeting_link IS NULL
)
WHERE notes LIKE '%Meeting:%'
AND meeting_link IS NULL;


-- Add follow_up_checkup field to appointments table
-- This field indicates if the appointment is a follow-up checkup

ALTER TABLE appointments
ADD COLUMN IF NOT EXISTS follow_up_checkup BOOLEAN DEFAULT FALSE;

-- Create index for better query performance
CREATE INDEX IF NOT EXISTS idx_appointments_follow_up_checkup ON appointments(follow_up_checkup);

-- Add comment for documentation
COMMENT ON COLUMN appointments.follow_up_checkup IS 'Indicates if this appointment is a follow-up checkup (true) or a new consultation (false)';


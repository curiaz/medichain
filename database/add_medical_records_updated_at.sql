-- database/add_medical_records_updated_at.sql

-- Add the updated_at column if it doesn't already exist
ALTER TABLE medical_records
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT now();

-- Create or replace a function to automatically update 'updated_at' on row modification
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop the existing trigger if it exists to avoid conflicts when recreating
DROP TRIGGER IF EXISTS set_medical_records_updated_at ON medical_records;

-- Create a trigger to execute the function before each update on the medical_records table
CREATE TRIGGER set_medical_records_updated_at
BEFORE UPDATE ON medical_records
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

COMMENT ON COLUMN medical_records.updated_at IS 'Timestamp when the medical record was last updated';


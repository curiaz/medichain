-- Migration: Add symptoms, documents, and AI diagnosis fields to appointments table
-- Run this migration to add support for AI health diagnosis in appointments

-- Add new columns to appointments table
ALTER TABLE appointments 
ADD COLUMN IF NOT EXISTS symptoms TEXT[],
ADD COLUMN IF NOT EXISTS documents JSONB DEFAULT '[]',
ADD COLUMN IF NOT EXISTS ai_diagnosis JSONB,
ADD COLUMN IF NOT EXISTS ai_diagnosis_processed BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS ai_diagnosis_processed_at TIMESTAMP WITH TIME ZONE;

-- Add index for AI diagnosis queries
CREATE INDEX IF NOT EXISTS idx_appointments_ai_diagnosis_processed 
ON appointments(ai_diagnosis_processed) 
WHERE ai_diagnosis_processed = FALSE;

-- Add comment to document the new fields
COMMENT ON COLUMN appointments.symptoms IS 'Array of symptoms selected by patient during booking';
COMMENT ON COLUMN appointments.documents IS 'JSON array of uploaded document metadata (lab results, etc.)';
COMMENT ON COLUMN appointments.ai_diagnosis IS 'AI diagnosis results from Supabase datasets, processed after booking';
COMMENT ON COLUMN appointments.ai_diagnosis_processed IS 'Flag indicating if AI diagnosis has been processed';
COMMENT ON COLUMN appointments.ai_diagnosis_processed_at IS 'Timestamp when AI diagnosis was processed';


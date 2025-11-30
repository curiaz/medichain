-- Migration: Add base64 data columns to doctor_documents table
-- Date: 2025-11-19
-- Description: Adds base64 and data columns to enable inline document viewing

-- Add base64 column for storing raw base64 string
ALTER TABLE doctor_documents 
ADD COLUMN IF NOT EXISTS base64 TEXT;

-- Add data column for storing full data URL (data:image/jpeg;base64,...)
ALTER TABLE doctor_documents 
ADD COLUMN IF NOT EXISTS data TEXT;

-- Add comments
COMMENT ON COLUMN doctor_documents.base64 IS 'Base64 encoded file data for inline viewing';
COMMENT ON COLUMN doctor_documents.data IS 'Full data URL (data:mime/type;base64,...) for inline viewing';

-- Note: These columns are nullable to support existing documents that don't have base64 data
-- New documents uploaded after this migration will include base64 data




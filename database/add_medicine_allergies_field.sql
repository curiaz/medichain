-- Migration: Add medicine_allergies field to appointments table
-- Run this migration to add support for medicine allergies in appointments

-- Add new column to appointments table
ALTER TABLE appointments 
ADD COLUMN IF NOT EXISTS medicine_allergies TEXT;

-- Add comment to document the new field
COMMENT ON COLUMN appointments.medicine_allergies IS 'Medicine allergies or adverse reactions reported by patient during booking';


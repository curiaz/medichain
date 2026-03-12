-- Add GCash reference number column to payments table
-- Run this in Supabase SQL Editor

-- Add gcash_reference_number column to store reference numbers from GCash
ALTER TABLE payments 
ADD COLUMN IF NOT EXISTS gcash_reference_number VARCHAR(255);

-- Create index for faster lookups when verifying references
CREATE INDEX IF NOT EXISTS idx_payments_gcash_reference ON payments(gcash_reference_number);

-- Add comment
COMMENT ON COLUMN payments.gcash_reference_number IS 'GCash payment reference number entered by admin after receiving payment notification';

-- Notify PostgREST to reload schema
NOTIFY pgrst, 'reload schema';


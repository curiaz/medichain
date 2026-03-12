-- Add payment-related columns to appointments table
-- Run this in Supabase SQL Editor

-- Add payment_transaction_id column if it doesn't exist
ALTER TABLE appointments 
ADD COLUMN IF NOT EXISTS payment_transaction_id VARCHAR(255);

-- Add payment_method column if it doesn't exist
ALTER TABLE appointments 
ADD COLUMN IF NOT EXISTS payment_method VARCHAR(50);

-- Create index on payment_transaction_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_appointments_payment_transaction_id 
ON appointments(payment_transaction_id);

-- Add comments
COMMENT ON COLUMN appointments.payment_transaction_id IS 'Transaction ID from payment gateway (Stripe, PayPal, etc.)';
COMMENT ON COLUMN appointments.payment_method IS 'Payment method used (credit_card, debit_card, etc.)';





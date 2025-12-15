-- Create payments table for storing payment transactions
-- Run this in Supabase SQL Editor

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create payments table
CREATE TABLE IF NOT EXISTS payments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  transaction_id VARCHAR(255) UNIQUE NOT NULL,
  user_firebase_uid VARCHAR(255) NOT NULL,
  amount DECIMAL(10, 2) NOT NULL,
  payment_method VARCHAR(50) NOT NULL CHECK (payment_method IN ('credit_card', 'debit_card', 'gcash', 'paypal', 'other')),
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'failed', 'refunded', 'cancelled')),
  payment_gateway_response JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  verified_at TIMESTAMP WITH TIME ZONE,
  expires_at TIMESTAMP WITH TIME ZONE,
  appointment_id UUID REFERENCES appointments(id) ON DELETE SET NULL,
  
  -- Indexes for faster queries
  CONSTRAINT payments_transaction_id_unique UNIQUE (transaction_id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_payments_transaction_id ON payments(transaction_id);
CREATE INDEX IF NOT EXISTS idx_payments_user_firebase_uid ON payments(user_firebase_uid);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments(created_at);
CREATE INDEX IF NOT EXISTS idx_payments_appointment_id ON payments(appointment_id);

-- Enable Row Level Security
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;

-- RLS Policies: Users can only view their own payments
CREATE POLICY "Users can view own payments" ON payments
  FOR SELECT USING (user_firebase_uid = auth.uid()::text);

CREATE POLICY "Users can create own payments" ON payments
  FOR INSERT WITH CHECK (user_firebase_uid = auth.uid()::text);

-- Admins can view all payments (optional - adjust based on your needs)
-- CREATE POLICY "Admins can view all payments" ON payments
--   FOR SELECT USING (
--     EXISTS (
--       SELECT 1 FROM user_profiles 
--       WHERE firebase_uid = auth.uid()::text 
--       AND role = 'admin'
--     )
--   );

-- Add comments
COMMENT ON TABLE payments IS 'Stores payment transactions for appointments';
COMMENT ON COLUMN payments.transaction_id IS 'Unique transaction ID from payment gateway or generated internally';
COMMENT ON COLUMN payments.status IS 'pending: awaiting payment, paid: payment confirmed, failed: payment failed, refunded: payment refunded, cancelled: payment cancelled';
COMMENT ON COLUMN payments.expires_at IS 'For pending payments (like GCash QR), when the payment link expires';

-- Notify PostgREST to reload schema
NOTIFY pgrst, 'reload schema';



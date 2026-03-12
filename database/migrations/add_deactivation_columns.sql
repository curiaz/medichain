-- Migration: Add deactivation and reactivation columns to user_profiles
-- Date: 2025-11-11
-- Purpose: Support doctor account deactivation and reactivation feature

-- Add deactivated_at column to track when account was deactivated
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS deactivated_at TIMESTAMP WITH TIME ZONE;

-- Add reactivated_at column to track when account was reactivated
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS reactivated_at TIMESTAMP WITH TIME ZONE;

-- Add is_active column if it doesn't exist (should already exist, but adding for safety)
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- Add account_status column to doctor_profiles if it doesn't exist
ALTER TABLE doctor_profiles 
ADD COLUMN IF NOT EXISTS account_status VARCHAR(50) DEFAULT 'active';

-- Create index on is_active for faster queries
CREATE INDEX IF NOT EXISTS idx_user_profiles_is_active ON user_profiles(is_active);

-- Create index on account_status for faster queries
CREATE INDEX IF NOT EXISTS idx_doctor_profiles_account_status ON doctor_profiles(account_status);

-- Update any existing records to ensure consistency
UPDATE user_profiles 
SET is_active = TRUE 
WHERE is_active IS NULL;

UPDATE doctor_profiles 
SET account_status = 'active' 
WHERE account_status IS NULL;

-- Add comments to columns
COMMENT ON COLUMN user_profiles.deactivated_at IS 'Timestamp when the account was deactivated';
COMMENT ON COLUMN user_profiles.reactivated_at IS 'Timestamp when the account was last reactivated';
COMMENT ON COLUMN user_profiles.is_active IS 'Whether the account is active (true) or deactivated (false)';
COMMENT ON COLUMN doctor_profiles.account_status IS 'Status of doctor account: active, deactivated, suspended';

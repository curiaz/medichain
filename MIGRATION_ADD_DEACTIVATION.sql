-- ============================================================================
-- MIGRATION: Add Account Deactivation Support
-- Date: 2025-11-11
-- Run this in your Supabase SQL Editor
-- ============================================================================

-- Step 1: Add deactivation/reactivation columns to user_profiles
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS deactivated_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS reactivated_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- Step 2: Add account_status to doctor_profiles
ALTER TABLE doctor_profiles 
ADD COLUMN IF NOT EXISTS account_status VARCHAR(50) DEFAULT 'active';

-- Step 3: Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_is_active 
ON user_profiles(is_active);

CREATE INDEX IF NOT EXISTS idx_doctor_profiles_account_status 
ON doctor_profiles(account_status);

-- Step 4: Update existing records to ensure defaults are set
UPDATE user_profiles 
SET is_active = TRUE 
WHERE is_active IS NULL;

UPDATE doctor_profiles 
SET account_status = 'active' 
WHERE account_status IS NULL;

-- Step 5: Add constraints and comments
COMMENT ON COLUMN user_profiles.deactivated_at IS 
'Timestamp when the account was deactivated (NULL if active)';

COMMENT ON COLUMN user_profiles.reactivated_at IS 
'Timestamp when the account was last reactivated';

COMMENT ON COLUMN user_profiles.is_active IS 
'Active status: TRUE = active, FALSE = deactivated';

COMMENT ON COLUMN doctor_profiles.account_status IS 
'Account status: active, deactivated, suspended, or pending';

-- Step 6: Verify the migration
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'user_profiles' 
AND column_name IN ('is_active', 'deactivated_at', 'reactivated_at')
ORDER BY column_name;

-- ============================================================================
-- Migration Complete!
-- You should see 3 rows showing the new columns.
-- ============================================================================

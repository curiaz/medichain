# 🔧 FIX: Database Migration Required for Account Deactivation

## The Problem
You're seeing this error when trying to deactivate a doctor account:
```
Could not find the 'deactivated_at' column of 'user_profiles' in the schema cache
```

This means your database is missing the required columns for the account deactivation feature.

## The Solution: Run Database Migration

### Step 1: Open Supabase Dashboard
1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor** (in the left sidebar)

### Step 2: Run the Migration SQL
1. Click **"New Query"**
2. Copy and paste the entire contents of `MIGRATION_ADD_DEACTIVATION.sql` file
3. Click **"Run"** or press `Ctrl+Enter`

### Step 3: Verify Migration
After running the SQL, you should see output showing:
```
column_name      | data_type                   | is_nullable | column_default
-----------------|-----------------------------|-------------|---------------
deactivated_at   | timestamp with time zone    | YES         | NULL
is_active        | boolean                     | YES         | true
reactivated_at   | timestamp with time zone    | YES         | NULL
```

### Step 4: Test the Feature
1. Go back to your MediChain application
2. Navigate to Doctor Profile → Account Security
3. Click "Deactivate Account"
4. The deactivation should now work! ✅

## What This Migration Does

The migration adds the following columns to your database:

### `user_profiles` table:
- **`is_active`** (BOOLEAN) - Whether account is active (TRUE) or deactivated (FALSE)
- **`deactivated_at`** (TIMESTAMP) - When the account was deactivated
- **`reactivated_at`** (TIMESTAMP) - When the account was last reactivated

### `doctor_profiles` table:
- **`account_status`** (VARCHAR) - Status: 'active', 'deactivated', 'suspended', 'pending'

## Alternative: Manual SQL Commands

If you prefer to run commands one by one, here they are:

```sql
-- Add columns to user_profiles
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS deactivated_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS reactivated_at TIMESTAMP WITH TIME ZONE;

-- Add column to doctor_profiles
ALTER TABLE doctor_profiles 
ADD COLUMN IF NOT EXISTS account_status VARCHAR(50) DEFAULT 'active';

-- Update existing records
UPDATE user_profiles SET is_active = TRUE WHERE is_active IS NULL;
UPDATE doctor_profiles SET account_status = 'active' WHERE account_status IS NULL;
```

## Troubleshooting

### Error: "permission denied for table user_profiles"
- Make sure you're logged in as the Supabase admin user
- Or run the SQL through the Supabase Dashboard SQL Editor (recommended)

### Error: "relation user_profiles does not exist"
- Your database schema may not be set up correctly
- Check that the `user_profiles` table exists in your database

### Still having issues?
1. Check that you're connected to the correct Supabase project
2. Verify your `.env` file has the correct Supabase credentials
3. Make sure the backend is using the service_role key (not anon key)

## After Migration Success

Once the migration is complete, you'll be able to:
- ✅ Deactivate doctor accounts
- ✅ Reactivate doctor accounts on login
- ✅ Keep doctor profiles visible to patients after deactivation
- ✅ Fully delete patient accounts

---

**Need Help?** 
- Migration SQL File: `MIGRATION_ADD_DEACTIVATION.sql`
- Documentation: `DOCTOR_PATIENT_ACCOUNT_MANAGEMENT.md`
- Reactivation Guide: `DOCTOR_REACTIVATION_FEATURE.md`

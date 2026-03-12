# Fix Failed Test - Quick Action Required

## What's the Issue?

Your test is failing because the `availability` column is missing from the `doctor_profiles` table in Supabase.

**Current Status:**
- ✅ Appointments table exists
- ❌ **Availability column missing** ← THIS NEEDS TO BE FIXED
- ✅ Verification timestamp exists

## Quick Fix (2 minutes)

### Step 1: Open Supabase Dashboard

1. Go to: https://supabase.com/dashboard
2. Select your **medichain** project
3. Click **SQL Editor** in the left sidebar
4. Click **New Query**

### Step 2: Copy & Paste This SQL

```sql
-- Add availability column to doctor_profiles table
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'doctor_profiles' 
        AND column_name = 'availability'
    ) THEN
        ALTER TABLE doctor_profiles
        ADD COLUMN availability JSONB DEFAULT '[]'::jsonb;
    END IF;
END $$;

-- Add index for better performance
CREATE INDEX IF NOT EXISTS idx_doctor_availability 
ON doctor_profiles USING GIN (availability);

-- Add helpful comment
COMMENT ON COLUMN doctor_profiles.availability IS 
'Available time slots: [{date: "2025-10-21", time_slots: [...]}]';
```

### Step 3: Click "Run" Button

You should see: **Success. No rows returned**

### Step 4: Verify It Worked

Run this in your terminal:

```bash
python check_migration.py
```

Expected output:
```
✅ ALL MIGRATIONS COMPLETE!
```

### Step 5: Run Tests Again

```bash
python test_appointment_system.py
```

Expected result: **10/10 tests passing** ✅

---

## Alternative Methods

### Option A: Interactive Guide
```bash
python complete_migration.py
```
This walks you through step-by-step.

### Option B: Use SQL File
Upload `database/add_doctor_availability.sql` directly in Supabase SQL Editor.

---

## Why This Happened

The `availability` column stores doctor schedules in JSONB format. Without it:
- Doctors can't set their availability
- Patients can't book appointments
- The test fails because it can't create appointments

## What This SQL Does

✅ Adds a new column `availability` (JSONB type)
✅ Sets default value to empty array `[]`
✅ Creates an index for fast queries
✅ Adds documentation comments
✅ Safe to run multiple times (checks if exists first)

---

## Still Having Issues?

See the detailed guide: **MIGRATION_GUIDE.md**

Or check the status anytime:
```bash
python check_migration.py
```

---

**Estimated Time:** 2-3 minutes
**Difficulty:** Easy (just copy/paste SQL)
**Risk:** None (migration is reversible and backward compatible)

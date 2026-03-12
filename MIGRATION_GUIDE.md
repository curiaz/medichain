# Database Migration Required - Fix Failed Test

## Current Status

The appointment booking system tests are failing because the `availability` column is missing from the `doctor_profiles` table in your Supabase database.

**Test Results:**
- ✅ 9/10 tests passing
- ❌ 1/1 test failing: `test_create_appointment` (requires `availability` column)

## Problem

The `availability` column stores doctor's available time slots as JSONB data. Without this column, the appointment system cannot:
- Store doctor availability schedules
- Check if time slots are available
- Create new appointments

## Solution

You need to run a SQL migration in your Supabase database to add the `availability` column.

### Option 1: Interactive Guide (Recommended)

Run this command and follow the on-screen instructions:

```bash
python complete_migration.py
```

This will:
1. Show you exactly what SQL to run
2. Guide you through the Supabase dashboard
3. Verify the migration afterward

### Option 2: Manual SQL Execution

1. **Open Supabase Dashboard:**
   - Go to: https://supabase.com/dashboard
   - Select your project
   - Click "SQL Editor" → "New Query"

2. **Run this SQL:**

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

3. **Verify the migration:**

```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'doctor_profiles'
AND column_name = 'availability';
```

Expected result: Should show `availability | jsonb`

### Option 3: Use SQL File

The SQL is available in the repository:

```bash
database/add_doctor_availability.sql
```

You can upload this file directly in Supabase SQL Editor.

## After Migration

Once you've added the column, verify everything works:

```bash
python test_appointment_system.py
```

**Expected result:** 10/10 tests passing ✅

## Database Schema After Migration

The `doctor_profiles` table will have:

```
doctor_profiles
├── id (primary key)
├── firebase_uid (unique)
├── email
├── full_name
├── specialty
├── verification_status
├── license_number
├── years_of_experience
├── availability (JSONB) ← NEW COLUMN
├── last_verification_request_sent (timestamp)
└── created_at, updated_at
```

## Availability Data Format

The `availability` column stores data in this format:

```json
[
  {
    "date": "2025-10-21",
    "time_slots": ["09:00", "10:00", "11:00", "14:00", "15:00"]
  },
  {
    "date": "2025-10-22",
    "time_slots": ["09:00", "10:00", "14:00"]
  }
]
```

## Why This Migration is Safe

✅ **Non-breaking:** Adds a new column with default value `[]`
✅ **Backward compatible:** Existing code won't break
✅ **Idempotent:** Safe to run multiple times (checks if column exists)
✅ **Indexed:** Includes GIN index for fast JSONB queries
✅ **Documented:** Includes SQL comments explaining the structure

## Troubleshooting

### "relation doctor_profiles does not exist"
The `doctor_profiles` table doesn't exist. Run the main schema first:
```sql
-- See: database/enhanced_profile_management_schema.sql
```

### "permission denied"
You need ALTER TABLE privileges. Make sure you're using:
- The service role key
- Or a user with proper permissions

### "column already exists"
Perfect! The migration was already completed. Just run the tests.

### Still failing after migration?
Check that:
1. The column was actually created (run verification query)
2. The backend is connecting to the correct database
3. The Supabase client is using fresh credentials

## Next Steps

1. ✅ Run the migration SQL in Supabase dashboard
2. ✅ Verify the column exists
3. ✅ Run test suite: `python test_appointment_system.py`
4. ✅ Confirm 10/10 tests passing
5. ✅ Commit the migration scripts to Git
6. ✅ Merge to master

## Files Involved

**Migration Scripts:**
- `complete_migration.py` - Interactive guide
- `run_appointments_migration.py` - Status checker
- `add_availability_column.py` - Original script (needs RPC)

**SQL Files:**
- `database/add_doctor_availability.sql` - The actual SQL
- `database/create_appointments_table.sql` - Already applied
- `database/add_verification_request_timestamp.sql` - Already applied

**Test Files:**
- `test_appointment_system.py` - Full test suite (10 tests)

## Questions?

If you encounter any issues:
1. Check the Supabase dashboard for error messages
2. Verify your database credentials in `.env`
3. Make sure you're connected to the right project
4. Review the SQL output in Supabase SQL Editor

---

**Status:** 🟡 Waiting for database migration
**Action Required:** Run SQL in Supabase dashboard
**Estimated Time:** 2-3 minutes

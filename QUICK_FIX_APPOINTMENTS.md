# 🎯 QUICK FIX: Appointments Not Working After Supabase Restart

## TL;DR - The Problem

**Reloading schema didn't work because the `appointment_time` column DOESN'T EXIST in your database!**

Your database has the wrong schema structure. No amount of schema reloading will create missing columns.

---

## ✅ The Solution (3 Steps - 5 minutes)

### Step 1: Open Supabase SQL Editor

Go to: https://supabase.com/dashboard/project/royvcmfbcghamnbnxdgb/editor

Click **"SQL Editor"** → **"New Query"**

### Step 2: Run This SQL

Copy the contents of **`FIX_APPOINTMENTS_TABLE.sql`** (or paste below):

```sql
DROP TABLE IF EXISTS appointments CASCADE;

CREATE TABLE appointments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_firebase_uid TEXT NOT NULL,
  doctor_firebase_uid TEXT NOT NULL,
  appointment_date DATE NOT NULL,
  appointment_time TIME NOT NULL,  -- THIS WAS MISSING!
  appointment_type TEXT DEFAULT 'general-practitioner',
  status TEXT DEFAULT 'scheduled',
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(doctor_firebase_uid, appointment_date, appointment_time)
);

CREATE INDEX idx_appointments_patient ON appointments(patient_firebase_uid);
CREATE INDEX idx_appointments_doctor ON appointments(doctor_firebase_uid);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_appointments_status ON appointments(status);

ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Patients can view own appointments" ON appointments
  FOR SELECT USING (patient_firebase_uid = auth.uid()::text);

CREATE POLICY "Doctors can view their appointments" ON appointments
  FOR SELECT USING (doctor_firebase_uid = auth.uid()::text);

CREATE POLICY "Patients can create appointments" ON appointments
  FOR INSERT WITH CHECK (patient_firebase_uid = auth.uid()::text);

CREATE POLICY "Patients can update own appointments" ON appointments
  FOR UPDATE USING (patient_firebase_uid = auth.uid()::text);

CREATE POLICY "Doctors can update their appointments" ON appointments
  FOR UPDATE USING (doctor_firebase_uid = auth.uid()::text);

NOTIFY pgrst, 'reload schema';
```

Click **"Run"** (F5)

### Step 3: Test It

```bash
python test_after_migration.py
```

You should see: **✅ ALL TESTS PASSED!**

---

## 🔍 What Was Wrong

| Database Had | Code Expected | Result |
|-------------|--------------|--------|
| `patient_id` (UUID) | `patient_firebase_uid` (TEXT) | ❌ Column not found |
| `doctor_id` (VARCHAR) | `doctor_firebase_uid` (TEXT) | ❌ Column not found |
| `appointment_date` (TIMESTAMP) | `appointment_date` (DATE) + `appointment_time` (TIME) | ❌ appointment_time missing |

**Schema reload can't fix this** - it only refreshes the cache of *existing* columns!

---

## 📁 Files Created For You

| File | Purpose |
|------|---------|
| `FIX_APPOINTMENTS_TABLE.sql` | SQL migration to run in Supabase |
| `test_after_migration.py` | Test script to verify fix works |
| `WHY_APPOINTMENTS_NOT_WORKING.md` | Detailed explanation |

---

## ⚡ After Running Migration

Your appointment system will work completely:
- ✅ Create appointments
- ✅ View appointments
- ✅ Update appointments
- ✅ Delete appointments
- ✅ Doctor availability management
- ✅ Frontend booking works

---

## 🆘 Still Not Working?

Run this to check status:
```bash
python test_after_migration.py
```

If you see `appointment_time column` error → Migration didn't run, try again in SQL Editor

If you see `SUCCESS` → You're all set! 🎉

---

**That's it!** Just run that SQL in Supabase and you're done. 🚀

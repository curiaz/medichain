# 🗄️ Database Migration Guide - Doctor Profiles

## 🚨 Issue: Missing `doctor_profiles` Table

The doctor signup is failing because the `doctor_profiles` table is missing or doesn't have the required columns.

**Error**:
```
Could not find the 'specialization' column of 'user_profiles' in the schema cache
```

---

## ✅ Solution: Run Database Migration

### **Quick Fix - Copy & Paste This SQL**

Open your **Supabase SQL Editor** and run this:

```sql
-- Create doctor_profiles table if it doesn't exist
CREATE TABLE IF NOT EXISTS doctor_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
  firebase_uid VARCHAR(255) UNIQUE,
  specialization VARCHAR(255),
  verification_document VARCHAR(500),
  verification_status VARCHAR(50) DEFAULT 'pending',
  license_number VARCHAR(100),
  years_of_experience INTEGER,
  hospital_affiliation VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- If table already exists, add missing columns
ALTER TABLE doctor_profiles 
ADD COLUMN IF NOT EXISTS specialization VARCHAR(255);

ALTER TABLE doctor_profiles 
ADD COLUMN IF NOT EXISTS verification_document VARCHAR(500);

ALTER TABLE doctor_profiles 
ADD COLUMN IF NOT EXISTS verification_status VARCHAR(50) DEFAULT 'pending';

ALTER TABLE doctor_profiles 
ADD COLUMN IF NOT EXISTS firebase_uid VARCHAR(255);

-- Add unique constraint on firebase_uid if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'doctor_profiles_firebase_uid_key'
    ) THEN
        ALTER TABLE doctor_profiles 
        ADD CONSTRAINT doctor_profiles_firebase_uid_key UNIQUE (firebase_uid);
    END IF;
END $$;

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_doctor_profiles_user_id 
ON doctor_profiles(user_id);

CREATE INDEX IF NOT EXISTS idx_doctor_profiles_firebase_uid 
ON doctor_profiles(firebase_uid);

CREATE INDEX IF NOT EXISTS idx_doctor_profiles_verification_status 
ON doctor_profiles(verification_status);
```

---

## 📊 Database Architecture

Your MediChain database uses **two separate tables**:

### **1. `user_profiles`** (Basic user info)
```sql
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY,
  firebase_uid VARCHAR(255) UNIQUE,
  email VARCHAR(255) UNIQUE,
  password_hash VARCHAR(255),
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  role VARCHAR(50),  -- 'doctor' or 'patient'
  created_at TIMESTAMP
);
```

### **2. `doctor_profiles`** (Doctor-specific info)
```sql
CREATE TABLE doctor_profiles (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES user_profiles(id),  -- Links to user_profiles
  firebase_uid VARCHAR(255) UNIQUE,
  specialization VARCHAR(255),
  verification_document VARCHAR(500),
  verification_status VARCHAR(50),  -- 'pending', 'approved', 'rejected'
  license_number VARCHAR(100),
  years_of_experience INTEGER,
  hospital_affiliation VARCHAR(255),
  created_at TIMESTAMP
);
```

---

## 🔄 Doctor Signup Flow (Updated)

```
Backend Processing:
1. Create Firebase account
2. Save verification document to filesystem
3. INSERT into user_profiles (basic info + role='doctor')
4. INSERT into doctor_profiles (specialization, verification_document, etc.)
5. Return success with token
```

---

## 🧪 Test After Migration

### **Step 1: Run the SQL Migration**
1. Open Supabase Dashboard → SQL Editor
2. Copy the SQL from above
3. Click "Run"

### **Step 2: Verify Tables Exist**
```sql
-- Check if doctor_profiles table exists
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name = 'doctor_profiles';

-- Check columns
SELECT column_name, data_type 
FROM information_schema.columns
WHERE table_name = 'doctor_profiles'
ORDER BY ordinal_position;
```

**Expected Output**:
- Table: `doctor_profiles` ✅
- Columns: `id`, `user_id`, `firebase_uid`, `specialization`, `verification_document`, `verification_status`, etc. ✅

### **Step 3: Test Doctor Signup**
1. Go to: `http://localhost:3000/signup?role=doctor`
2. Fill in all fields
3. Upload a document
4. Click "Create Account"

**Expected Backend Logs**:
```
[DEBUG] 🏥 Doctor signup request received
[DEBUG] ✅ Firebase user created: ...
[DEBUG] ✅ Verification file saved: ...
[DEBUG] ✅ User profile created: doctor@example.com
[DEBUG] ✅ Doctor profile created: doctor@example.com  ← NEW!
201 Created ✅
```

### **Step 4: Verify in Database**
```sql
-- Check user_profiles
SELECT id, email, role, firebase_uid
FROM user_profiles
WHERE role = 'doctor'
ORDER BY created_at DESC
LIMIT 5;

-- Check doctor_profiles (should have matching records)
SELECT 
  dp.id,
  dp.user_id,
  dp.specialization,
  dp.verification_document,
  dp.verification_status,
  up.email
FROM doctor_profiles dp
JOIN user_profiles up ON dp.user_id = up.id
ORDER BY dp.created_at DESC
LIMIT 5;
```

**Expected Result**:
Both tables should have matching records for the doctor! ✅

---

## 🔍 Relationship Between Tables

```
user_profiles (role='doctor')
    ↓
    └── doctor_profiles (user_id → user_profiles.id)
```

**Example**:
```sql
-- User profile (basic info)
INSERT INTO user_profiles VALUES (
  'user-uuid-123',
  'firebase-uid-abc',
  'doctor@example.com',
  'password_hash_here',
  'Dr. John',
  'Smith',
  'doctor'
);

-- Doctor profile (doctor-specific info)
INSERT INTO doctor_profiles VALUES (
  'doctor-uuid-456',
  'user-uuid-123',  -- References user_profiles.id
  'firebase-uid-abc',
  'Cardiology',
  'verification_doc.pdf',
  'pending'
);
```

---

## 🆘 Troubleshooting

### **Issue**: "relation 'doctor_profiles' does not exist"
**Solution**: The table wasn't created. Run the migration SQL again.

### **Issue**: "insert or update on table 'doctor_profiles' violates foreign key constraint"
**Solution**: The `user_id` doesn't exist in `user_profiles`. Make sure the user profile is created first (the backend does this automatically).

### **Issue**: "duplicate key value violates unique constraint 'doctor_profiles_firebase_uid_key'"
**Solution**: A doctor profile with this Firebase UID already exists. This is normal - you can't sign up twice with the same account.

---

## 📝 Summary

✅ **Two-table architecture**:
- `user_profiles`: Basic user info for ALL users (patients + doctors)
- `doctor_profiles`: Doctor-specific info (specialization, verification, etc.)

✅ **Migration creates**:
- `doctor_profiles` table if it doesn't exist
- Required columns if they're missing
- Indexes for better performance

✅ **Backend updated** to:
- Create records in BOTH tables during doctor signup
- Clean up both tables if signup fails

---

**Run the migration SQL now and try doctor signup again!** 🚀

**Migration File**: `backend/migrations/add_doctor_fields.sql`

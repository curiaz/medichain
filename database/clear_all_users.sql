-- SQL Script to Clear All Users from Database
-- WARNING: This will permanently delete ALL user data!
-- Run this in Supabase SQL Editor
-- 
-- Usage: Copy and paste this entire script into Supabase SQL Editor and execute

-- Step 1: Delete related data first (in order of dependencies)

-- Delete appointments
DELETE FROM appointments WHERE id != '00000000-0000-0000-0000-000000000000';

-- Delete prescriptions
DELETE FROM prescriptions WHERE id != '00000000-0000-0000-0000-000000000000';

-- Delete AI diagnoses
DELETE FROM ai_diagnoses WHERE id != '00000000-0000-0000-0000-000000000000';

-- Delete medical records
DELETE FROM medical_records WHERE id != '00000000-0000-0000-0000-000000000000';

-- Delete blockchain transactions
DELETE FROM blockchain_transactions WHERE id != '00000000-0000-0000-0000-000000000000';

-- Delete user documents
DELETE FROM user_documents WHERE id != '00000000-0000-0000-0000-000000000000';

-- Delete privacy settings
DELETE FROM privacy_settings WHERE user_firebase_uid != '';

-- Delete credential updates
DELETE FROM credential_updates WHERE id != '00000000-0000-0000-0000-000000000000';

-- Step 2: Delete doctor profiles
DELETE FROM doctor_profiles WHERE id != '00000000-0000-0000-0000-000000000000';

-- Step 3: Delete user profiles (this should cascade to any remaining related data)
DELETE FROM user_profiles WHERE id != '00000000-0000-0000-0000-000000000000';

-- Verify deletion
SELECT 
    (SELECT COUNT(*) FROM user_profiles) as remaining_users,
    (SELECT COUNT(*) FROM doctor_profiles) as remaining_doctors,
    (SELECT COUNT(*) FROM appointments) as remaining_appointments,
    (SELECT COUNT(*) FROM medical_records) as remaining_medical_records;

-- Note: Firebase Auth users are NOT deleted by this script
-- You need to delete them manually from Firebase Console or use Firebase Admin SDK


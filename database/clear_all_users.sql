-- SQL Script to Clear All Users from Database
-- WARNING: This will permanently delete ALL user data!
-- Run this in Supabase SQL Editor
-- 
-- Usage: Copy and paste this entire script into Supabase SQL Editor and execute

-- This script only deletes from tables that actually exist in your schema
-- Tables are checked for existence before deletion

-- Step 1: Delete related data first (in order of dependencies)

-- Delete appointments (if table exists)
DO $$ 
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'appointments') THEN
        DELETE FROM appointments WHERE id != '00000000-0000-0000-0000-000000000000';
        RAISE NOTICE 'Deleted appointments';
    END IF;
END $$;

-- Delete prescriptions (if table exists)
DO $$ 
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'prescriptions') THEN
        DELETE FROM prescriptions WHERE id != '00000000-0000-0000-0000-000000000000';
        RAISE NOTICE 'Deleted prescriptions';
    END IF;
END $$;

-- Delete AI diagnoses (if table exists)
DO $$ 
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'ai_diagnoses') THEN
        DELETE FROM ai_diagnoses WHERE id != '00000000-0000-0000-0000-000000000000';
        RAISE NOTICE 'Deleted AI diagnoses';
    END IF;
END $$;

-- Delete medical records (if table exists)
DO $$ 
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'medical_records') THEN
        DELETE FROM medical_records WHERE id != '00000000-0000-0000-0000-000000000000';
        RAISE NOTICE 'Deleted medical records';
    END IF;
END $$;

-- Delete blockchain transactions (if table exists)
DO $$ 
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'blockchain_transactions') THEN
        DELETE FROM blockchain_transactions WHERE id != '00000000-0000-0000-0000-000000000000';
        RAISE NOTICE 'Deleted blockchain transactions';
    END IF;
END $$;

-- Delete user documents (if table exists)
DO $$ 
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'user_documents') THEN
        DELETE FROM user_documents WHERE id != '00000000-0000-0000-0000-000000000000';
        RAISE NOTICE 'Deleted user documents';
    END IF;
END $$;

-- Delete privacy settings (if table exists)
DO $$ 
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'privacy_settings') THEN
        DELETE FROM privacy_settings WHERE user_firebase_uid != '';
        RAISE NOTICE 'Deleted privacy settings';
    END IF;
END $$;

-- Delete credential updates (if table exists)
DO $$ 
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'credential_updates') THEN
        DELETE FROM credential_updates WHERE id != '00000000-0000-0000-0000-000000000000';
        RAISE NOTICE 'Deleted credential updates';
    END IF;
END $$;

-- Step 2: Delete doctor profiles (if table exists)
DO $$ 
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'doctor_profiles') THEN
        DELETE FROM doctor_profiles WHERE id != '00000000-0000-0000-0000-000000000000';
        RAISE NOTICE 'Deleted doctor profiles';
    END IF;
END $$;

-- Step 3: Delete user profiles (this should cascade to any remaining related data)
DO $$ 
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'user_profiles') THEN
        DELETE FROM user_profiles WHERE id != '00000000-0000-0000-0000-000000000000';
        RAISE NOTICE 'Deleted user profiles';
    END IF;
END $$;

-- Verify deletion
SELECT 
    COALESCE((SELECT COUNT(*) FROM user_profiles), 0) as remaining_users,
    COALESCE((SELECT COUNT(*) FROM doctor_profiles WHERE EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'doctor_profiles')), 0) as remaining_doctors,
    COALESCE((SELECT COUNT(*) FROM appointments WHERE EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'appointments')), 0) as remaining_appointments,
    COALESCE((SELECT COUNT(*) FROM medical_records WHERE EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'medical_records')), 0) as remaining_medical_records;

-- Note: Firebase Auth users are NOT deleted by this script
-- You need to delete them manually from Firebase Console or use Firebase Admin SDK


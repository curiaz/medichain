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
DO $$
DECLARE
    user_count INTEGER := 0;
    doctor_count INTEGER := 0;
    appointment_count INTEGER := 0;
    medical_record_count INTEGER := 0;
BEGIN
    -- Count remaining users
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'user_profiles') THEN
        SELECT COUNT(*) INTO user_count FROM user_profiles;
    END IF;
    
    -- Count remaining doctors
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'doctor_profiles') THEN
        SELECT COUNT(*) INTO doctor_count FROM doctor_profiles;
    END IF;
    
    -- Count remaining appointments
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'appointments') THEN
        SELECT COUNT(*) INTO appointment_count FROM appointments;
    END IF;
    
    -- Count remaining medical records
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'medical_records') THEN
        SELECT COUNT(*) INTO medical_record_count FROM medical_records;
    END IF;
    
    RAISE NOTICE '=== Deletion Summary ===';
    RAISE NOTICE 'Remaining users: %', user_count;
    RAISE NOTICE 'Remaining doctors: %', doctor_count;
    RAISE NOTICE 'Remaining appointments: %', appointment_count;
    RAISE NOTICE 'Remaining medical records: %', medical_record_count;
END $$;

-- Note: Firebase Auth users are NOT deleted by this script
-- You need to delete them manually from Firebase Console or use Firebase Admin SDK


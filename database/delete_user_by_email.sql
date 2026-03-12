-- SQL Script to Delete a Specific User by Email
-- This script deletes the user with email: bosx1negamer25@gmail.com
-- Run this in Supabase SQL Editor
-- 
-- Usage: Copy and paste this entire script into Supabase SQL Editor and execute

DO $$
DECLARE
    target_email TEXT := 'bosx1negamer25@gmail.com';
    user_firebase_uid TEXT;
    user_id UUID;
    doctor_id UUID;
    deleted_count INTEGER;
BEGIN
    -- Get user information
    SELECT id, firebase_uid INTO user_id, user_firebase_uid
    FROM user_profiles
    WHERE email = target_email
    LIMIT 1;
    
    IF user_id IS NULL THEN
        RAISE NOTICE 'User with email % not found', target_email;
        RETURN;
    END IF;
    
    RAISE NOTICE 'Found user: ID=%, Firebase UID=%, Email=%', user_id, user_firebase_uid, target_email;
    
    -- Step 1: Delete related data (in order of dependencies)
    
    -- Delete appointments where user is patient or doctor
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'appointments') THEN
        DELETE FROM appointments 
        WHERE patient_id = user_id OR doctor_id = user_id;
        GET DIAGNOSTICS deleted_count = ROW_COUNT;
        RAISE NOTICE 'Deleted % appointments', deleted_count;
    END IF;
    
    -- Delete prescriptions
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'prescriptions') THEN
        DELETE FROM prescriptions WHERE patient_id = user_id OR doctor_id = user_id;
        GET DIAGNOSTICS deleted_count = ROW_COUNT;
        RAISE NOTICE 'Deleted % prescriptions', deleted_count;
    END IF;
    
    -- Delete AI diagnoses
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'ai_diagnoses') THEN
        DELETE FROM ai_diagnoses WHERE patient_id = user_id OR doctor_id = user_id;
        GET DIAGNOSTICS deleted_count = ROW_COUNT;
        RAISE NOTICE 'Deleted % AI diagnoses', deleted_count;
    END IF;
    
    -- Delete medical records
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'medical_records') THEN
        DELETE FROM medical_records WHERE patient_id = user_id OR doctor_id = user_id;
        GET DIAGNOSTICS deleted_count = ROW_COUNT;
        RAISE NOTICE 'Deleted % medical records', deleted_count;
    END IF;
    
    -- Delete blockchain transactions
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'blockchain_transactions') THEN
        DELETE FROM blockchain_transactions WHERE user_id = user_id;
        GET DIAGNOSTICS deleted_count = ROW_COUNT;
        RAISE NOTICE 'Deleted % blockchain transactions', deleted_count;
    END IF;
    
    -- Delete user documents
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'user_documents') THEN
        DELETE FROM user_documents WHERE user_id = user_id;
        GET DIAGNOSTICS deleted_count = ROW_COUNT;
        RAISE NOTICE 'Deleted % user documents', deleted_count;
    END IF;
    
    -- Delete privacy settings
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'privacy_settings') THEN
        DELETE FROM privacy_settings WHERE user_firebase_uid = user_firebase_uid;
        GET DIAGNOSTICS deleted_count = ROW_COUNT;
        RAISE NOTICE 'Deleted % privacy settings', deleted_count;
    END IF;
    
    -- Delete credential updates
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'credential_updates') THEN
        DELETE FROM credential_updates WHERE user_id = user_id;
        GET DIAGNOSTICS deleted_count = ROW_COUNT;
        RAISE NOTICE 'Deleted % credential updates', deleted_count;
    END IF;
    
    -- Step 2: Delete doctor-related data if user is a doctor
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'doctor_profiles') THEN
        SELECT id INTO doctor_id
        FROM doctor_profiles
        WHERE user_id = user_id OR firebase_uid = user_firebase_uid
        LIMIT 1;
        
        IF doctor_id IS NOT NULL THEN
            RAISE NOTICE 'User is a doctor, deleting doctor-related data...';
            
            -- Delete doctor documents
            IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'doctor_documents') THEN
                DELETE FROM doctor_documents WHERE doctor_id = doctor_id OR firebase_uid = user_firebase_uid;
                GET DIAGNOSTICS deleted_count = ROW_COUNT;
                RAISE NOTICE 'Deleted % doctor documents', deleted_count;
            END IF;
            
            -- Delete doctor profile
            DELETE FROM doctor_profiles WHERE id = doctor_id;
            GET DIAGNOSTICS deleted_count = ROW_COUNT;
            RAISE NOTICE 'Deleted % doctor profile(s)', deleted_count;
        END IF;
    END IF;
    
    -- Step 3: Delete user profile (this should cascade to any remaining related data)
    DELETE FROM user_profiles WHERE id = user_id;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    IF deleted_count > 0 THEN
        RAISE NOTICE '✅ Successfully deleted user profile for %', target_email;
    ELSE
        RAISE NOTICE '⚠️  User profile was not deleted (may have been deleted already)';
    END IF;
    
    -- Verify deletion
    SELECT COUNT(*) INTO deleted_count
    FROM user_profiles
    WHERE email = target_email;
    
    IF deleted_count = 0 THEN
        RAISE NOTICE '✅ Verification: User % has been completely removed from database', target_email;
    ELSE
        RAISE NOTICE '⚠️  Warning: User % still exists in database (count: %)', target_email, deleted_count;
    END IF;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '❌ Error deleting user: %', SQLERRM;
        RAISE;
END $$;

-- Note: Firebase Auth user is NOT deleted by this script
-- You need to delete it manually from Firebase Console or use Firebase Admin SDK
-- To delete from Firebase, use the Firebase Console or run:
-- firebase auth:delete <firebase_uid>


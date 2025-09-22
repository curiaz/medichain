-- Verification Query - Run this after setup to check everything is working
-- This will show you the status of RLS on all your tables

SELECT
    schemaname,
    tablename,
    rowsecurity as rls_enabled,
    CASE
        WHEN rowsecurity THEN '✅ RLS Enabled'
        ELSE '❌ RLS Disabled'
    END as status
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('user_profiles', 'doctor_profiles', 'medical_records', 'ai_diagnoses', 'appointments', 'prescriptions')
ORDER BY tablename;

-- Check if policies exist
SELECT
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual
FROM pg_policies
WHERE schemaname = 'public'
AND tablename IN ('user_profiles', 'doctor_profiles', 'medical_records', 'ai_diagnoses', 'appointments', 'prescriptions')
ORDER BY tablename, policyname;

-- Check if helper functions exist
SELECT
    proname as function_name,
    pg_get_function_identity_arguments(oid) as arguments,
    obj_description(oid, 'pg_proc') as description
FROM pg_proc
WHERE proname IN ('uid', 'user_role', 'is_admin', 'is_doctor')
AND pg_function_is_visible(oid)
ORDER BY proname;</content>
<parameter name="filePath">c:\Users\abayo\OneDrive\Desktop\thesis\medichain\verify_setup.sql

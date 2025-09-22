-- FIX RLS POLICIES FOR FIREBASE AUTHENTICATION
-- Run this SQL in your Supabase dashboard SQL editor
-- This will completely replace all RLS policies with Firebase-compatible ones

-- ==============================================
-- STEP 1: DROP ALL EXISTING POLICIES
-- ==============================================

-- Drop ALL policies from user_profiles table
DO $$
DECLARE
    policy_name TEXT;
BEGIN
    FOR policy_name IN
        SELECT polname
        FROM pg_policy
        WHERE polrelid = 'user_profiles'::regclass
    LOOP
        EXECUTE 'DROP POLICY IF EXISTS "' || policy_name || '" ON user_profiles';
    END LOOP;
END $$;

-- Drop ALL policies from doctor_profiles table
DO $$
DECLARE
    policy_name TEXT;
BEGIN
    FOR policy_name IN
        SELECT polname
        FROM pg_policy
        WHERE polrelid = 'doctor_profiles'::regclass
    LOOP
        EXECUTE 'DROP POLICY IF EXISTS "' || policy_name || '" ON doctor_profiles';
    END LOOP;
END $$;

-- Drop ALL policies from medical_records table
DO $$
DECLARE
    policy_name TEXT;
BEGIN
    FOR policy_name IN
        SELECT polname
        FROM pg_policy
        WHERE polrelid = 'medical_records'::regclass
    LOOP
        EXECUTE 'DROP POLICY IF EXISTS "' || policy_name || '" ON medical_records';
    END LOOP;
END $$;

-- Drop ALL policies from ai_diagnoses table
DO $$
DECLARE
    policy_name TEXT;
BEGIN
    FOR policy_name IN
        SELECT polname
        FROM pg_policy
        WHERE polrelid = 'ai_diagnoses'::regclass
    LOOP
        EXECUTE 'DROP POLICY IF EXISTS "' || policy_name || '" ON ai_diagnoses';
    END LOOP;
END $$;

-- Drop ALL policies from prescriptions table
DO $$
DECLARE
    policy_name TEXT;
BEGIN
    FOR policy_name IN
        SELECT polname
        FROM pg_policy
        WHERE polrelid = 'prescriptions'::regclass
    LOOP
        EXECUTE 'DROP POLICY IF EXISTS "' || policy_name || '" ON prescriptions';
    END LOOP;
END $$;

-- Drop ALL policies from appointments table
DO $$
DECLARE
    policy_name TEXT;
BEGIN
    FOR policy_name IN
        SELECT polname
        FROM pg_policy
        WHERE polrelid = 'appointments'::regclass
    LOOP
        EXECUTE 'DROP POLICY IF EXISTS "' || policy_name || '" ON appointments';
    END LOOP;
END $$;

-- ==============================================
-- STEP 2: CREATE NEW FIREBASE-COMPATIBLE POLICIES
-- ==============================================

-- Service role can manage all tables (for backend operations)
CREATE POLICY "Service role can manage user_profiles" ON user_profiles FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role can manage doctor_profiles" ON doctor_profiles FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role can manage medical_records" ON medical_records FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role can manage ai_diagnoses" ON ai_diagnoses FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role can manage prescriptions" ON prescriptions FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role can manage appointments" ON appointments FOR ALL USING (auth.role() = 'service_role');

-- Allow authenticated users to perform operations (backend controls access)
CREATE POLICY "Allow authenticated operations on user_profiles" ON user_profiles FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Allow authenticated operations on doctor_profiles" ON doctor_profiles FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Allow authenticated operations on medical_records" ON medical_records FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Allow authenticated operations on ai_diagnoses" ON ai_diagnoses FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Allow authenticated operations on prescriptions" ON prescriptions FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Allow authenticated operations on appointments" ON appointments FOR ALL USING (auth.role() = 'authenticated');

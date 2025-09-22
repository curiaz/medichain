-- Complete Firebase RLS Setup Script
-- Run this in Supabase SQL Editor to reset and apply all policies

-- ==============================================
-- STEP 1: DROP EXISTING POLICIES
-- ==============================================

-- Drop all existing policies for user_profiles
DROP POLICY IF EXISTS "Users can view own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;
DROP POLICY IF EXISTS "Doctors can view patient profiles" ON user_profiles;
DROP POLICY IF EXISTS "Admins can view all profiles" ON user_profiles;
DROP POLICY IF EXISTS "Service role can manage profiles" ON user_profiles;

-- Drop all existing policies for doctor_profiles
DROP POLICY IF EXISTS "Users can view own doctor profile" ON doctor_profiles;
DROP POLICY IF EXISTS "Users can insert own doctor profile" ON doctor_profiles;
DROP POLICY IF EXISTS "Users can update own doctor profile" ON doctor_profiles;
DROP POLICY IF EXISTS "Patients can view assigned doctors" ON doctor_profiles;
DROP POLICY IF EXISTS "Public can view verified doctors" ON doctor_profiles;
DROP POLICY IF EXISTS "Service role can manage doctor profiles" ON doctor_profiles;

-- Drop all existing policies for medical_records
DROP POLICY IF EXISTS "Patients can view own records" ON medical_records;
DROP POLICY IF EXISTS "Doctors can view patient records" ON medical_records;
DROP POLICY IF EXISTS "Doctors can create patient records" ON medical_records;
DROP POLICY IF EXISTS "Doctors can update their records" ON medical_records;
DROP POLICY IF EXISTS "Admins can view all records" ON medical_records;
DROP POLICY IF EXISTS "Service role can manage records" ON medical_records;

-- Drop all existing policies for ai_diagnoses
DROP POLICY IF EXISTS "Users can view own AI diagnoses" ON ai_diagnoses;
DROP POLICY IF EXISTS "Users can create own AI diagnoses" ON ai_diagnoses;
DROP POLICY IF EXISTS "Doctors can view patient AI diagnoses" ON ai_diagnoses;
DROP POLICY IF EXISTS "Service role can manage AI diagnoses" ON ai_diagnoses;

-- Drop all existing policies for appointments
DROP POLICY IF EXISTS "Users can view own appointments" ON appointments;
DROP POLICY IF EXISTS "Patients can create appointments" ON appointments;
DROP POLICY IF EXISTS "Doctors can update appointments" ON appointments;
DROP POLICY IF EXISTS "Service role can manage appointments" ON appointments;

-- Drop all existing policies for prescriptions
DROP POLICY IF EXISTS "Patients can view own prescriptions" ON prescriptions;
DROP POLICY IF EXISTS "Doctors can view prescriptions they created" ON prescriptions;
DROP POLICY IF EXISTS "Doctors can create prescriptions" ON prescriptions;
DROP POLICY IF EXISTS "Doctors can update their prescriptions" ON prescriptions;
DROP POLICY IF EXISTS "Service role can manage prescriptions" ON prescriptions;

-- Drop helper functions if they exist
DROP FUNCTION IF EXISTS auth.uid();
DROP FUNCTION IF EXISTS auth.user_role();
DROP FUNCTION IF EXISTS auth.is_admin();
DROP FUNCTION IF EXISTS auth.is_doctor();

-- ==============================================
-- STEP 2: CREATE HELPER FUNCTIONS
-- ==============================================

-- Function to get current user ID from JWT
CREATE OR REPLACE FUNCTION auth.uid()
RETURNS TEXT
LANGUAGE SQL
STABLE
AS $$
    SELECT auth.jwt() ->> 'sub';
$$;

-- Function to get current user role
CREATE OR REPLACE FUNCTION auth.user_role()
RETURNS TEXT
LANGUAGE SQL
STABLE
AS $$
    SELECT role FROM user_profiles
    WHERE firebase_uid = auth.uid();
$$;

-- Function to check if user is admin
CREATE OR REPLACE FUNCTION auth.is_admin()
RETURNS BOOLEAN
LANGUAGE SQL
STABLE
AS $$
    SELECT EXISTS (
        SELECT 1 FROM user_profiles
        WHERE firebase_uid = auth.uid()
        AND role = 'admin'
    );
$$;

-- Function to check if user is doctor
CREATE OR REPLACE FUNCTION auth.is_doctor()
RETURNS BOOLEAN
LANGUAGE SQL
STABLE
AS $$
    SELECT EXISTS (
        SELECT 1 FROM user_profiles
        WHERE firebase_uid = auth.uid()
        AND role = 'doctor'
    );
$$;

-- ==============================================
-- STEP 3: ENABLE RLS ON TABLES
-- ==============================================

-- Enable RLS on all tables
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE doctor_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE medical_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_diagnoses ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE prescriptions ENABLE ROW LEVEL SECURITY;

-- ==============================================
-- STEP 4: CREATE NEW POLICIES
-- ==============================================

-- USER_PROFILES POLICIES
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (auth.jwt() ->> 'sub' = firebase_uid);

CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.jwt() ->> 'sub' = firebase_uid);

CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.jwt() ->> 'sub' = firebase_uid);

CREATE POLICY "Doctors can view patient profiles" ON user_profiles
    FOR SELECT USING (
        role = 'patient' AND
        EXISTS (
            SELECT 1 FROM appointments a
            JOIN user_profiles d ON d.firebase_uid = a.doctor_firebase_uid
            WHERE a.patient_firebase_uid = user_profiles.firebase_uid
            AND d.firebase_uid = auth.jwt() ->> 'sub'
        )
    );

CREATE POLICY "Admins can view all profiles" ON user_profiles
    FOR SELECT USING (auth.is_admin());

CREATE POLICY "Service role can manage profiles" ON user_profiles
    FOR ALL USING (auth.role() = 'service_role');

-- DOCTOR_PROFILES POLICIES
CREATE POLICY "Users can view own doctor profile" ON doctor_profiles
    FOR SELECT USING (auth.jwt() ->> 'sub' = firebase_uid);

CREATE POLICY "Users can insert own doctor profile" ON doctor_profiles
    FOR INSERT WITH CHECK (auth.jwt() ->> 'sub' = firebase_uid);

CREATE POLICY "Users can update own doctor profile" ON doctor_profiles
    FOR UPDATE USING (auth.jwt() ->> 'sub' = firebase_uid);

CREATE POLICY "Patients can view assigned doctors" ON doctor_profiles
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM appointments a
            WHERE a.doctor_firebase_uid = doctor_profiles.firebase_uid
            AND a.patient_firebase_uid = auth.jwt() ->> 'sub'
        )
    );

CREATE POLICY "Public can view verified doctors" ON doctor_profiles
    FOR SELECT USING (is_verified = true);

CREATE POLICY "Service role can manage doctor profiles" ON doctor_profiles
    FOR ALL USING (auth.role() = 'service_role');

-- MEDICAL_RECORDS POLICIES
CREATE POLICY "Patients can view own records" ON medical_records
    FOR SELECT USING (auth.jwt() ->> 'sub' = patient_firebase_uid);

CREATE POLICY "Doctors can view patient records" ON medical_records
    FOR SELECT USING (
        auth.jwt() ->> 'sub' = doctor_firebase_uid OR
        EXISTS (
            SELECT 1 FROM appointments a
            WHERE a.patient_firebase_uid = medical_records.patient_firebase_uid
            AND a.doctor_firebase_uid = auth.jwt() ->> 'sub'
        )
    );

CREATE POLICY "Doctors can create patient records" ON medical_records
    FOR INSERT WITH CHECK (auth.is_doctor());

CREATE POLICY "Doctors can update their records" ON medical_records
    FOR UPDATE USING (auth.jwt() ->> 'sub' = doctor_firebase_uid);

CREATE POLICY "Admins can view all records" ON medical_records
    FOR SELECT USING (auth.is_admin());

CREATE POLICY "Service role can manage records" ON medical_records
    FOR ALL USING (auth.role() = 'service_role');

-- AI_DIAGNOSES POLICIES
CREATE POLICY "Users can view own AI diagnoses" ON ai_diagnoses
    FOR SELECT USING (auth.jwt() ->> 'sub' = user_firebase_uid);

CREATE POLICY "Users can create own AI diagnoses" ON ai_diagnoses
    FOR INSERT WITH CHECK (auth.jwt() ->> 'sub' = user_firebase_uid);

CREATE POLICY "Doctors can view patient AI diagnoses" ON ai_diagnoses
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM appointments a
            WHERE a.patient_firebase_uid = ai_diagnoses.user_firebase_uid
            AND a.doctor_firebase_uid = auth.jwt() ->> 'sub'
        )
    );

CREATE POLICY "Service role can manage AI diagnoses" ON ai_diagnoses
    FOR ALL USING (auth.role() = 'service_role');

-- APPOINTMENTS POLICIES
CREATE POLICY "Users can view own appointments" ON appointments
    FOR SELECT USING (
        auth.jwt() ->> 'sub' = patient_firebase_uid OR
        auth.jwt() ->> 'sub' = doctor_firebase_uid
    );

CREATE POLICY "Patients can create appointments" ON appointments
    FOR INSERT WITH CHECK (
        auth.jwt() ->> 'sub' = patient_firebase_uid AND
        NOT auth.is_doctor()
    );

CREATE POLICY "Doctors can update appointments" ON appointments
    FOR UPDATE USING (auth.jwt() ->> 'sub' = doctor_firebase_uid);

CREATE POLICY "Service role can manage appointments" ON appointments
    FOR ALL USING (auth.role() = 'service_role');

-- PRESCRIPTIONS POLICIES
CREATE POLICY "Patients can view own prescriptions" ON prescriptions
    FOR SELECT USING (auth.jwt() ->> 'sub' = patient_firebase_uid);

CREATE POLICY "Doctors can view prescriptions they created" ON prescriptions
    FOR SELECT USING (auth.jwt() ->> 'sub' = doctor_firebase_uid);

CREATE POLICY "Doctors can create prescriptions" ON prescriptions
    FOR INSERT WITH CHECK (auth.is_doctor());

CREATE POLICY "Doctors can update their prescriptions" ON prescriptions
    FOR UPDATE USING (auth.jwt() ->> 'sub' = doctor_firebase_uid);

CREATE POLICY "Service role can manage prescriptions" ON prescriptions
    FOR ALL USING (auth.role() = 'service_role');

-- ==============================================
-- SETUP COMPLETE
-- ==============================================

-- Verify setup by running this query:
-- SELECT schemaname, tablename, rowsecurity
-- FROM pg_tables
-- WHERE schemaname = 'public'
-- AND tablename IN ('user_profiles', 'doctor_profiles', 'medical_records', 'ai_diagnoses', 'appointments', 'prescriptions')
-- ORDER BY tablename;</content>
<parameter name="filePath">c:\Users\abayo\OneDrive\Desktop\thesis\medichain\complete_firebase_setup.sql

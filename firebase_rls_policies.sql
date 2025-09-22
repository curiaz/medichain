-- Firebase-Integrated Row Level Security (RLS) Policies for MediChain
-- Run this SQL in your Supabase dashboard SQL editor AFTER creating the tables

-- Enable RLS on all tables
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE doctor_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE medical_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_diagnoses ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE prescriptions ENABLE ROW LEVEL SECURITY;

-- ==============================================
-- USER_PROFILES TABLE POLICIES
-- ==============================================

-- Policy: Users can view their own profile
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (auth.jwt() ->> 'sub' = firebase_uid);

-- Policy: Users can insert their own profile (for signup)
CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.jwt() ->> 'sub' = firebase_uid);

-- Policy: Users can update their own profile
CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.jwt() ->> 'sub' = firebase_uid);

-- Policy: Doctors can view patient profiles for their appointments
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

-- Policy: Admins can view all profiles
CREATE POLICY "Admins can view all profiles" ON user_profiles
    FOR SELECT USING (auth.is_admin());

-- Policy: Service role can manage all profiles (for backend operations)
CREATE POLICY "Service role can manage profiles" ON user_profiles
    FOR ALL USING (auth.role() = 'service_role');

-- ==============================================
-- DOCTOR_PROFILES TABLE POLICIES
-- ==============================================

-- Policy: Users can view their own doctor profile
CREATE POLICY "Users can view own doctor profile" ON doctor_profiles
    FOR SELECT USING (auth.jwt() ->> 'sub' = firebase_uid);

-- Policy: Users can insert their own doctor profile
CREATE POLICY "Users can insert own doctor profile" ON doctor_profiles
    FOR INSERT WITH CHECK (auth.jwt() ->> 'sub' = firebase_uid);

-- Policy: Users can update their own doctor profile
CREATE POLICY "Users can update own doctor profile" ON doctor_profiles
    FOR UPDATE USING (auth.jwt() ->> 'sub' = firebase_uid);

-- Policy: Patients can view doctor profiles for their appointments
CREATE POLICY "Patients can view assigned doctors" ON doctor_profiles
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM appointments a
            WHERE a.doctor_firebase_uid = doctor_profiles.firebase_uid
            AND a.patient_firebase_uid = auth.jwt() ->> 'sub'
        )
    );

-- Policy: All users can view verified doctor profiles (for booking)
CREATE POLICY "Public can view verified doctors" ON doctor_profiles
    FOR SELECT USING (is_verified = true);

-- Policy: Service role can manage doctor profiles
CREATE POLICY "Service role can manage doctor profiles" ON doctor_profiles
    FOR ALL USING (auth.role() = 'service_role');

-- ==============================================
-- MEDICAL_RECORDS TABLE POLICIES
-- ==============================================

-- Policy: Patients can view their own medical records
CREATE POLICY "Patients can view own records" ON medical_records
    FOR SELECT USING (auth.jwt() ->> 'sub' = patient_firebase_uid);

-- Policy: Doctors can view records for their patients
CREATE POLICY "Doctors can view patient records" ON medical_records
    FOR SELECT USING (
        auth.jwt() ->> 'sub' = doctor_firebase_uid OR
        EXISTS (
            SELECT 1 FROM appointments a
            WHERE a.patient_firebase_uid = medical_records.patient_firebase_uid
            AND a.doctor_firebase_uid = auth.jwt() ->> 'sub'
        )
    );

-- Policy: Doctors can create records for their patients
CREATE POLICY "Doctors can create patient records" ON medical_records
    FOR INSERT WITH CHECK (auth.is_doctor());

-- Policy: Doctors can update records they created
CREATE POLICY "Doctors can update their records" ON medical_records
    FOR UPDATE USING (auth.jwt() ->> 'sub' = doctor_firebase_uid);

-- Policy: Admins can view all records
CREATE POLICY "Admins can view all records" ON medical_records
    FOR SELECT USING (auth.is_admin());

-- Policy: Service role can manage all records
CREATE POLICY "Service role can manage records" ON medical_records
    FOR ALL USING (auth.role() = 'service_role');

-- ==============================================
-- AI_DIAGNOSES TABLE POLICIES
-- ==============================================

-- Policy: Users can view their own AI diagnoses
CREATE POLICY "Users can view own AI diagnoses" ON ai_diagnoses
    FOR SELECT USING (auth.jwt() ->> 'sub' = user_firebase_uid);

-- Policy: Users can create their own AI diagnosis records
CREATE POLICY "Users can create own AI diagnoses" ON ai_diagnoses
    FOR INSERT WITH CHECK (auth.jwt() ->> 'sub' = user_firebase_uid);

-- Policy: Doctors can view AI diagnoses for their patients
CREATE POLICY "Doctors can view patient AI diagnoses" ON ai_diagnoses
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM appointments a
            WHERE a.patient_firebase_uid = ai_diagnoses.user_firebase_uid
            AND a.doctor_firebase_uid = auth.jwt() ->> 'sub'
        )
    );

-- Policy: Service role can manage AI diagnoses
CREATE POLICY "Service role can manage AI diagnoses" ON ai_diagnoses
    FOR ALL USING (auth.role() = 'service_role');

-- ==============================================
-- APPOINTMENTS TABLE POLICIES
-- ==============================================

-- Policy: Users can view their own appointments
CREATE POLICY "Users can view own appointments" ON appointments
    FOR SELECT USING (
        auth.jwt() ->> 'sub' = patient_firebase_uid OR
        auth.jwt() ->> 'sub' = doctor_firebase_uid
    );

-- Policy: Patients can create appointments
CREATE POLICY "Patients can create appointments" ON appointments
    FOR INSERT WITH CHECK (
        auth.jwt() ->> 'sub' = patient_firebase_uid AND
        NOT auth.is_doctor()
    );

-- Policy: Doctors can update appointment status
CREATE POLICY "Doctors can update appointments" ON appointments
    FOR UPDATE USING (auth.jwt() ->> 'sub' = doctor_firebase_uid);

-- Policy: Service role can manage appointments
CREATE POLICY "Service role can manage appointments" ON appointments
    FOR ALL USING (auth.role() = 'service_role');

-- ==============================================
-- PRESCRIPTIONS TABLE POLICIES
-- ==============================================

-- Policy: Patients can view their own prescriptions
CREATE POLICY "Patients can view own prescriptions" ON prescriptions
    FOR SELECT USING (auth.jwt() ->> 'sub' = patient_firebase_uid);

-- Policy: Doctors can view prescriptions they created
CREATE POLICY "Doctors can view prescriptions they created" ON prescriptions
    FOR SELECT USING (auth.jwt() ->> 'sub' = doctor_firebase_uid);

-- Policy: Doctors can create prescriptions for their patients
CREATE POLICY "Doctors can create prescriptions" ON prescriptions
    FOR INSERT WITH CHECK (auth.is_doctor());

-- Policy: Doctors can update prescriptions they created
CREATE POLICY "Doctors can update their prescriptions" ON prescriptions
    FOR UPDATE USING (auth.jwt() ->> 'sub' = doctor_firebase_uid);

-- Policy: Service role can manage prescriptions
CREATE POLICY "Service role can manage prescriptions" ON prescriptions
    FOR ALL USING (auth.role() = 'service_role');

-- ==============================================
-- HELPER FUNCTIONS (Create these first)
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

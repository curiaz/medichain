-- Updated RLS Policies for Firebase Authentication
-- Run this SQL in your Supabase dashboard SQL editor
-- This will replace the existing RLS policies to work with Firebase authentication

-- ==============================================
-- DROP EXISTING POLICIES
-- ==============================================

-- Drop all existing policies for user_profiles
DROP POLICY IF EXISTS "Users can view own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON user_profiles;

-- Drop all existing policies for doctor_profiles
DROP POLICY IF EXISTS "Doctors can manage own profile" ON doctor_profiles;
DROP POLICY IF EXISTS "All users can view doctor profiles" ON doctor_profiles;

-- Drop all existing policies for medical_records
DROP POLICY IF EXISTS "Patients can view own medical records" ON medical_records;
DROP POLICY IF EXISTS "Doctors can view their patients' records" ON medical_records;
DROP POLICY IF EXISTS "Doctors can create medical records" ON medical_records;
DROP POLICY IF EXISTS "Doctors can update medical records" ON medical_records;

-- Drop all existing policies for ai_diagnoses
DROP POLICY IF EXISTS "Users can view own AI diagnoses" ON ai_diagnoses;
DROP POLICY IF EXISTS "Users can create AI diagnoses" ON ai_diagnoses;
DROP POLICY IF EXISTS "Users can update own AI diagnoses" ON ai_diagnoses;

-- Drop all existing policies for prescriptions
DROP POLICY IF EXISTS "Patients can view own prescriptions" ON prescriptions;
DROP POLICY IF EXISTS "Doctors can view their prescriptions" ON prescriptions;
DROP POLICY IF EXISTS "Doctors can create prescriptions" ON prescriptions;
DROP POLICY IF EXISTS "Doctors can update their prescriptions" ON prescriptions;

-- Drop all existing policies for appointments
DROP POLICY IF EXISTS "Patients can view own appointments" ON appointments;
DROP POLICY IF EXISTS "Doctors can view their appointments" ON appointments;
DROP POLICY IF EXISTS "Patients can create appointments" ON appointments;
DROP POLICY IF EXISTS "Users can update their appointments" ON appointments;

-- ==============================================
-- NEW RLS POLICIES FOR FIREBASE AUTHENTICATION
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

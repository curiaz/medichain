-- Drop existing policies before recreating them
-- Run this FIRST if you get "policy already exists" errors

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

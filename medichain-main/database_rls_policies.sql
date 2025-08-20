-- Row Level Security (RLS) Policies for MediChain Database
-- Run this SQL in your Supabase SQL editor after creating the tables

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE doctors ENABLE ROW LEVEL SECURITY;
ALTER TABLE medical_records ENABLE ROW LEVEL SECURITY;

-- ==============================================
-- PROFILES TABLE POLICIES
-- ==============================================

-- Policy: Users can view their own profile
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

-- Policy: Users can insert their own profile (for signup)
CREATE POLICY "Users can insert own profile" ON profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Policy: Users can update their own profile
CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

-- Policy: Allow service role to manage profiles (for backend operations)
CREATE POLICY "Service role can manage profiles" ON profiles
    FOR ALL USING (auth.role() = 'service_role');

-- ==============================================
-- PATIENTS TABLE POLICIES
-- ==============================================

-- Policy: Users can view their own patient record
CREATE POLICY "Users can view own patient record" ON patients
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = patients.user_id 
            AND profiles.id = auth.uid()
        )
    );

-- Policy: Users can insert their own patient record
CREATE POLICY "Users can insert own patient record" ON patients
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = patients.user_id 
            AND profiles.id = auth.uid()
            AND profiles.role = 'patient'
        )
    );

-- Policy: Users can update their own patient record
CREATE POLICY "Users can update own patient record" ON patients
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = patients.user_id 
            AND profiles.id = auth.uid()
        )
    );

-- Policy: Doctors can view patient records for their patients
CREATE POLICY "Doctors can view assigned patients" ON patients
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'doctor'
        )
        AND EXISTS (
            SELECT 1 FROM medical_records mr
            JOIN doctors d ON d.id = mr.doctor_id
            JOIN profiles dp ON dp.id = d.user_id
            WHERE mr.patient_id = patients.id
            AND dp.id = auth.uid()
        )
    );

-- Policy: Service role can manage patients
CREATE POLICY "Service role can manage patients" ON patients
    FOR ALL USING (auth.role() = 'service_role');

-- ==============================================
-- DOCTORS TABLE POLICIES
-- ==============================================

-- Policy: Users can view their own doctor record
CREATE POLICY "Users can view own doctor record" ON doctors
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = doctors.user_id 
            AND profiles.id = auth.uid()
        )
    );

-- Policy: Users can insert their own doctor record
CREATE POLICY "Users can insert own doctor record" ON doctors
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = doctors.user_id 
            AND profiles.id = auth.uid()
            AND profiles.role = 'doctor'
        )
    );

-- Policy: Users can update their own doctor record
CREATE POLICY "Users can update own doctor record" ON doctors
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = doctors.user_id 
            AND profiles.id = auth.uid()
        )
    );

-- Policy: Patients can view doctors who have treated them
CREATE POLICY "Patients can view their doctors" ON doctors
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'patient'
        )
        AND EXISTS (
            SELECT 1 FROM medical_records mr
            JOIN patients p ON p.id = mr.patient_id
            JOIN profiles pp ON pp.id = p.user_id
            WHERE mr.doctor_id = doctors.id
            AND pp.id = auth.uid()
        )
    );

-- Policy: Service role can manage doctors
CREATE POLICY "Service role can manage doctors" ON doctors
    FOR ALL USING (auth.role() = 'service_role');

-- ==============================================
-- MEDICAL RECORDS TABLE POLICIES
-- ==============================================

-- Policy: Patients can view their own medical records
CREATE POLICY "Patients can view own medical records" ON medical_records
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM patients p
            JOIN profiles pp ON pp.id = p.user_id
            WHERE p.id = medical_records.patient_id
            AND pp.id = auth.uid()
            AND pp.role = 'patient'
        )
    );

-- Policy: Doctors can view medical records they created
CREATE POLICY "Doctors can view own medical records" ON medical_records
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM doctors d
            JOIN profiles dp ON dp.id = d.user_id
            WHERE d.id = medical_records.doctor_id
            AND dp.id = auth.uid()
            AND dp.role = 'doctor'
        )
    );

-- Policy: Doctors can create medical records
CREATE POLICY "Doctors can create medical records" ON medical_records
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM doctors d
            JOIN profiles dp ON dp.id = d.user_id
            WHERE d.id = medical_records.doctor_id
            AND dp.id = auth.uid()
            AND dp.role = 'doctor'
        )
    );

-- Policy: Doctors can update medical records they created
CREATE POLICY "Doctors can update own medical records" ON medical_records
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM doctors d
            JOIN profiles dp ON dp.id = d.user_id
            WHERE d.id = medical_records.doctor_id
            AND dp.id = auth.uid()
            AND dp.role = 'doctor'
        )
    );

-- Policy: Admins can view all medical records
CREATE POLICY "Admins can view all medical records" ON medical_records
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'admin'
        )
    );

-- Policy: Service role can manage medical records
CREATE POLICY "Service role can manage medical records" ON medical_records
    FOR ALL USING (auth.role() = 'service_role');

-- ==============================================
-- FUNCTIONS AND TRIGGERS
-- ==============================================

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for profiles table
CREATE TRIGGER update_profiles_updated_at 
    BEFORE UPDATE ON profiles 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ==============================================
-- ADDITIONAL HELPER POLICIES
-- ==============================================

-- Allow authenticated users to read their own auth.users data
-- This might be needed for some operations
CREATE POLICY "Users can view own auth data" ON auth.users
    FOR SELECT USING (auth.uid() = id);

-- ==============================================
-- INDEXES FOR PERFORMANCE
-- ==============================================

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_role ON profiles(role);
CREATE INDEX IF NOT EXISTS idx_patients_user_id ON patients(user_id);
CREATE INDEX IF NOT EXISTS idx_doctors_user_id ON doctors(user_id);
CREATE INDEX IF NOT EXISTS idx_doctors_license ON doctors(license_number);
CREATE INDEX IF NOT EXISTS idx_medical_records_patient ON medical_records(patient_id);
CREATE INDEX IF NOT EXISTS idx_medical_records_doctor ON medical_records(doctor_id);
CREATE INDEX IF NOT EXISTS idx_medical_records_created_at ON medical_records(created_at);

-- ==============================================
-- GRANT PERMISSIONS
-- ==============================================

-- Grant necessary permissions to authenticated users
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT SELECT, INSERT, UPDATE ON profiles TO authenticated;
GRANT SELECT, INSERT, UPDATE ON patients TO authenticated;
GRANT SELECT, INSERT, UPDATE ON doctors TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON medical_records TO authenticated;

-- Grant permissions to service role (for backend operations)
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;

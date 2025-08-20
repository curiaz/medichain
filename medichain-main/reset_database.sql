-- Complete database reset for Medichain
-- This will drop all existing tables and recreate them clean
-- Run this in your Supabase SQL Editor

-- Step 1: Drop all existing tables (in correct order to handle foreign key dependencies)
DROP TABLE IF EXISTS medical_records CASCADE;
DROP TABLE IF EXISTS patients CASCADE;
DROP TABLE IF EXISTS doctors CASCADE;
DROP TABLE IF EXISTS profiles CASCADE;

-- Step 2: Create profiles table (clean version with separate name fields)
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('doctor', 'patient', 'admin')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 3: Create doctors table
CREATE TABLE doctors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    specialization TEXT,
    license_number TEXT,
    hospital_affiliation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 4: Create patients table
CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    date_of_birth DATE,
    gender TEXT,
    blood_type TEXT,
    emergency_contact TEXT,
    emergency_phone TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 5: Create medical_records table
CREATE TABLE medical_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    doctor_id UUID REFERENCES doctors(id),
    record_type TEXT NOT NULL,
    encrypted_data TEXT NOT NULL,
    data_hash TEXT NOT NULL,
    blockchain_hash TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 6: Enable Row Level Security (RLS)
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE doctors ENABLE ROW LEVEL SECURITY;
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE medical_records ENABLE ROW LEVEL SECURITY;

-- Step 7: Create RLS Policies

-- Profiles policies
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Service role can do anything on profiles" ON profiles
    FOR ALL USING (auth.role() = 'service_role');

-- Doctors policies
CREATE POLICY "Doctors can view own data" ON doctors
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Doctors can update own data" ON doctors
    FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Service role can do anything on doctors" ON doctors
    FOR ALL USING (auth.role() = 'service_role');

-- Patients policies
CREATE POLICY "Patients can view own data" ON patients
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Patients can update own data" ON patients
    FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Service role can do anything on patients" ON patients
    FOR ALL USING (auth.role() = 'service_role');

-- Medical records policies
CREATE POLICY "Patients can view own records" ON medical_records
    FOR SELECT USING (
        patient_id IN (
            SELECT id FROM patients WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Doctors can view records they created" ON medical_records
    FOR SELECT USING (
        doctor_id IN (
            SELECT id FROM doctors WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Doctors can create records" ON medical_records
    FOR INSERT WITH CHECK (
        doctor_id IN (
            SELECT id FROM doctors WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Service role can do anything on medical_records" ON medical_records
    FOR ALL USING (auth.role() = 'service_role');

-- Step 8: Create indexes for better performance
CREATE INDEX idx_profiles_email ON profiles(email);
CREATE INDEX idx_profiles_role ON profiles(role);
CREATE INDEX idx_doctors_user_id ON doctors(user_id);
CREATE INDEX idx_patients_user_id ON patients(user_id);
CREATE INDEX idx_medical_records_patient_id ON medical_records(patient_id);
CREATE INDEX idx_medical_records_doctor_id ON medical_records(doctor_id);

-- Step 9: Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Step 10: Create triggers for updated_at
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_doctors_updated_at BEFORE UPDATE ON doctors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_patients_updated_at BEFORE UPDATE ON patients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_medical_records_updated_at BEFORE UPDATE ON medical_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Verification query to check all tables
SELECT table_name, column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name IN ('profiles', 'doctors', 'patients', 'medical_records')
ORDER BY table_name, ordinal_position;

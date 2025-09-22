-- Enhanced MediChain Database Schema with Firebase Integration
-- Run this SQL in your Supabase dashboard SQL editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS appointments CASCADE;
DROP TABLE IF EXISTS ai_diagnoses CASCADE;
DROP TABLE IF EXISTS prescriptions CASCADE;
DROP TABLE IF EXISTS medical_records CASCADE;
DROP TABLE IF EXISTS doctor_profiles CASCADE;
DROP TABLE IF EXISTS user_profiles CASCADE;

-- Create user_profiles table (extends Firebase auth)
CREATE TABLE user_profiles (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    firebase_uid VARCHAR(255) UNIQUE NOT NULL, -- Firebase UID
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    date_of_birth DATE,
    gender VARCHAR(10) CHECK (gender IN ('male', 'female', 'other')),
    role VARCHAR(20) NOT NULL CHECK (role IN ('patient', 'doctor', 'admin')),
    avatar_url TEXT,
    address JSONB, -- Store address as JSON
    emergency_contact JSONB, -- Store emergency contact as JSON
    medical_conditions TEXT[], -- Array of chronic conditions
    allergies TEXT[], -- Array of allergies
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create doctor_profiles table (additional doctor-specific info)
CREATE TABLE doctor_profiles (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    firebase_uid VARCHAR(255) REFERENCES user_profiles(firebase_uid) ON DELETE CASCADE,
    license_number VARCHAR(100) UNIQUE NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    years_of_experience INTEGER,
    hospital_affiliation VARCHAR(200),
    consultation_fee DECIMAL(10,2),
    available_hours JSONB, -- Store schedule as JSON
    bio TEXT,
    education JSONB, -- Array of education details
    certifications TEXT[], -- Array of certifications
    languages_spoken TEXT[], -- Array of languages
    rating DECIMAL(3,2) DEFAULT 0.00,
    total_reviews INTEGER DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create medical_records table
CREATE TABLE medical_records (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    patient_firebase_uid VARCHAR(255) REFERENCES user_profiles(firebase_uid) ON DELETE CASCADE,
    doctor_firebase_uid VARCHAR(255) REFERENCES user_profiles(firebase_uid) ON DELETE SET NULL,
    record_type VARCHAR(50) NOT NULL CHECK (record_type IN ('diagnosis', 'prescription', 'lab_result', 'imaging', 'consultation')),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    symptoms TEXT[],
    diagnosis TEXT,
    treatment_plan TEXT,
    medications JSONB, -- Array of medication objects
    lab_results JSONB, -- Lab test results
    vital_signs JSONB, -- Blood pressure, heart rate, etc.
    attachments JSONB, -- Array of file URLs
    encrypted_data TEXT, -- Encrypted sensitive data
    blockchain_hash VARCHAR(64), -- Blockchain verification hash
    follow_up_date DATE,
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'resolved', 'follow_up')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create ai_diagnoses table
CREATE TABLE ai_diagnoses (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_firebase_uid VARCHAR(255) REFERENCES user_profiles(firebase_uid) ON DELETE CASCADE,
    session_id VARCHAR(100), -- For tracking conversation sessions
    symptoms_input TEXT NOT NULL,
    patient_age INTEGER,
    patient_gender VARCHAR(10),
    ai_diagnosis JSONB NOT NULL, -- Full AI response
    primary_condition VARCHAR(200),
    confidence_score DECIMAL(5,2),
    differential_diagnoses JSONB, -- Array of alternative diagnoses
    recommended_actions JSONB, -- Array of recommended actions
    severity_level VARCHAR(20),
    prescription_suggestions JSONB, -- AI-suggested prescriptions
    follow_up_recommended BOOLEAN DEFAULT FALSE,
    doctor_review_needed BOOLEAN DEFAULT FALSE,
    ai_model_version VARCHAR(50),
    feedback_rating INTEGER CHECK (feedback_rating BETWEEN 1 AND 5),
    feedback_notes TEXT,
    is_shared_with_doctor BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create prescriptions table
CREATE TABLE prescriptions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    patient_firebase_uid VARCHAR(255) REFERENCES user_profiles(firebase_uid) ON DELETE CASCADE,
    doctor_firebase_uid VARCHAR(255) REFERENCES user_profiles(firebase_uid) ON DELETE SET NULL,
    medical_record_id UUID REFERENCES medical_records(id) ON DELETE SET NULL,
    ai_diagnosis_id UUID REFERENCES ai_diagnoses(id) ON DELETE SET NULL,
    prescription_number VARCHAR(50) UNIQUE,
    medications JSONB NOT NULL, -- Array of medication objects with dosage, frequency, duration
    instructions TEXT,
    duration_days INTEGER,
    refills_allowed INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'cancelled')),
    issued_date DATE DEFAULT CURRENT_DATE,
    expiry_date DATE,
    pharmacy_notes TEXT,
    digital_signature TEXT, -- Doctor's digital signature
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create appointments table
CREATE TABLE appointments (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    patient_firebase_uid VARCHAR(255) REFERENCES user_profiles(firebase_uid) ON DELETE CASCADE,
    doctor_firebase_uid VARCHAR(255) REFERENCES user_profiles(firebase_uid) ON DELETE CASCADE,
    appointment_date TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_minutes INTEGER DEFAULT 30,
    appointment_type VARCHAR(50) DEFAULT 'consultation' CHECK (appointment_type IN ('consultation', 'follow_up', 'emergency', 'checkup')),
    status VARCHAR(20) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'confirmed', 'in_progress', 'completed', 'cancelled', 'no_show')),
    chief_complaint TEXT,
    notes TEXT,
    consultation_fee DECIMAL(10,2),
    payment_status VARCHAR(20) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'refunded')),
    meeting_link TEXT, -- For telemedicine
    reminder_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_user_profiles_firebase_uid ON user_profiles(firebase_uid);
CREATE INDEX idx_user_profiles_email ON user_profiles(email);
CREATE INDEX idx_user_profiles_role ON user_profiles(role);

CREATE INDEX idx_doctor_profiles_firebase_uid ON doctor_profiles(firebase_uid);
CREATE INDEX idx_doctor_profiles_specialization ON doctor_profiles(specialization);

CREATE INDEX idx_medical_records_patient ON medical_records(patient_firebase_uid);
CREATE INDEX idx_medical_records_doctor ON medical_records(doctor_firebase_uid);
CREATE INDEX idx_medical_records_type ON medical_records(record_type);
CREATE INDEX idx_medical_records_created_at ON medical_records(created_at);

CREATE INDEX idx_ai_diagnoses_user ON ai_diagnoses(user_firebase_uid);
CREATE INDEX idx_ai_diagnoses_session ON ai_diagnoses(session_id);
CREATE INDEX idx_ai_diagnoses_created_at ON ai_diagnoses(created_at);

CREATE INDEX idx_prescriptions_patient ON prescriptions(patient_firebase_uid);
CREATE INDEX idx_prescriptions_doctor ON prescriptions(doctor_firebase_uid);
CREATE INDEX idx_prescriptions_status ON prescriptions(status);

CREATE INDEX idx_appointments_patient ON appointments(patient_firebase_uid);
CREATE INDEX idx_appointments_doctor ON appointments(doctor_firebase_uid);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_appointments_status ON appointments(status);

-- Create functions for automatic updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_doctor_profiles_updated_at BEFORE UPDATE ON doctor_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_medical_records_updated_at BEFORE UPDATE ON medical_records FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_diagnoses_updated_at BEFORE UPDATE ON ai_diagnoses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_prescriptions_updated_at BEFORE UPDATE ON prescriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_appointments_updated_at BEFORE UPDATE ON appointments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE doctor_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE medical_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_diagnoses ENABLE ROW LEVEL SECURITY;
ALTER TABLE prescriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;

-- RLS Policies

-- User Profiles: Users can only see and edit their own profile
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (auth.uid()::text = firebase_uid);

CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.uid()::text = firebase_uid);

CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid()::text = firebase_uid);

-- Doctor Profiles: Doctors can manage their own profile, patients can view all doctors
CREATE POLICY "Doctors can manage own profile" ON doctor_profiles
    FOR ALL USING (auth.uid()::text = firebase_uid);

CREATE POLICY "All users can view doctor profiles" ON doctor_profiles
    FOR SELECT TO authenticated USING (true);

-- Medical Records: Patients see their own, doctors see their patients'
CREATE POLICY "Patients can view own medical records" ON medical_records
    FOR SELECT USING (auth.uid()::text = patient_firebase_uid);

CREATE POLICY "Doctors can view their patients' records" ON medical_records
    FOR SELECT USING (auth.uid()::text = doctor_firebase_uid);

CREATE POLICY "Doctors can create medical records" ON medical_records
    FOR INSERT WITH CHECK (auth.uid()::text = doctor_firebase_uid);

CREATE POLICY "Doctors can update medical records" ON medical_records
    FOR UPDATE USING (auth.uid()::text = doctor_firebase_uid);

-- AI Diagnoses: Users can only see their own
CREATE POLICY "Users can view own AI diagnoses" ON ai_diagnoses
    FOR SELECT USING (auth.uid()::text = user_firebase_uid);

CREATE POLICY "Users can create AI diagnoses" ON ai_diagnoses
    FOR INSERT WITH CHECK (auth.uid()::text = user_firebase_uid);

CREATE POLICY "Users can update own AI diagnoses" ON ai_diagnoses
    FOR UPDATE USING (auth.uid()::text = user_firebase_uid);

-- Prescriptions: Patients see their own, doctors see what they prescribed
CREATE POLICY "Patients can view own prescriptions" ON prescriptions
    FOR SELECT USING (auth.uid()::text = patient_firebase_uid);

CREATE POLICY "Doctors can view their prescriptions" ON prescriptions
    FOR SELECT USING (auth.uid()::text = doctor_firebase_uid);

CREATE POLICY "Doctors can create prescriptions" ON prescriptions
    FOR INSERT WITH CHECK (auth.uid()::text = doctor_firebase_uid);

CREATE POLICY "Doctors can update their prescriptions" ON prescriptions
    FOR UPDATE USING (auth.uid()::text = doctor_firebase_uid);

-- Appointments: Both patients and doctors can see their appointments
CREATE POLICY "Patients can view own appointments" ON appointments
    FOR SELECT USING (auth.uid()::text = patient_firebase_uid);

CREATE POLICY "Doctors can view their appointments" ON appointments
    FOR SELECT USING (auth.uid()::text = doctor_firebase_uid);

CREATE POLICY "Patients can create appointments" ON appointments
    FOR INSERT WITH CHECK (auth.uid()::text = patient_firebase_uid);

CREATE POLICY "Users can update their appointments" ON appointments
    FOR UPDATE USING (auth.uid()::text = patient_firebase_uid OR auth.uid()::text = doctor_firebase_uid);

-- Insert sample data for testing

-- Sample Doctor Profile
INSERT INTO user_profiles (firebase_uid, email, first_name, last_name, phone, role, gender, date_of_birth)
VALUES 
    ('doctor_sample_uid', 'dr.smith@medichain.com', 'John', 'Smith', '+1234567890', 'doctor', 'male', '1980-05-15'),
    ('patient_sample_uid', 'patient@medichain.com', 'Jane', 'Doe', '+1987654321', 'patient', 'female', '1990-08-20');

-- Sample Doctor Profile Details
INSERT INTO doctor_profiles (firebase_uid, user_id, license_number, specialization, years_of_experience, hospital_affiliation, consultation_fee, bio)
VALUES (
    'doctor_sample_uid',
    (SELECT id FROM user_profiles WHERE firebase_uid = 'doctor_sample_uid'),
    'MD-12345',
    'General Medicine',
    10,
    'City General Hospital',
    150.00,
    'Experienced general practitioner with focus on preventive care and family medicine.'
);

COMMENT ON TABLE user_profiles IS 'Main user profiles table that extends Firebase authentication';
COMMENT ON TABLE doctor_profiles IS 'Additional information specific to doctor users';
COMMENT ON TABLE medical_records IS 'Patient medical records and history';
COMMENT ON TABLE ai_diagnoses IS 'AI-generated diagnoses and recommendations';
COMMENT ON TABLE prescriptions IS 'Electronic prescriptions';
COMMENT ON TABLE appointments IS 'Appointment scheduling and management';

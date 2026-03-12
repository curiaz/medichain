-- Enhanced Database Schema for Profile Management System
-- AI-Driven Diagnosis and Prescription System with Blockchain-Integrated Health Records

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS credential_updates CASCADE;
DROP TABLE IF EXISTS privacy_settings CASCADE;
DROP TABLE IF EXISTS user_documents CASCADE;
DROP TABLE IF EXISTS blockchain_transactions CASCADE;
DROP TABLE IF EXISTS appointments CASCADE;
DROP TABLE IF EXISTS ai_diagnoses CASCADE;
DROP TABLE IF EXISTS prescriptions CASCADE;
DROP TABLE IF EXISTS medical_records CASCADE;
DROP TABLE IF EXISTS doctor_profiles CASCADE;
DROP TABLE IF EXISTS user_profiles CASCADE;

-- Create enhanced user_profiles table
CREATE TABLE user_profiles (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    firebase_uid VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    -- Human-friendly external patient identifier (stored as HMAC for lookup and AEAD-encrypted for display)
    patient_id_hmac VARCHAR(64) UNIQUE,
    patient_id_enc TEXT,
    date_of_birth DATE,
    gender VARCHAR(10) CHECK (gender IN ('male', 'female', 'other')),
    role VARCHAR(20) NOT NULL CHECK (role IN ('patient', 'doctor', 'admin')),
    avatar_url TEXT,
    
    -- Address information (JSONB for flexibility)
    address JSONB DEFAULT '{}',
    
    -- Emergency contact information
    emergency_contact JSONB DEFAULT '{}',
    
    -- Medical information
    medical_conditions TEXT[] DEFAULT '{}',
    allergies TEXT[] DEFAULT '{}',
    current_medications TEXT[] DEFAULT '{}',
    blood_type VARCHAR(5),
    medical_notes TEXT,
    
    -- Account status
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create doctor_profiles table (additional doctor-specific info)
CREATE TABLE doctor_profiles (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    firebase_uid VARCHAR(255) REFERENCES user_profiles(firebase_uid) ON DELETE CASCADE,
    
    -- Professional information
    license_number VARCHAR(100) UNIQUE NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    years_of_experience INTEGER DEFAULT 0,
    hospital_affiliation VARCHAR(200),
    consultation_fee DECIMAL(10,2) DEFAULT 0.00,
    
    -- Schedule and availability
    available_hours JSONB DEFAULT '{}',
    
    -- Professional details
    bio TEXT,
    education JSONB DEFAULT '[]',
    certifications TEXT[] DEFAULT '{}',
    languages_spoken TEXT[] DEFAULT '{}',
    
    -- Ratings and reviews
    rating DECIMAL(3,2) DEFAULT 0.00,
    total_reviews INTEGER DEFAULT 0,
    
    -- Verification status
    is_verified BOOLEAN DEFAULT FALSE,
    verification_date TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create user_documents table for secure document storage
CREATE TABLE user_documents (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_firebase_uid VARCHAR(255) REFERENCES user_profiles(firebase_uid) ON DELETE CASCADE,
    
    -- File information
    filename VARCHAR(255) NOT NULL,
    unique_filename VARCHAR(255) UNIQUE NOT NULL,
    file_path TEXT NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    file_size BIGINT NOT NULL,
    
    -- Document metadata
    document_type VARCHAR(50) NOT NULL CHECK (document_type IN (
        'medical_certificate', 'id_document', 'prescription', 
        'lab_result', 'insurance_card', 'general'
    )),
    description TEXT,
    
    -- Security and access
    is_encrypted BOOLEAN DEFAULT TRUE,
    access_level VARCHAR(20) DEFAULT 'private' CHECK (access_level IN ('private', 'doctors', 'public')),
    
    -- Timestamps
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Create privacy_settings table for user privacy controls
CREATE TABLE privacy_settings (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_firebase_uid VARCHAR(255) REFERENCES user_profiles(firebase_uid) ON DELETE CASCADE,
    
    -- Profile visibility
    profile_visibility VARCHAR(20) DEFAULT 'private' CHECK (profile_visibility IN ('public', 'private', 'doctors_only')),
    
    -- Medical information sharing
    medical_info_visible_to_doctors BOOLEAN DEFAULT TRUE,
    medical_info_visible_to_hospitals BOOLEAN DEFAULT FALSE,
    medical_info_visible_to_admins BOOLEAN DEFAULT FALSE,
    
    -- AI and research
    allow_ai_analysis BOOLEAN DEFAULT TRUE,
    share_data_for_research BOOLEAN DEFAULT FALSE,
    
    -- Security settings
    emergency_access_enabled BOOLEAN DEFAULT TRUE,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    login_notifications BOOLEAN DEFAULT TRUE,
    
    -- Data control
    data_export_enabled BOOLEAN DEFAULT TRUE,
    data_deletion_enabled BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create blockchain_transactions table for audit trail
CREATE TABLE blockchain_transactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_firebase_uid VARCHAR(255) REFERENCES user_profiles(firebase_uid) ON DELETE CASCADE,
    
    -- Transaction details
    action VARCHAR(100) NOT NULL,
    data_hash VARCHAR(64) NOT NULL,
    blockchain_tx_hash VARCHAR(64) UNIQUE NOT NULL,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    block_number BIGINT,
    gas_used BIGINT
);

-- Create credential_updates table for login credential tracking
CREATE TABLE credential_updates (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_firebase_uid VARCHAR(255) REFERENCES user_profiles(firebase_uid) ON DELETE CASCADE,
    
    -- Update details
    credential_type VARCHAR(50) NOT NULL CHECK (credential_type IN ('email', 'password', '2fa_enable', '2fa_disable')),
    update_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Security information
    ip_address INET,
    user_agent TEXT,
    device_fingerprint VARCHAR(255),
    
    -- Status
    success BOOLEAN DEFAULT TRUE,
    failure_reason TEXT
);

-- Create medical_records table
CREATE TABLE medical_records (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    patient_firebase_uid VARCHAR(255) REFERENCES user_profiles(firebase_uid) ON DELETE CASCADE,
    doctor_firebase_uid VARCHAR(255) REFERENCES user_profiles(firebase_uid) ON DELETE SET NULL,
    
    -- Record information
    record_type VARCHAR(50) NOT NULL CHECK (record_type IN ('diagnosis', 'prescription', 'lab_result', 'imaging', 'consultation')),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    symptoms TEXT[],
    diagnosis TEXT,
    treatment_plan TEXT,
    
    -- Medical data
    medications JSONB DEFAULT '[]',
    lab_results JSONB DEFAULT '{}',
    vital_signs JSONB DEFAULT '{}',
    attachments JSONB DEFAULT '[]',
    
    -- Security and blockchain
    encrypted_data TEXT,
    blockchain_hash VARCHAR(64),
    
    -- Follow-up and priority
    follow_up_date DATE,
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'resolved', 'follow_up')),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create ai_diagnoses table
CREATE TABLE ai_diagnoses (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_firebase_uid VARCHAR(255) REFERENCES user_profiles(firebase_uid) ON DELETE CASCADE,
    
    -- Session information
    session_id VARCHAR(100),
    
    -- Input data
    symptoms_input TEXT NOT NULL,
    patient_age INTEGER,
    patient_gender VARCHAR(10),
    
    -- AI analysis
    ai_diagnosis JSONB NOT NULL,
    primary_condition VARCHAR(200),
    confidence_score DECIMAL(5,2),
    differential_diagnoses JSONB DEFAULT '[]',
    recommended_actions JSONB DEFAULT '[]',
    severity_level VARCHAR(20),
    prescription_suggestions JSONB DEFAULT '[]',
    
    -- Follow-up recommendations
    follow_up_recommended BOOLEAN DEFAULT FALSE,
    doctor_review_needed BOOLEAN DEFAULT FALSE,
    
    -- AI model information
    ai_model_version VARCHAR(50),
    
    -- Feedback
    feedback_rating INTEGER CHECK (feedback_rating BETWEEN 1 AND 5),
    feedback_notes TEXT,
    
    -- Sharing settings
    is_shared_with_doctor BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
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
    
    -- Prescription details
    prescription_number VARCHAR(50) UNIQUE,
    medications JSONB NOT NULL,
    instructions TEXT,
    duration_days INTEGER,
    refills_allowed INTEGER DEFAULT 0,
    
    -- Status and dates
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'cancelled')),
    issued_date DATE DEFAULT CURRENT_DATE,
    expiry_date DATE,
    
    -- Additional information
    pharmacy_notes TEXT,
    digital_signature TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create appointments table
CREATE TABLE appointments (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    patient_firebase_uid VARCHAR(255) REFERENCES user_profiles(firebase_uid) ON DELETE CASCADE,
    doctor_firebase_uid VARCHAR(255) REFERENCES user_profiles(firebase_uid) ON DELETE CASCADE,
    
    -- Appointment details
    appointment_date TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_minutes INTEGER DEFAULT 30,
    appointment_type VARCHAR(50) DEFAULT 'consultation' CHECK (appointment_type IN ('consultation', 'follow_up', 'emergency', 'checkup')),
    
    -- Status and information
    status VARCHAR(20) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'confirmed', 'in_progress', 'completed', 'cancelled', 'no_show')),
    chief_complaint TEXT,
    notes TEXT,
    
    -- Payment and meeting
    consultation_fee DECIMAL(10,2),
    payment_status VARCHAR(20) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'refunded')),
    meeting_link TEXT,
    
    -- Notifications
    reminder_sent BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_user_profiles_firebase_uid ON user_profiles(firebase_uid);
CREATE INDEX idx_user_profiles_email ON user_profiles(email);
CREATE INDEX idx_user_profiles_role ON user_profiles(role);
CREATE INDEX idx_user_profiles_created_at ON user_profiles(created_at);

CREATE INDEX idx_doctor_profiles_firebase_uid ON doctor_profiles(firebase_uid);
CREATE INDEX idx_doctor_profiles_specialization ON doctor_profiles(specialization);
CREATE INDEX idx_doctor_profiles_is_verified ON doctor_profiles(is_verified);

CREATE INDEX idx_user_documents_user ON user_documents(user_firebase_uid);
CREATE INDEX idx_user_documents_type ON user_documents(document_type);
CREATE INDEX idx_user_documents_upload_date ON user_documents(upload_date);
CREATE INDEX idx_user_documents_hash ON user_documents(file_hash);

CREATE INDEX idx_privacy_settings_user ON privacy_settings(user_firebase_uid);

CREATE INDEX idx_blockchain_transactions_user ON blockchain_transactions(user_firebase_uid);
CREATE INDEX idx_blockchain_transactions_action ON blockchain_transactions(action);
CREATE INDEX idx_blockchain_transactions_timestamp ON blockchain_transactions(timestamp);
CREATE INDEX idx_blockchain_transactions_hash ON blockchain_transactions(blockchain_tx_hash);

CREATE INDEX idx_credential_updates_user ON credential_updates(user_firebase_uid);
CREATE INDEX idx_credential_updates_timestamp ON credential_updates(update_timestamp);

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
CREATE TRIGGER update_privacy_settings_updated_at BEFORE UPDATE ON privacy_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_medical_records_updated_at BEFORE UPDATE ON medical_records FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_diagnoses_updated_at BEFORE UPDATE ON ai_diagnoses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_prescriptions_updated_at BEFORE UPDATE ON prescriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_appointments_updated_at BEFORE UPDATE ON appointments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE doctor_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE privacy_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE blockchain_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE credential_updates ENABLE ROW LEVEL SECURITY;
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

-- User Documents: Users can only access their own documents
CREATE POLICY "Users can manage own documents" ON user_documents
    FOR ALL USING (auth.uid()::text = user_firebase_uid);

-- Privacy Settings: Users can only manage their own settings
CREATE POLICY "Users can manage own privacy settings" ON privacy_settings
    FOR ALL USING (auth.uid()::text = user_firebase_uid);

-- Blockchain Transactions: Users can only view their own transactions
CREATE POLICY "Users can view own blockchain transactions" ON blockchain_transactions
    FOR SELECT USING (auth.uid()::text = user_firebase_uid);

-- Credential Updates: Users can only view their own credential updates
CREATE POLICY "Users can view own credential updates" ON credential_updates
    FOR SELECT USING (auth.uid()::text = user_firebase_uid);

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
INSERT INTO user_profiles (firebase_uid, email, first_name, last_name, phone, role, gender, date_of_birth, medical_conditions, allergies)
VALUES 
    ('doctor_sample_uid', 'dr.smith@medichain.com', 'John', 'Smith', '+1234567890', 'doctor', 'male', '1980-05-15', '{}', '{}'),
    ('patient_sample_uid', 'patient@medichain.com', 'Jane', 'Doe', '+1987654321', 'patient', 'female', '1990-08-20', '{"Diabetes Type 2"}', '{"Penicillin"}');

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

-- Sample Privacy Settings
INSERT INTO privacy_settings (user_firebase_uid, profile_visibility, medical_info_visible_to_doctors, allow_ai_analysis)
VALUES 
    ('doctor_sample_uid', 'doctors_only', true, true),
    ('patient_sample_uid', 'private', true, true);

COMMENT ON TABLE user_profiles IS 'Main user profiles table with enhanced medical information';
COMMENT ON TABLE doctor_profiles IS 'Additional information specific to doctor users';
COMMENT ON TABLE user_documents IS 'Secure document storage with blockchain integration';
COMMENT ON TABLE privacy_settings IS 'User privacy and security controls';
COMMENT ON TABLE blockchain_transactions IS 'Audit trail for all profile changes';
COMMENT ON TABLE credential_updates IS 'Login credential change tracking';
COMMENT ON TABLE medical_records IS 'Patient medical records and history';
COMMENT ON TABLE ai_diagnoses IS 'AI-generated diagnoses and recommendations';
COMMENT ON TABLE prescriptions IS 'Electronic prescriptions';
COMMENT ON TABLE appointments IS 'Appointment scheduling and management';


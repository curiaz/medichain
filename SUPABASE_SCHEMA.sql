-- =====================================================
-- SUPABASE DATABASE SCHEMA FOR MEDICHAIN HEALTHCARE
-- Complete database schema with Row Level Security (RLS)
-- =====================================================

-- 1. PATIENTS TABLE
CREATE TABLE patients (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    firebase_uid VARCHAR(128) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    phone VARCHAR(20),
    address TEXT,
    emergency_contact JSONB, -- {"name": "Contact Name", "phone": "123-456-7890", "relationship": "spouse"}
    role VARCHAR(20) DEFAULT 'patient' CHECK (role IN ('patient', 'doctor', 'admin')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. DOCTORS TABLE
CREATE TABLE doctors (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    firebase_uid VARCHAR(128) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    license_number VARCHAR(100) UNIQUE NOT NULL,
    specialization VARCHAR(100),
    phone VARCHAR(20),
    verified BOOLEAN DEFAULT FALSE,
    verification_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. MEDICAL RECORDS TABLE
CREATE TABLE medical_records (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    doctor_id VARCHAR(128) NOT NULL, -- Firebase UID of doctor
    diagnosis TEXT NOT NULL,
    treatment TEXT,
    medications JSONB, -- [{"name": "Medicine", "dosage": "10mg", "frequency": "2x daily"}]
    notes TEXT,
    visit_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. APPOINTMENTS TABLE
CREATE TABLE appointments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    doctor_id VARCHAR(128) NOT NULL,
    appointment_date TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(20) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'confirmed', 'cancelled', 'completed')),
    reason TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. AI DIAGNOSIS HISTORY TABLE
CREATE TABLE ai_diagnosis_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    symptoms JSONB NOT NULL, -- {"symptoms": ["headache", "fever"], "severity": 7}
    ai_diagnosis TEXT NOT NULL,
    confidence_score DECIMAL(3,2), -- 0.00 to 1.00
    recommendations TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. CONTACT MESSAGES TABLE (for healthcare inquiries)
CREATE TABLE contact_messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    subject VARCHAR(255),
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'new' CHECK (status IN ('new', 'reviewed', 'responded', 'closed')),
    priority VARCHAR(10) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Patients indexes
CREATE INDEX idx_patients_firebase_uid ON patients(firebase_uid);
CREATE INDEX idx_patients_email ON patients(email);
CREATE INDEX idx_patients_role ON patients(role);

-- Doctors indexes
CREATE INDEX idx_doctors_firebase_uid ON doctors(firebase_uid);
CREATE INDEX idx_doctors_license ON doctors(license_number);
CREATE INDEX idx_doctors_verified ON doctors(verified);

-- Medical records indexes
CREATE INDEX idx_medical_records_patient ON medical_records(patient_id);
CREATE INDEX idx_medical_records_doctor ON medical_records(doctor_id);
CREATE INDEX idx_medical_records_date ON medical_records(visit_date);

-- Appointments indexes
CREATE INDEX idx_appointments_patient ON appointments(patient_id);
CREATE INDEX idx_appointments_doctor ON appointments(doctor_id);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_appointments_status ON appointments(status);

-- AI diagnosis indexes
CREATE INDEX idx_ai_diagnosis_patient ON ai_diagnosis_history(patient_id);
CREATE INDEX idx_ai_diagnosis_date ON ai_diagnosis_history(created_at);

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE doctors ENABLE ROW LEVEL SECURITY;
ALTER TABLE medical_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_diagnosis_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE contact_messages ENABLE ROW LEVEL SECURITY;

-- PATIENTS RLS POLICIES
-- Patients can only see their own records
CREATE POLICY "Patients can view own data" ON patients
    FOR SELECT USING (firebase_uid = auth.jwt() ->> 'sub');

-- Patients can update their own profile (except role)
CREATE POLICY "Patients can update own profile" ON patients
    FOR UPDATE USING (firebase_uid = auth.jwt() ->> 'sub')
    WITH CHECK (firebase_uid = auth.jwt() ->> 'sub');

-- Doctors can view patient records they're treating
CREATE POLICY "Doctors can view patients" ON patients
    FOR SELECT USING (
        auth.jwt() ->> 'role' = 'doctor' OR 
        auth.jwt() ->> 'role' = 'admin'
    );

-- DOCTORS RLS POLICIES
-- Doctors can view their own profile
CREATE POLICY "Doctors can view own profile" ON doctors
    FOR SELECT USING (firebase_uid = auth.jwt() ->> 'sub');

-- Doctors can update their own profile
CREATE POLICY "Doctors can update own profile" ON doctors
    FOR UPDATE USING (firebase_uid = auth.jwt() ->> 'sub')
    WITH CHECK (firebase_uid = auth.jwt() ->> 'sub');

-- MEDICAL RECORDS RLS POLICIES
-- Patients can view their own medical records
CREATE POLICY "Patients can view own medical records" ON medical_records
    FOR SELECT USING (
        patient_id IN (
            SELECT id FROM patients WHERE firebase_uid = auth.jwt() ->> 'sub'
        )
    );

-- Doctors can view and create medical records for their patients
CREATE POLICY "Doctors can manage medical records" ON medical_records
    FOR ALL USING (
        auth.jwt() ->> 'role' = 'doctor' OR 
        auth.jwt() ->> 'role' = 'admin'
    );

-- APPOINTMENTS RLS POLICIES
-- Patients can view their own appointments
CREATE POLICY "Patients can view own appointments" ON appointments
    FOR SELECT USING (
        patient_id IN (
            SELECT id FROM patients WHERE firebase_uid = auth.jwt() ->> 'sub'
        )
    );

-- Doctors can view appointments they're involved in
CREATE POLICY "Doctors can view their appointments" ON appointments
    FOR SELECT USING (
        doctor_id = auth.jwt() ->> 'sub' OR 
        auth.jwt() ->> 'role' = 'admin'
    );

-- Patients can create appointments
CREATE POLICY "Patients can create appointments" ON appointments
    FOR INSERT WITH CHECK (
        patient_id IN (
            SELECT id FROM patients WHERE firebase_uid = auth.jwt() ->> 'sub'
        )
    );

-- AI DIAGNOSIS HISTORY RLS POLICIES
-- Patients can view their own AI diagnosis history
CREATE POLICY "Patients can view own AI diagnosis" ON ai_diagnosis_history
    FOR SELECT USING (
        patient_id IN (
            SELECT id FROM patients WHERE firebase_uid = auth.jwt() ->> 'sub'
        )
    );

-- System can create AI diagnosis records
CREATE POLICY "System can create AI diagnosis" ON ai_diagnosis_history
    FOR INSERT WITH CHECK (true);

-- CONTACT MESSAGES RLS POLICIES
-- Anyone can create contact messages
CREATE POLICY "Anyone can create contact messages" ON contact_messages
    FOR INSERT WITH CHECK (true);

-- Only admins can view contact messages
CREATE POLICY "Admins can view contact messages" ON contact_messages
    FOR SELECT USING (auth.jwt() ->> 'role' = 'admin');

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_patients_updated_at BEFORE UPDATE ON patients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_doctors_updated_at BEFORE UPDATE ON doctors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_medical_records_updated_at BEFORE UPDATE ON medical_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_appointments_updated_at BEFORE UPDATE ON appointments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contact_messages_updated_at BEFORE UPDATE ON contact_messages
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- SAMPLE DATA FOR TESTING
-- =====================================================

-- Insert sample patient (use actual Firebase UID in production)
INSERT INTO patients (firebase_uid, email, full_name, date_of_birth, phone, role) VALUES
('sample_firebase_uid_1', 'patient@medichain.com', 'John Doe', '1990-01-15', '+1-555-0123', 'patient');

-- Insert sample doctor
INSERT INTO doctors (firebase_uid, email, full_name, license_number, specialization, verified) VALUES
('sample_firebase_uid_2', 'doctor@medichain.com', 'Dr. Jane Smith', 'MD123456', 'General Medicine', true);

-- Sample medical record
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment, medications, notes) VALUES
(
    (SELECT id FROM patients WHERE email = 'patient@medichain.com'),
    'sample_firebase_uid_2',
    'Common cold with mild symptoms',
    'Rest and hydration',
    '[{"name": "Acetaminophen", "dosage": "500mg", "frequency": "Every 6 hours as needed"}]',
    'Patient reported symptoms: runny nose, mild headache. Advised to return if symptoms worsen.'
);

-- Sample appointment
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason, status) VALUES
(
    (SELECT id FROM patients WHERE email = 'patient@medichain.com'),
    'sample_firebase_uid_2',
    NOW() + INTERVAL '7 days',
    'Follow-up visit for cold symptoms',
    'scheduled'
);

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Check if all tables were created
SELECT table_name, table_type 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('patients', 'doctors', 'medical_records', 'appointments', 'ai_diagnosis_history', 'contact_messages');

-- Check RLS policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
FROM pg_policies 
WHERE schemaname = 'public';

-- Check indexes
SELECT indexname, tablename, indexdef 
FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY tablename, indexname;

-- Sample query to verify data relationships
SELECT 
    p.full_name as patient_name,
    d.full_name as doctor_name,
    mr.diagnosis,
    mr.visit_date,
    a.appointment_date,
    a.status as appointment_status
FROM patients p
LEFT JOIN medical_records mr ON p.id = mr.patient_id
LEFT JOIN doctors d ON mr.doctor_id = d.firebase_uid
LEFT JOIN appointments a ON p.id = a.patient_id AND a.doctor_id = d.firebase_uid
WHERE p.email = 'patient@medichain.com';

COMMIT;
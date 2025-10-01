-- =====================================================
-- SAFE SUPABASE DATABASE SCHEMA FOR MEDICHAIN HEALTHCARE
-- Handles existing tables and creates missing ones only
-- =====================================================

-- Check and create tables only if they don't exist
-- This prevents conflicts with existing tables

-- 1. PATIENTS TABLE (CREATE IF NOT EXISTS)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'patients') THEN
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
        RAISE NOTICE 'Created patients table';
    ELSE
        RAISE NOTICE 'patients table already exists';
    END IF;
END $$;

-- 2. DOCTORS TABLE (CREATE IF NOT EXISTS)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'doctors') THEN
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
        RAISE NOTICE 'Created doctors table';
    ELSE
        RAISE NOTICE 'doctors table already exists';
    END IF;
END $$;

-- 3. MEDICAL RECORDS TABLE (ALTER IF EXISTS OR CREATE)
DO $$ 
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'medical_records') THEN
        -- Add missing columns if they don't exist
        BEGIN
            ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS medications JSONB;
            ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS notes TEXT;
            ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS visit_date DATE DEFAULT CURRENT_DATE;
            ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
            ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
            RAISE NOTICE 'Updated medical_records table with missing columns';
        EXCEPTION
            WHEN OTHERS THEN
                RAISE NOTICE 'Some columns may already exist in medical_records table';
        END;
    ELSE
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
        RAISE NOTICE 'Created medical_records table';
    END IF;
END $$;

-- 4. APPOINTMENTS TABLE (CREATE IF NOT EXISTS)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'appointments') THEN
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
        RAISE NOTICE 'Created appointments table';
    ELSE
        RAISE NOTICE 'appointments table already exists';
    END IF;
END $$;

-- 5. AI DIAGNOSIS HISTORY TABLE (CREATE IF NOT EXISTS)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'ai_diagnosis_history') THEN
        CREATE TABLE ai_diagnosis_history (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
            symptoms JSONB NOT NULL, -- {"symptoms": ["headache", "fever"], "severity": 7}
            ai_diagnosis TEXT NOT NULL,
            confidence_score DECIMAL(3,2), -- 0.00 to 1.00
            recommendations TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        RAISE NOTICE 'Created ai_diagnosis_history table';
    ELSE
        RAISE NOTICE 'ai_diagnosis_history table already exists';
    END IF;
END $$;

-- 6. CONTACT MESSAGES TABLE (CREATE IF NOT EXISTS)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'contact_messages') THEN
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
        RAISE NOTICE 'Created contact_messages table';
    ELSE
        RAISE NOTICE 'contact_messages table already exists';
    END IF;
END $$;

-- =====================================================
-- SAFE INDEX CREATION (CREATE IF NOT EXISTS)
-- =====================================================

-- Patients indexes
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_patients_firebase_uid') THEN
        CREATE INDEX idx_patients_firebase_uid ON patients(firebase_uid);
        RAISE NOTICE 'Created idx_patients_firebase_uid';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_patients_email') THEN
        CREATE INDEX idx_patients_email ON patients(email);
        RAISE NOTICE 'Created idx_patients_email';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_patients_role') THEN
        CREATE INDEX idx_patients_role ON patients(role);
        RAISE NOTICE 'Created idx_patients_role';
    END IF;
END $$;

-- Doctors indexes
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_doctors_firebase_uid') THEN
        CREATE INDEX idx_doctors_firebase_uid ON doctors(firebase_uid);
        RAISE NOTICE 'Created idx_doctors_firebase_uid';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_doctors_license') THEN
        CREATE INDEX idx_doctors_license ON doctors(license_number);
        RAISE NOTICE 'Created idx_doctors_license';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_doctors_verified') THEN
        CREATE INDEX idx_doctors_verified ON doctors(verified);
        RAISE NOTICE 'Created idx_doctors_verified';
    END IF;
END $$;

-- Medical records indexes
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_medical_records_patient') THEN
        CREATE INDEX idx_medical_records_patient ON medical_records(patient_id);
        RAISE NOTICE 'Created idx_medical_records_patient';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_medical_records_doctor') THEN
        CREATE INDEX idx_medical_records_doctor ON medical_records(doctor_id);
        RAISE NOTICE 'Created idx_medical_records_doctor';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_medical_records_date') THEN
        CREATE INDEX idx_medical_records_date ON medical_records(visit_date);
        RAISE NOTICE 'Created idx_medical_records_date';
    END IF;
END $$;

-- Appointments indexes
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_appointments_patient') THEN
        CREATE INDEX idx_appointments_patient ON appointments(patient_id);
        RAISE NOTICE 'Created idx_appointments_patient';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_appointments_doctor') THEN
        CREATE INDEX idx_appointments_doctor ON appointments(doctor_id);
        RAISE NOTICE 'Created idx_appointments_doctor';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_appointments_date') THEN
        CREATE INDEX idx_appointments_date ON appointments(appointment_date);
        RAISE NOTICE 'Created idx_appointments_date';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_appointments_status') THEN
        CREATE INDEX idx_appointments_status ON appointments(status);
        RAISE NOTICE 'Created idx_appointments_status';
    END IF;
END $$;

-- AI diagnosis indexes
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_ai_diagnosis_patient') THEN
        CREATE INDEX idx_ai_diagnosis_patient ON ai_diagnosis_history(patient_id);
        RAISE NOTICE 'Created idx_ai_diagnosis_patient';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_ai_diagnosis_date') THEN
        CREATE INDEX idx_ai_diagnosis_date ON ai_diagnosis_history(created_at);
        RAISE NOTICE 'Created idx_ai_diagnosis_date';
    END IF;
END $$;

-- =====================================================
-- ROW LEVEL SECURITY (RLS) SETUP
-- =====================================================

-- Enable RLS on all tables (safe operation)
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE doctors ENABLE ROW LEVEL SECURITY;
ALTER TABLE medical_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_diagnosis_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE contact_messages ENABLE ROW LEVEL SECURITY;

-- Drop existing policies first (to avoid conflicts)
DROP POLICY IF EXISTS "Patients can view own data" ON patients;
DROP POLICY IF EXISTS "Patients can update own profile" ON patients;
DROP POLICY IF EXISTS "Doctors can view patients" ON patients;
DROP POLICY IF EXISTS "Doctors can view own profile" ON doctors;
DROP POLICY IF EXISTS "Doctors can update own profile" ON doctors;
DROP POLICY IF EXISTS "Patients can view own medical records" ON medical_records;
DROP POLICY IF EXISTS "Doctors can manage medical records" ON medical_records;
DROP POLICY IF EXISTS "Patients can view own appointments" ON appointments;
DROP POLICY IF EXISTS "Doctors can view their appointments" ON appointments;
DROP POLICY IF EXISTS "Patients can create appointments" ON appointments;
DROP POLICY IF EXISTS "Patients can view own AI diagnosis" ON ai_diagnosis_history;
DROP POLICY IF EXISTS "System can create AI diagnosis" ON ai_diagnosis_history;
DROP POLICY IF EXISTS "Anyone can create contact messages" ON contact_messages;
DROP POLICY IF EXISTS "Admins can view contact messages" ON contact_messages;

-- PATIENTS RLS POLICIES
CREATE POLICY "Patients can view own data" ON patients
    FOR SELECT USING (firebase_uid = auth.jwt() ->> 'sub');

CREATE POLICY "Patients can update own profile" ON patients
    FOR UPDATE USING (firebase_uid = auth.jwt() ->> 'sub')
    WITH CHECK (firebase_uid = auth.jwt() ->> 'sub');

CREATE POLICY "Doctors can view patients" ON patients
    FOR SELECT USING (
        auth.jwt() ->> 'role' = 'doctor' OR 
        auth.jwt() ->> 'role' = 'admin'
    );

-- DOCTORS RLS POLICIES
CREATE POLICY "Doctors can view own profile" ON doctors
    FOR SELECT USING (firebase_uid = auth.jwt() ->> 'sub');

CREATE POLICY "Doctors can update own profile" ON doctors
    FOR UPDATE USING (firebase_uid = auth.jwt() ->> 'sub')
    WITH CHECK (firebase_uid = auth.jwt() ->> 'sub');

-- MEDICAL RECORDS RLS POLICIES
CREATE POLICY "Patients can view own medical records" ON medical_records
    FOR SELECT USING (
        patient_id IN (
            SELECT id FROM patients WHERE firebase_uid = auth.jwt() ->> 'sub'
        )
    );

CREATE POLICY "Doctors can manage medical records" ON medical_records
    FOR ALL USING (
        auth.jwt() ->> 'role' = 'doctor' OR 
        auth.jwt() ->> 'role' = 'admin'
    );

-- APPOINTMENTS RLS POLICIES
CREATE POLICY "Patients can view own appointments" ON appointments
    FOR SELECT USING (
        patient_id IN (
            SELECT id FROM patients WHERE firebase_uid = auth.jwt() ->> 'sub'
        )
    );

CREATE POLICY "Doctors can view their appointments" ON appointments
    FOR SELECT USING (
        doctor_id = auth.jwt() ->> 'sub' OR 
        auth.jwt() ->> 'role' = 'admin'
    );

CREATE POLICY "Patients can create appointments" ON appointments
    FOR INSERT WITH CHECK (
        patient_id IN (
            SELECT id FROM patients WHERE firebase_uid = auth.jwt() ->> 'sub'
        )
    );

-- AI DIAGNOSIS HISTORY RLS POLICIES
CREATE POLICY "Patients can view own AI diagnosis" ON ai_diagnosis_history
    FOR SELECT USING (
        patient_id IN (
            SELECT id FROM patients WHERE firebase_uid = auth.jwt() ->> 'sub'
        )
    );

CREATE POLICY "System can create AI diagnosis" ON ai_diagnosis_history
    FOR INSERT WITH CHECK (true);

-- CONTACT MESSAGES RLS POLICIES
CREATE POLICY "Anyone can create contact messages" ON contact_messages
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Admins can view contact messages" ON contact_messages
    FOR SELECT USING (auth.jwt() ->> 'role' = 'admin');

-- =====================================================
-- FUNCTIONS AND TRIGGERS (SAFE CREATION)
-- =====================================================

-- Function to update updated_at timestamp (replace if exists)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop existing triggers first, then recreate
DROP TRIGGER IF EXISTS update_patients_updated_at ON patients;
DROP TRIGGER IF EXISTS update_doctors_updated_at ON doctors;
DROP TRIGGER IF EXISTS update_medical_records_updated_at ON medical_records;
DROP TRIGGER IF EXISTS update_appointments_updated_at ON appointments;
DROP TRIGGER IF EXISTS update_contact_messages_updated_at ON contact_messages;

-- Create triggers
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
-- SAMPLE DATA (INSERT ONLY IF NOT EXISTS)
-- =====================================================

-- Insert sample patient only if doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM patients WHERE email = 'patient@medichain.com') THEN
        INSERT INTO patients (firebase_uid, email, full_name, date_of_birth, phone, role) VALUES
        ('sample_firebase_uid_1', 'patient@medichain.com', 'John Doe', '1990-01-15', '+1-555-0123', 'patient');
        RAISE NOTICE 'Inserted sample patient';
    ELSE
        RAISE NOTICE 'Sample patient already exists';
    END IF;
END $$;

-- Insert sample doctor only if doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM doctors WHERE email = 'doctor@medichain.com') THEN
        INSERT INTO doctors (firebase_uid, email, full_name, license_number, specialization, verified) VALUES
        ('sample_firebase_uid_2', 'doctor@medichain.com', 'Dr. Jane Smith', 'MD123456', 'General Medicine', true);
        RAISE NOTICE 'Inserted sample doctor';
    ELSE
        RAISE NOTICE 'Sample doctor already exists';
    END IF;
END $$;

-- Insert sample medical record only if doesn't exist
DO $$
DECLARE
    patient_uuid UUID;
BEGIN
    SELECT id INTO patient_uuid FROM patients WHERE email = 'patient@medichain.com';
    
    IF patient_uuid IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM medical_records 
        WHERE patient_id = patient_uuid AND doctor_id = 'sample_firebase_uid_2'
    ) THEN
        INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment, medications, notes) VALUES
        (
            patient_uuid,
            'sample_firebase_uid_2',
            'Common cold with mild symptoms',
            'Rest and hydration',
            '[{"name": "Acetaminophen", "dosage": "500mg", "frequency": "Every 6 hours as needed"}]',
            'Patient reported symptoms: runny nose, mild headache. Advised to return if symptoms worsen.'
        );
        RAISE NOTICE 'Inserted sample medical record';
    ELSE
        RAISE NOTICE 'Sample medical record already exists or patient not found';
    END IF;
END $$;

-- Insert sample appointment only if doesn't exist
DO $$
DECLARE
    patient_uuid UUID;
BEGIN
    SELECT id INTO patient_uuid FROM patients WHERE email = 'patient@medichain.com';
    
    IF patient_uuid IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM appointments 
        WHERE patient_id = patient_uuid AND doctor_id = 'sample_firebase_uid_2'
    ) THEN
        INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason, status) VALUES
        (
            patient_uuid,
            'sample_firebase_uid_2',
            NOW() + INTERVAL '7 days',
            'Follow-up visit for cold symptoms',
            'scheduled'
        );
        RAISE NOTICE 'Inserted sample appointment';
    ELSE
        RAISE NOTICE 'Sample appointment already exists or patient not found';
    END IF;
END $$;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Check if all tables were created
SELECT 
    table_name, 
    table_type,
    CASE 
        WHEN table_name IN ('patients', 'doctors', 'medical_records', 'appointments', 'ai_diagnosis_history', 'contact_messages') 
        THEN '✅ Required' 
        ELSE '📋 Additional' 
    END as status
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Check RLS policies count
SELECT 
    tablename,
    COUNT(*) as policy_count
FROM pg_policies 
WHERE schemaname = 'public'
GROUP BY tablename
ORDER BY tablename;

-- Check indexes count
SELECT 
    tablename,
    COUNT(*) as index_count
FROM pg_indexes 
WHERE schemaname = 'public'
GROUP BY tablename
ORDER BY tablename;

-- Sample data verification
SELECT 
    'patients' as table_name,
    COUNT(*) as record_count
FROM patients
UNION ALL
SELECT 
    'doctors' as table_name,
    COUNT(*) as record_count
FROM doctors
UNION ALL
SELECT 
    'medical_records' as table_name,
    COUNT(*) as record_count
FROM medical_records
UNION ALL
SELECT 
    'appointments' as table_name,
    COUNT(*) as record_count
FROM appointments;

-- Final success message
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '🎉 MEDICHAIN DATABASE SCHEMA SETUP COMPLETE! 🎉';
    RAISE NOTICE '';
    RAISE NOTICE '✅ All tables created or verified';
    RAISE NOTICE '✅ Indexes created for performance';
    RAISE NOTICE '✅ Row Level Security (RLS) policies active';
    RAISE NOTICE '✅ Triggers for timestamp updates active';
    RAISE NOTICE '✅ Sample data inserted for testing';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 Your MediChain healthcare system database is ready!';
END $$;

COMMIT;
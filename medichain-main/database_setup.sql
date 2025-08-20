-- Complete Database Setup for MediChain Authentication
-- Run these queries in your Supabase SQL editor

-- 1. Create users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('doctor', 'patient', 'admin')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Create health_records table for medical records
CREATE TABLE IF NOT EXISTS health_records (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    patient_id UUID NOT NULL,
    doctor_id UUID,
    diagnosis TEXT NOT NULL,
    prescription TEXT NOT NULL,
    blockchain_tx_hash VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 3. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_health_records_patient_id ON health_records(patient_id);
CREATE INDEX IF NOT EXISTS idx_health_records_doctor_id ON health_records(doctor_id);

-- 4. Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE health_records ENABLE ROW LEVEL SECURITY;

-- 5. Create RLS policies for users
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

-- 6. Create RLS policies for health records
CREATE POLICY "Users can view own records" ON health_records
    FOR SELECT USING (patient_id = auth.uid() OR doctor_id = auth.uid());

CREATE POLICY "Doctors can create records" ON health_records
    FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'doctor');

CREATE POLICY "Doctors can update own records" ON health_records
    FOR UPDATE USING (doctor_id = auth.uid());

-- 7. Insert sample data for testing
INSERT INTO users (email, password_hash, full_name, role) VALUES
('doctor@medichain.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/J9eH7O3m.', 'Dr. John Smith', 'doctor'),
('patient@medichain.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/J9eH7O3m.', 'Jane Doe', 'patient')
ON CONFLICT (email) DO NOTHING;

-- 8. Create a simple test record
INSERT INTO health_records (patient_id, doctor_id, diagnosis, prescription, blockchain_tx_hash) 
SELECT 
    (SELECT id FROM users WHERE email = 'patient@medichain.com'),
    (SELECT id FROM users WHERE email = 'doctor@medichain.com'),
    'Test Diagnosis',
    'Test Prescription: Take 2 tablets daily',
    '0x1234567890abcdef'
WHERE NOT EXISTS (SELECT 1 FROM health_records WHERE diagnosis = 'Test Diagnosis');

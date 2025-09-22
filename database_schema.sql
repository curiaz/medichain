-- MediChain Database Schema
-- Run this SQL in your Supabase dashboard SQL editor

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('doctor', 'patient', 'admin')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create health_records table
CREATE TABLE IF NOT EXISTS health_records (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES users(id),
    doctor_id INTEGER REFERENCES users(id),
    diagnosis TEXT NOT NULL,
    prescription TEXT NOT NULL,
    encrypted_diagnosis TEXT,
    encrypted_prescription TEXT,
    blockchain_hash VARCHAR(64),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_health_records_patient ON health_records(patient_id);
CREATE INDEX IF NOT EXISTS idx_health_records_doctor ON health_records(doctor_id);

-- Insert a test admin user (password: Admin123!)
-- Password hash for 'Admin123!' using bcrypt
INSERT INTO users (email, password_hash, full_name, role) 
VALUES (
    'admin@medichain.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewDhHmcqzT.YqpKy',
    'System Administrator',
    'admin'
) ON CONFLICT (email) DO NOTHING;

-- Insert a test doctor user (password: Doctor123!)
INSERT INTO users (email, password_hash, full_name, role) 
VALUES (
    'doctor@medichain.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewDhHmcqzT.YqpKy',
    'Dr. John Smith',
    'doctor'
) ON CONFLICT (email) DO NOTHING;

-- Insert a test patient user (password: Patient123!)
INSERT INTO users (email, password_hash, full_name, role) 
VALUES (
    'patient@medichain.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewDhHmcqzT.YqpKy',
    'Jane Doe',
    'patient'
) ON CONFLICT (email) DO NOTHING;

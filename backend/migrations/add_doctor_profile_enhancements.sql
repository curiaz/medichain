-- Migration: Add doctor profile enhancements
-- Date: 2024
-- Description: Adds privacy settings, address fields, and activity tracking

-- Add address fields to user_profiles if not exists
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS address VARCHAR(255),
ADD COLUMN IF NOT EXISTS city VARCHAR(100),
ADD COLUMN IF NOT EXISTS state VARCHAR(100),
ADD COLUMN IF NOT EXISTS zip_code VARCHAR(20);

-- Add privacy settings to doctor_profiles
ALTER TABLE doctor_profiles
ADD COLUMN IF NOT EXISTS profile_visibility VARCHAR(50) DEFAULT 'public',
ADD COLUMN IF NOT EXISTS show_email BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS show_phone BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS allow_patient_messages BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS data_sharing BOOLEAN DEFAULT false;

-- Create activity_logs table
CREATE TABLE IF NOT EXISTS activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firebase_uid VARCHAR(255) NOT NULL,
    action VARCHAR(255) NOT NULL,
    details TEXT,
    timestamp TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index on firebase_uid for faster queries
CREATE INDEX IF NOT EXISTS idx_activity_logs_firebase_uid ON activity_logs(firebase_uid);
CREATE INDEX IF NOT EXISTS idx_activity_logs_timestamp ON activity_logs(timestamp DESC);

-- Create doctor_documents table for document uploads
CREATE TABLE IF NOT EXISTS doctor_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firebase_uid VARCHAR(255) NOT NULL,
    document_type VARCHAR(50) NOT NULL, -- 'license', 'certificate', 'verification'
    filename VARCHAR(500) NOT NULL,
    file_size INTEGER,
    file_type VARCHAR(100),
    uploaded_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for doctor_documents
CREATE INDEX IF NOT EXISTS idx_doctor_documents_firebase_uid ON doctor_documents(firebase_uid);
CREATE INDEX IF NOT EXISTS idx_doctor_documents_status ON doctor_documents(status);

-- Enable RLS on new tables
ALTER TABLE activity_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE doctor_documents ENABLE ROW LEVEL SECURITY;

-- RLS Policies for activity_logs
CREATE POLICY "Users can view their own activity logs"
ON activity_logs FOR SELECT
USING (firebase_uid = current_setting('request.jwt.claims', true)::json->>'sub');

-- RLS Policies for doctor_documents
CREATE POLICY "Doctors can view their own documents"
ON doctor_documents FOR SELECT
USING (firebase_uid = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Doctors can insert their own documents"
ON doctor_documents FOR INSERT
WITH CHECK (firebase_uid = current_setting('request.jwt.claims', true)::json->>'sub');

-- Add comment for documentation
COMMENT ON TABLE activity_logs IS 'Stores user activity history for audit trail';
COMMENT ON TABLE doctor_documents IS 'Stores doctor verification documents and certificates';

-- Refresh updated_at trigger for doctor_documents
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_doctor_documents_updated_at BEFORE UPDATE ON doctor_documents
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

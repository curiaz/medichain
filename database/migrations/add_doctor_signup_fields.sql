-- Migration: Add comprehensive doctor signup fields to doctor_profiles table
-- Date: 2025-01-XX
-- Description: Adds all fields required for the multi-step doctor signup process

-- Ensure doctor_profiles table exists with id column
-- If the table doesn't exist, this will fail - you need to create it first
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'doctor_profiles'
    ) THEN
        RAISE EXCEPTION 'doctor_profiles table does not exist. Please create it first.';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'doctor_profiles' 
        AND column_name = 'id'
    ) THEN
        RAISE EXCEPTION 'doctor_profiles table does not have an id column. Please check your table structure.';
    END IF;
END $$;

-- Add new columns to doctor_profiles table
ALTER TABLE doctor_profiles 
ADD COLUMN IF NOT EXISTS prc_license_number VARCHAR(100),
ADD COLUMN IF NOT EXISTS prc_expiration_date DATE,
ADD COLUMN IF NOT EXISTS affiliation_type VARCHAR(50) CHECK (affiliation_type IN ('clinic_hospital', 'independent_private', 'not_affiliated')),
ADD COLUMN IF NOT EXISTS clinic_hospital_affiliation VARCHAR(255),
ADD COLUMN IF NOT EXISTS professional_address TEXT,
ADD COLUMN IF NOT EXISTS hospital_clinic_contact_number VARCHAR(20),
ADD COLUMN IF NOT EXISTS signup_step INTEGER DEFAULT 0, -- Track which step doctor is on (0=not started, 1=email verified, 2=info filled, 3=documents uploaded, 4=photo uploaded, 5=submitted)
ADD COLUMN IF NOT EXISTS signup_completed BOOLEAN DEFAULT FALSE;

-- Add index for signup tracking
CREATE INDEX IF NOT EXISTS idx_doctor_profiles_signup_step ON doctor_profiles(signup_step);
CREATE INDEX IF NOT EXISTS idx_doctor_profiles_signup_completed ON doctor_profiles(signup_completed);
CREATE INDEX IF NOT EXISTS idx_doctor_profiles_prc_license ON doctor_profiles(prc_license_number);

-- Add comments
COMMENT ON COLUMN doctor_profiles.prc_license_number IS 'PRC License Number for doctor registration';
COMMENT ON COLUMN doctor_profiles.prc_expiration_date IS 'PRC License expiration date';
COMMENT ON COLUMN doctor_profiles.affiliation_type IS 'Doctor affiliation: clinic_hospital, independent_private, or not_affiliated';
COMMENT ON COLUMN doctor_profiles.clinic_hospital_affiliation IS 'Name of clinic/hospital if affiliated';
COMMENT ON COLUMN doctor_profiles.professional_address IS 'Professional practice address';
COMMENT ON COLUMN doctor_profiles.hospital_clinic_contact_number IS 'Contact number of hospital/clinic';
COMMENT ON COLUMN doctor_profiles.signup_step IS 'Current step in signup process (0-5)';
COMMENT ON COLUMN doctor_profiles.signup_completed IS 'Whether doctor has completed all signup steps';

-- Create doctor_documents table for storing uploaded documents
-- Handle existing table gracefully
DO $$ 
BEGIN
    -- Drop table if it exists (this will also drop any foreign key constraints)
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'doctor_documents'
    ) THEN
        DROP TABLE doctor_documents CASCADE;
    END IF;
END $$;

-- Create the table with proper foreign key references
CREATE TABLE doctor_documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    doctor_id UUID NOT NULL,
    firebase_uid VARCHAR(255),
    document_type VARCHAR(50) NOT NULL CHECK (document_type IN ('prc_id_front', 'prc_id_back', 'ptr', 'board_certificate', 'clinic_hospital_id', 'supporting_document')),
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER, -- Size in bytes
    mime_type VARCHAR(100),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_doctor_documents_doctor_id FOREIGN KEY (doctor_id) REFERENCES doctor_profiles(id) ON DELETE CASCADE
);

-- Add foreign key for firebase_uid if user_profiles table exists
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'user_profiles'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'user_profiles' 
        AND column_name = 'firebase_uid'
    ) THEN
        ALTER TABLE doctor_documents 
        ADD CONSTRAINT fk_doctor_documents_firebase_uid 
        FOREIGN KEY (firebase_uid) REFERENCES user_profiles(firebase_uid) ON DELETE CASCADE;
    END IF;
END $$;

-- Add indexes for doctor_documents
CREATE INDEX IF NOT EXISTS idx_doctor_documents_doctor_id ON doctor_documents(doctor_id);
CREATE INDEX IF NOT EXISTS idx_doctor_documents_firebase_uid ON doctor_documents(firebase_uid);
CREATE INDEX IF NOT EXISTS idx_doctor_documents_type ON doctor_documents(document_type);

-- Add comments
COMMENT ON TABLE doctor_documents IS 'Stores uploaded documents for doctor verification';
COMMENT ON COLUMN doctor_documents.document_type IS 'Type of document: prc_id_front, prc_id_back, ptr, board_certificate, clinic_hospital_id, supporting_document';

-- Update existing doctor_profiles to set default signup_step
UPDATE doctor_profiles 
SET signup_step = 5, signup_completed = TRUE 
WHERE verification_status = 'approved' OR verification_status = 'pending';


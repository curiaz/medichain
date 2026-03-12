-- Migration: Add doctor verification fields to doctor_profiles table
-- Date: 2025-10-15
-- Description: Adds specialization, verification_document, and verification_status columns to doctor_profiles

-- Create doctor_profiles table if it doesn't exist
CREATE TABLE IF NOT EXISTS doctor_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
  firebase_uid VARCHAR(255) UNIQUE,
  specialization VARCHAR(255),
  verification_document VARCHAR(500),
  verification_status VARCHAR(50) DEFAULT 'pending',
  license_number VARCHAR(100),
  years_of_experience INTEGER,
  hospital_affiliation VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- If table already exists, add missing columns
ALTER TABLE doctor_profiles 
ADD COLUMN IF NOT EXISTS specialization VARCHAR(255);

ALTER TABLE doctor_profiles 
ADD COLUMN IF NOT EXISTS verification_document VARCHAR(500);

ALTER TABLE doctor_profiles 
ADD COLUMN IF NOT EXISTS verification_status VARCHAR(50) DEFAULT 'pending';

ALTER TABLE doctor_profiles 
ADD COLUMN IF NOT EXISTS firebase_uid VARCHAR(255);

-- Add unique constraint on firebase_uid if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'doctor_profiles_firebase_uid_key'
    ) THEN
        ALTER TABLE doctor_profiles 
        ADD CONSTRAINT doctor_profiles_firebase_uid_key UNIQUE (firebase_uid);
    END IF;
END $$;

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_doctor_profiles_user_id 
ON doctor_profiles(user_id);

CREATE INDEX IF NOT EXISTS idx_doctor_profiles_firebase_uid 
ON doctor_profiles(firebase_uid);

CREATE INDEX IF NOT EXISTS idx_doctor_profiles_verification_status 
ON doctor_profiles(verification_status);

-- Add comments to columns
COMMENT ON TABLE doctor_profiles IS 'Doctor-specific profile information including verification details';
COMMENT ON COLUMN doctor_profiles.specialization IS 'Medical specialization (e.g., Cardiology, Pediatrics)';
COMMENT ON COLUMN doctor_profiles.verification_document IS 'Filename of uploaded verification document';
COMMENT ON COLUMN doctor_profiles.verification_status IS 'Verification status: pending, approved, rejected';


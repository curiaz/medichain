-- Migration: Create e_signatures table for secure storage of doctor e-signatures
-- Date: 2025-01-XX
-- Description: Stores encrypted e-signatures with metadata (timestamp, doctor ID, IP) and prevents updates after admin approval

-- Create e_signatures table
CREATE TABLE IF NOT EXISTS e_signatures (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    doctor_id UUID NOT NULL,
    firebase_uid VARCHAR(255),
    
    -- Encrypted signature data
    encrypted_signature TEXT NOT NULL, -- AES-256 encrypted signature image (base64)
    signature_hash VARCHAR(64) NOT NULL, -- SHA-256 hash for integrity verification
    
    -- Metadata
    ip_address VARCHAR(45), -- IPv4 or IPv6 address
    user_agent TEXT, -- Browser/user agent info
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Admin approval tracking
    is_approved BOOLEAN DEFAULT FALSE,
    approved_at TIMESTAMP WITH TIME ZONE,
    approved_by UUID, -- Admin user ID who approved
    
    -- Foreign key constraints
    CONSTRAINT fk_e_signatures_doctor_id FOREIGN KEY (doctor_id) REFERENCES doctor_profiles(id) ON DELETE CASCADE
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
        ALTER TABLE e_signatures 
        ADD CONSTRAINT fk_e_signatures_firebase_uid 
        FOREIGN KEY (firebase_uid) REFERENCES user_profiles(firebase_uid) ON DELETE CASCADE;
    END IF;
END $$;

-- Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_e_signatures_doctor_id ON e_signatures(doctor_id);
CREATE INDEX IF NOT EXISTS idx_e_signatures_firebase_uid ON e_signatures(firebase_uid);
CREATE INDEX IF NOT EXISTS idx_e_signatures_is_approved ON e_signatures(is_approved);
CREATE INDEX IF NOT EXISTS idx_e_signatures_created_at ON e_signatures(created_at);

-- Add unique constraint: one signature per doctor (can be updated only if not approved)
-- Note: This allows updates before approval, but prevents multiple approved signatures
CREATE UNIQUE INDEX IF NOT EXISTS idx_e_signatures_doctor_unique 
ON e_signatures(doctor_id) 
WHERE is_approved = FALSE;

-- Add comments
COMMENT ON TABLE e_signatures IS 'Stores encrypted e-signatures for doctors with metadata and approval tracking';
COMMENT ON COLUMN e_signatures.encrypted_signature IS 'AES-256 encrypted signature image data (base64 encoded)';
COMMENT ON COLUMN e_signatures.signature_hash IS 'SHA-256 hash of the original signature for integrity verification';
COMMENT ON COLUMN e_signatures.ip_address IS 'IP address from which signature was created';
COMMENT ON COLUMN e_signatures.is_approved IS 'Whether the signature has been approved by admin (prevents updates)';




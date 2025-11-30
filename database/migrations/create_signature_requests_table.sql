-- Migration: Create signature_requests table for e-signature update requests
-- Date: 2025-01-XX
-- Description: Stores signature update requests with old/new signatures, reason, and approval status

-- Create signature_requests table
CREATE TABLE IF NOT EXISTS signature_requests (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    doctor_id UUID NOT NULL,
    firebase_uid VARCHAR(255),
    
    -- Signature data
    old_signature_id UUID, -- Reference to e_signatures table (old signature)
    new_signature_encrypted TEXT NOT NULL, -- AES-256 encrypted new signature
    new_signature_hash VARCHAR(64) NOT NULL, -- SHA-256 hash of new signature
    
    -- Request details
    reason TEXT NOT NULL, -- Reason for change provided by doctor
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    
    -- Metadata
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Review details
    reviewed_by UUID, -- Admin user ID who reviewed
    reviewed_at TIMESTAMP WITH TIME ZONE,
    review_notes TEXT, -- Optional notes from admin
    
    -- Foreign key constraints
    CONSTRAINT fk_signature_requests_doctor_id FOREIGN KEY (doctor_id) REFERENCES doctor_profiles(id) ON DELETE CASCADE,
    CONSTRAINT fk_signature_requests_old_signature FOREIGN KEY (old_signature_id) REFERENCES e_signatures(id) ON DELETE SET NULL
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
        ALTER TABLE signature_requests 
        ADD CONSTRAINT fk_signature_requests_firebase_uid 
        FOREIGN KEY (firebase_uid) REFERENCES user_profiles(firebase_uid) ON DELETE CASCADE;
    END IF;
END $$;

-- Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_signature_requests_doctor_id ON signature_requests(doctor_id);
CREATE INDEX IF NOT EXISTS idx_signature_requests_firebase_uid ON signature_requests(firebase_uid);
CREATE INDEX IF NOT EXISTS idx_signature_requests_status ON signature_requests(status);
CREATE INDEX IF NOT EXISTS idx_signature_requests_created_at ON signature_requests(created_at);
CREATE INDEX IF NOT EXISTS idx_signature_requests_reviewed_by ON signature_requests(reviewed_by);

-- Add comments
COMMENT ON TABLE signature_requests IS 'Stores e-signature update requests with approval workflow';
COMMENT ON COLUMN signature_requests.old_signature_id IS 'Reference to the current active signature';
COMMENT ON COLUMN signature_requests.new_signature_encrypted IS 'AES-256 encrypted new signature data';
COMMENT ON COLUMN signature_requests.new_signature_hash IS 'SHA-256 hash of the new signature for integrity verification';
COMMENT ON COLUMN signature_requests.reason IS 'Reason provided by doctor for signature change';
COMMENT ON COLUMN signature_requests.status IS 'Request status: pending, approved, or rejected';
COMMENT ON COLUMN signature_requests.reviewed_by IS 'Admin user ID who reviewed the request';




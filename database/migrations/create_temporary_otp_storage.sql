-- Create temporary_otp_storage table for OTP management
-- This table stores OTP codes with 1-minute expiration for email verification

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create temporary_otp_storage table
CREATE TABLE IF NOT EXISTS temporary_otp_storage (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    otp_code VARCHAR(6) NOT NULL,
    session_token TEXT NOT NULL,
    firebase_reset_link TEXT, -- Can store JSON metadata for doctor signup
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_used BOOLEAN DEFAULT FALSE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_temporary_otp_storage_email ON temporary_otp_storage(email);
CREATE INDEX IF NOT EXISTS idx_temporary_otp_storage_expires_at ON temporary_otp_storage(expires_at);
CREATE INDEX IF NOT EXISTS idx_temporary_otp_storage_is_used ON temporary_otp_storage(is_used);
CREATE INDEX IF NOT EXISTS idx_temporary_otp_storage_email_is_used ON temporary_otp_storage(email, is_used);

-- Add comments for documentation
COMMENT ON TABLE temporary_otp_storage IS 'Stores temporary OTP codes for email verification with 1-minute expiration';
COMMENT ON COLUMN temporary_otp_storage.email IS 'Email address of the user requesting OTP';
COMMENT ON COLUMN temporary_otp_storage.otp_code IS '6-digit OTP verification code';
COMMENT ON COLUMN temporary_otp_storage.session_token IS 'Secure session token for password reset flow';
COMMENT ON COLUMN temporary_otp_storage.firebase_reset_link IS 'Firebase password reset link or JSON metadata for doctor signup';
COMMENT ON COLUMN temporary_otp_storage.expires_at IS 'Timestamp when the OTP expires (1 minute from creation)';
COMMENT ON COLUMN temporary_otp_storage.is_used IS 'Flag indicating if the OTP has been used';


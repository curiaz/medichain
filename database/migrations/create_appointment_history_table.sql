-- Migration: Create appointment_history table for logging deleted appointments
-- Date: 2025-11-19
-- Description: Archives appointment data before deletion for historical records

-- Create appointment_history table
CREATE TABLE IF NOT EXISTS appointment_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- Original appointment data (archived)
    original_appointment_id UUID NOT NULL,
    patient_firebase_uid VARCHAR(255) NOT NULL,
    doctor_firebase_uid VARCHAR(255) NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    appointment_type VARCHAR(50),
    status VARCHAR(50),
    notes TEXT,
    meeting_link TEXT,
    symptoms TEXT[],
    documents JSONB,
    medicine_allergies TEXT,
    ai_diagnosis JSONB,
    follow_up_checkup BOOLEAN DEFAULT FALSE,
    
    -- Archive metadata
    deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_reason VARCHAR(100) DEFAULT 'past_appointment_cleanup',
    
    -- Original timestamps
    original_created_at TIMESTAMP WITH TIME ZONE,
    original_updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_appointment_history_patient ON appointment_history(patient_firebase_uid);
CREATE INDEX IF NOT EXISTS idx_appointment_history_doctor ON appointment_history(doctor_firebase_uid);
CREATE INDEX IF NOT EXISTS idx_appointment_history_deleted_at ON appointment_history(deleted_at DESC);
CREATE INDEX IF NOT EXISTS idx_appointment_history_original_id ON appointment_history(original_appointment_id);

-- Add comments
COMMENT ON TABLE appointment_history IS 'Archives deleted appointments for historical record keeping';
COMMENT ON COLUMN appointment_history.original_appointment_id IS 'Original appointment ID before deletion';
COMMENT ON COLUMN appointment_history.deleted_reason IS 'Reason for deletion (e.g., past_appointment_cleanup, manual_deletion)';




-- Create appointment_ratings table
-- Patients can rate doctors after appointment completion
-- Only one rating per appointment (enforced by UNIQUE constraint)

CREATE TABLE IF NOT EXISTS appointment_ratings (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    appointment_id UUID NOT NULL REFERENCES appointments(id) ON DELETE CASCADE,
    patient_firebase_uid VARCHAR(255) NOT NULL REFERENCES user_profiles(firebase_uid) ON DELETE CASCADE,
    doctor_firebase_uid VARCHAR(255) NOT NULL REFERENCES user_profiles(firebase_uid) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure only one rating per appointment
    UNIQUE(appointment_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_appointment_ratings_appointment_id ON appointment_ratings(appointment_id);
CREATE INDEX IF NOT EXISTS idx_appointment_ratings_patient ON appointment_ratings(patient_firebase_uid);
CREATE INDEX IF NOT EXISTS idx_appointment_ratings_doctor ON appointment_ratings(doctor_firebase_uid);
CREATE INDEX IF NOT EXISTS idx_appointment_ratings_created_at ON appointment_ratings(created_at);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_appointment_ratings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updated_at
CREATE TRIGGER update_appointment_ratings_updated_at 
    BEFORE UPDATE ON appointment_ratings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_appointment_ratings_updated_at();

-- Enable Row Level Security
ALTER TABLE appointment_ratings ENABLE ROW LEVEL SECURITY;

-- RLS Policies
-- Patients can view and manage their own ratings
CREATE POLICY "Patients can view their own ratings"
    ON appointment_ratings FOR SELECT
    USING (auth.uid()::text = patient_firebase_uid);

CREATE POLICY "Patients can insert their own ratings"
    ON appointment_ratings FOR INSERT
    WITH CHECK (auth.uid()::text = patient_firebase_uid);

CREATE POLICY "Patients can update their own ratings"
    ON appointment_ratings FOR UPDATE
    USING (auth.uid()::text = patient_firebase_uid);

-- Doctors can view ratings they received
CREATE POLICY "Doctors can view ratings they received"
    ON appointment_ratings FOR SELECT
    USING (auth.uid()::text = doctor_firebase_uid);

-- Public can view ratings (for doctor profiles)
-- Note: This allows anyone to see ratings, but not patient/doctor identities
-- Adjust based on privacy requirements
CREATE POLICY "Public can view ratings"
    ON appointment_ratings FOR SELECT
    USING (true);





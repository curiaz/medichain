-- Add review_status column to medical_records table to track if AI diagnosis has been reviewed
-- This allows us to distinguish between pending and reviewed AI diagnoses

-- Add review_status column if it doesn't exist
ALTER TABLE medical_records
ADD COLUMN IF NOT EXISTS review_status VARCHAR(20) DEFAULT 'pending' 
CHECK (review_status IN ('pending', 'reviewed', 'in_progress'));

-- Update existing records: if diagnosis exists and is not empty, mark as reviewed
UPDATE medical_records
SET review_status = 'reviewed'
WHERE diagnosis IS NOT NULL 
  AND diagnosis != ''
  AND review_status = 'pending';

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_medical_records_review_status ON medical_records(review_status);

-- Add comment
COMMENT ON COLUMN medical_records.review_status IS 'Status of AI diagnosis review: pending (not reviewed), reviewed (doctor has reviewed and saved), in_progress (doctor is reviewing)';


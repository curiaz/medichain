-- Verification script to check if review_status migration was successful
-- Run this after executing add_review_status_to_medical_records.sql

-- 1. Check if review_status column exists
SELECT 
    column_name, 
    data_type, 
    column_default,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'medical_records' 
  AND column_name = 'review_status';

-- 2. Check if index exists
SELECT 
    indexname, 
    indexdef
FROM pg_indexes 
WHERE tablename = 'medical_records' 
  AND indexname = 'idx_medical_records_review_status';

-- 3. Check distribution of review_status values
SELECT 
    review_status,
    COUNT(*) as count
FROM medical_records
GROUP BY review_status
ORDER BY review_status;

-- 4. Check if trigger exists for updated_at
SELECT 
    trigger_name, 
    event_manipulation, 
    event_object_table,
    action_statement
FROM information_schema.triggers 
WHERE trigger_name = 'set_medical_records_updated_at';

-- 5. Sample data check - show a few records with their review_status
SELECT 
    id,
    appointment_id,
    patient_firebase_uid,
    diagnosis,
    review_status,
    created_at,
    updated_at
FROM medical_records
ORDER BY updated_at DESC
LIMIT 5;


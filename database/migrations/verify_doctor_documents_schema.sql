-- Verification Script: Check doctor_documents table schema
-- This script verifies that all required columns exist in the doctor_documents table

-- Check if table exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'doctor_documents'
    ) THEN
        RAISE EXCEPTION 'doctor_documents table does not exist. Please run add_doctor_signup_fields.sql migration first.';
    ELSE
        RAISE NOTICE '✅ doctor_documents table exists';
    END IF;
END $$;

-- List all columns in doctor_documents table
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public' 
    AND table_name = 'doctor_documents'
ORDER BY ordinal_position;

-- Expected columns:
-- 1. id (uuid, PRIMARY KEY)
-- 2. doctor_id (uuid, NOT NULL)
-- 3. firebase_uid (varchar)
-- 4. document_type (varchar, NOT NULL)
-- 5. file_name (varchar, NOT NULL)
-- 6. file_path (text, NOT NULL)
-- 7. file_size (integer)
-- 8. mime_type (varchar)
-- 9. uploaded_at (timestamp with time zone)
-- 10. created_at (timestamp with time zone)
-- 11. updated_at (timestamp with time zone)

-- Check for missing columns and add them if needed
DO $$ 
BEGIN
    -- Check and add file_name if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'doctor_documents' 
        AND column_name = 'file_name'
    ) THEN
        ALTER TABLE doctor_documents ADD COLUMN file_name VARCHAR(255) NOT NULL DEFAULT '';
        RAISE NOTICE '✅ Added file_name column';
    END IF;
    
    -- Check and add file_path if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'doctor_documents' 
        AND column_name = 'file_path'
    ) THEN
        ALTER TABLE doctor_documents ADD COLUMN file_path TEXT NOT NULL DEFAULT '';
        RAISE NOTICE '✅ Added file_path column';
    END IF;
    
    -- Check and add file_size if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'doctor_documents' 
        AND column_name = 'file_size'
    ) THEN
        ALTER TABLE doctor_documents ADD COLUMN file_size INTEGER;
        RAISE NOTICE '✅ Added file_size column';
    END IF;
    
    -- Check and add mime_type if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'doctor_documents' 
        AND column_name = 'mime_type'
    ) THEN
        ALTER TABLE doctor_documents ADD COLUMN mime_type VARCHAR(100);
        RAISE NOTICE '✅ Added mime_type column';
    END IF;
    
    -- Check and add uploaded_at if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'doctor_documents' 
        AND column_name = 'uploaded_at'
    ) THEN
        ALTER TABLE doctor_documents ADD COLUMN uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
        RAISE NOTICE '✅ Added uploaded_at column';
    END IF;
    
    -- Check and add created_at if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'doctor_documents' 
        AND column_name = 'created_at'
    ) THEN
        ALTER TABLE doctor_documents ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
        RAISE NOTICE '✅ Added created_at column';
    END IF;
    
    -- Check and add updated_at if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'doctor_documents' 
        AND column_name = 'updated_at'
    ) THEN
        ALTER TABLE doctor_documents ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
        RAISE NOTICE '✅ Added updated_at column';
    END IF;
    
    RAISE NOTICE '✅ All required columns verified/added';
END $$;

-- Verify foreign key constraints
SELECT 
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_name = 'doctor_documents';

-- Summary
DO $$
DECLARE
    column_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO column_count
    FROM information_schema.columns
    WHERE table_schema = 'public' 
        AND table_name = 'doctor_documents';
    
    RAISE NOTICE '📊 Total columns in doctor_documents: %', column_count;
    
    IF column_count >= 11 THEN
        RAISE NOTICE '✅ doctor_documents table has all required columns';
    ELSE
        RAISE WARNING '⚠️  doctor_documents table may be missing some columns. Expected 11, found %', column_count;
    END IF;
END $$;


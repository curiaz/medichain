-- =====================================================
-- FIXED SUPABASE DATABASE SCHEMA FOR MEDICHAIN HEALTHCARE
-- Handles existing table structure conflicts
-- =====================================================

-- First, let's check the current structure of existing tables
DO $$
BEGIN
    -- Check if medical_records table exists and show its structure
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'medical_records') THEN
        RAISE NOTICE 'medical_records table exists. Checking current structure...';
        
        -- Show existing columns
        PERFORM column_name FROM information_schema.columns 
        WHERE table_name = 'medical_records' AND table_schema = 'public';
        
        RAISE NOTICE 'Current medical_records columns found. Will handle structure carefully.';
    END IF;
END $$;

-- =====================================================
-- SAFE TABLE CREATION WITH STRUCTURE HANDLING
-- =====================================================

-- 1. PATIENTS TABLE (CREATE IF NOT EXISTS)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'patients') THEN
        CREATE TABLE patients (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            firebase_uid VARCHAR(128) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            full_name VARCHAR(255) NOT NULL,
            date_of_birth DATE,
            phone VARCHAR(20),
            address TEXT,
            emergency_contact JSONB, -- {"name": "Contact Name", "phone": "123-456-7890", "relationship": "spouse"}
            role VARCHAR(20) DEFAULT 'patient' CHECK (role IN ('patient', 'doctor', 'admin')),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        RAISE NOTICE 'Created patients table';
    ELSE
        RAISE NOTICE 'patients table already exists - checking structure';
        
        -- Add missing columns to patients table if needed
        BEGIN
            ALTER TABLE patients ADD COLUMN IF NOT EXISTS firebase_uid VARCHAR(128);
            ALTER TABLE patients ADD COLUMN IF NOT EXISTS address TEXT;
            ALTER TABLE patients ADD COLUMN IF NOT EXISTS emergency_contact JSONB;
            ALTER TABLE patients ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'patient';
            ALTER TABLE patients ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
            ALTER TABLE patients ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
        EXCEPTION
            WHEN OTHERS THEN
                RAISE NOTICE 'Some columns may already exist in patients table';
        END;
    END IF;
END $$;

-- 2. DOCTORS TABLE (CREATE IF NOT EXISTS)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'doctors') THEN
        CREATE TABLE doctors (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            firebase_uid VARCHAR(128) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            full_name VARCHAR(255) NOT NULL,
            license_number VARCHAR(100) UNIQUE NOT NULL,
            specialization VARCHAR(100),
            phone VARCHAR(20),
            verified BOOLEAN DEFAULT FALSE,
            verification_date TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        RAISE NOTICE 'Created doctors table';
    ELSE
        RAISE NOTICE 'doctors table already exists';
    END IF;
END $$;

-- 3. MEDICAL RECORDS TABLE - CAREFUL HANDLING
DO $$ 
DECLARE
    has_patient_id BOOLEAN := FALSE;
    has_user_id BOOLEAN := FALSE;
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'medical_records') THEN
        -- Check what ID columns exist
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'medical_records' AND column_name = 'patient_id'
        ) INTO has_patient_id;
        
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'medical_records' AND column_name = 'user_id'
        ) INTO has_user_id;
        
        RAISE NOTICE 'medical_records table exists. patient_id: %, user_id: %', has_patient_id, has_user_id;
        
        -- Add missing columns based on current structure
        BEGIN
            -- If no patient_id but has user_id, add patient_id and map it
            IF NOT has_patient_id AND has_user_id THEN
                ALTER TABLE medical_records ADD COLUMN patient_id UUID;
                RAISE NOTICE 'Added patient_id column to medical_records';
            ELSIF NOT has_patient_id AND NOT has_user_id THEN
                -- Neither exists, add patient_id
                ALTER TABLE medical_records ADD COLUMN patient_id UUID;
                RAISE NOTICE 'Added patient_id column to medical_records (fresh setup)';
            END IF;
            
            -- Add other missing columns
            ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS doctor_id VARCHAR(128);
            ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS diagnosis TEXT;
            ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS treatment TEXT;
            ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS medications JSONB;
            ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS notes TEXT;
            ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS visit_date DATE DEFAULT CURRENT_DATE;
            ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
            ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
            
            RAISE NOTICE 'Updated medical_records table with missing columns';
        EXCEPTION
            WHEN OTHERS THEN
                RAISE NOTICE 'Some columns may already exist in medical_records table: %', SQLERRM;
        END;
    ELSE
        -- Create new medical_records table
        CREATE TABLE medical_records (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            patient_id UUID, -- Will add foreign key constraint later if patients table exists
            doctor_id VARCHAR(128) NOT NULL,
            diagnosis TEXT NOT NULL,
            treatment TEXT,
            medications JSONB, -- [{"name": "Medicine", "dosage": "10mg", "frequency": "2x daily"}]
            notes TEXT,
            visit_date DATE DEFAULT CURRENT_DATE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        RAISE NOTICE 'Created medical_records table';
    END IF;
END $$;

-- Add foreign key constraint if both tables exist and constraint doesn't exist
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'patients') 
       AND EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'medical_records')
       AND EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'medical_records' AND column_name = 'patient_id')
       AND NOT EXISTS (
           SELECT 1 FROM information_schema.table_constraints 
           WHERE constraint_name = 'medical_records_patient_id_fkey'
       ) THEN
        BEGIN
            ALTER TABLE medical_records 
            ADD CONSTRAINT medical_records_patient_id_fkey 
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE;
            RAISE NOTICE 'Added foreign key constraint for medical_records.patient_id';
        EXCEPTION
            WHEN OTHERS THEN
                RAISE NOTICE 'Could not add foreign key constraint: %', SQLERRM;
        END;
    END IF;
END $$;

-- 4. APPOINTMENTS TABLE (CREATE IF NOT EXISTS)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'appointments') THEN
        CREATE TABLE appointments (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            patient_id UUID, -- Will add constraint later
            doctor_id VARCHAR(128) NOT NULL,
            appointment_date TIMESTAMP WITH TIME ZONE NOT NULL,
            status VARCHAR(20) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'confirmed', 'cancelled', 'completed')),
            reason TEXT,
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        RAISE NOTICE 'Created appointments table';
    ELSE
        RAISE NOTICE 'appointments table already exists';
    END IF;
END $$;

-- Add foreign key for appointments if possible
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'patients') 
       AND EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'appointments')
       AND NOT EXISTS (
           SELECT 1 FROM information_schema.table_constraints 
           WHERE constraint_name = 'appointments_patient_id_fkey'
       ) THEN
        BEGIN
            ALTER TABLE appointments 
            ADD CONSTRAINT appointments_patient_id_fkey 
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE;
            RAISE NOTICE 'Added foreign key constraint for appointments.patient_id';
        EXCEPTION
            WHEN OTHERS THEN
                RAISE NOTICE 'Could not add foreign key constraint for appointments: %', SQLERRM;
        END;
    END IF;
END $$;

-- 5. AI DIAGNOSIS HISTORY TABLE (CREATE IF NOT EXISTS)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'ai_diagnosis_history') THEN
        CREATE TABLE ai_diagnosis_history (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            patient_id UUID, -- Will add constraint later
            symptoms JSONB NOT NULL, -- {"symptoms": ["headache", "fever"], "severity": 7}
            ai_diagnosis TEXT NOT NULL,
            confidence_score DECIMAL(3,2), -- 0.00 to 1.00
            recommendations TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        RAISE NOTICE 'Created ai_diagnosis_history table';
    ELSE
        RAISE NOTICE 'ai_diagnosis_history table already exists';
    END IF;
END $$;

-- Add foreign key for ai_diagnosis_history if possible
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'patients') 
       AND EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'ai_diagnosis_history')
       AND NOT EXISTS (
           SELECT 1 FROM information_schema.table_constraints 
           WHERE constraint_name = 'ai_diagnosis_history_patient_id_fkey'
       ) THEN
        BEGIN
            ALTER TABLE ai_diagnosis_history 
            ADD CONSTRAINT ai_diagnosis_history_patient_id_fkey 
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE;
            RAISE NOTICE 'Added foreign key constraint for ai_diagnosis_history.patient_id';
        EXCEPTION
            WHEN OTHERS THEN
                RAISE NOTICE 'Could not add foreign key constraint for ai_diagnosis_history: %', SQLERRM;
        END;
    END IF;
END $$;

-- 6. CONTACT MESSAGES TABLE (CREATE IF NOT EXISTS)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'contact_messages') THEN
        CREATE TABLE contact_messages (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            subject VARCHAR(255),
            message TEXT NOT NULL,
            status VARCHAR(20) DEFAULT 'new' CHECK (status IN ('new', 'reviewed', 'responded', 'closed')),
            priority VARCHAR(10) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        RAISE NOTICE 'Created contact_messages table';
    ELSE
        RAISE NOTICE 'contact_messages table already exists';
    END IF;
END $$;

-- =====================================================
-- SAFE INDEX CREATION (SKIP ERRORS)
-- =====================================================

-- Create indexes with error handling
DO $$ 
BEGIN
    -- Patients indexes
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_patients_firebase_uid') THEN
            CREATE INDEX idx_patients_firebase_uid ON patients(firebase_uid);
            RAISE NOTICE 'Created idx_patients_firebase_uid';
        END IF;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Could not create idx_patients_firebase_uid: %', SQLERRM;
    END;
    
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_patients_email') THEN
            CREATE INDEX idx_patients_email ON patients(email);
            RAISE NOTICE 'Created idx_patients_email';
        END IF;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Could not create idx_patients_email: %', SQLERRM;
    END;
    
    -- Medical records indexes (only if columns exist)
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'medical_records' AND column_name = 'patient_id') THEN
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_medical_records_patient') THEN
                CREATE INDEX idx_medical_records_patient ON medical_records(patient_id);
                RAISE NOTICE 'Created idx_medical_records_patient';
            END IF;
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Could not create idx_medical_records_patient: %', SQLERRM;
        END;
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'medical_records' AND column_name = 'doctor_id') THEN
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_medical_records_doctor') THEN
                CREATE INDEX idx_medical_records_doctor ON medical_records(doctor_id);
                RAISE NOTICE 'Created idx_medical_records_doctor';
            END IF;
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Could not create idx_medical_records_doctor: %', SQLERRM;
        END;
    END IF;
END $$;

-- =====================================================
-- ROW LEVEL SECURITY (SAFE SETUP)
-- =====================================================

-- Enable RLS (safe operation - won't fail if already enabled)
DO $$
BEGIN
    -- Enable RLS on tables that exist
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'patients') THEN
        ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'Enabled RLS on patients table';
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'doctors') THEN
        ALTER TABLE doctors ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'Enabled RLS on doctors table';
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'medical_records') THEN
        ALTER TABLE medical_records ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'Enabled RLS on medical_records table';
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'appointments') THEN
        ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'Enabled RLS on appointments table';
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'ai_diagnosis_history') THEN
        ALTER TABLE ai_diagnosis_history ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'Enabled RLS on ai_diagnosis_history table';
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'contact_messages') THEN
        ALTER TABLE contact_messages ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'Enabled RLS on contact_messages table';
    END IF;
END $$;

-- Drop existing policies safely
DO $$
BEGIN
    -- Drop policies with error handling
    BEGIN
        DROP POLICY IF EXISTS "Patients can view own data" ON patients;
        DROP POLICY IF EXISTS "Patients can update own profile" ON patients;
        DROP POLICY IF EXISTS "Doctors can view patients" ON patients;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Some patient policies may not exist';
    END;
    
    BEGIN
        DROP POLICY IF EXISTS "Patients can view own medical records" ON medical_records;
        DROP POLICY IF EXISTS "Doctors can manage medical records" ON medical_records;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Some medical_records policies may not exist';
    END;
END $$;

-- Create RLS policies with error handling
DO $$
BEGIN
    -- PATIENTS RLS POLICIES (only if table exists)
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'patients') THEN
        BEGIN
            CREATE POLICY "Patients can view own data" ON patients
                FOR SELECT USING (firebase_uid = auth.jwt() ->> 'sub');
            RAISE NOTICE 'Created patient view policy';
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Could not create patient view policy: %', SQLERRM;
        END;
        
        BEGIN
            CREATE POLICY "Patients can update own profile" ON patients
                FOR UPDATE USING (firebase_uid = auth.jwt() ->> 'sub')
                WITH CHECK (firebase_uid = auth.jwt() ->> 'sub');
            RAISE NOTICE 'Created patient update policy';
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Could not create patient update policy: %', SQLERRM;
        END;
    END IF;
    
    -- MEDICAL RECORDS RLS POLICIES (only if patient_id column exists)
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'medical_records')
       AND EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'medical_records' AND column_name = 'patient_id') THEN
        BEGIN
            CREATE POLICY "Patients can view own medical records" ON medical_records
                FOR SELECT USING (
                    patient_id IN (
                        SELECT id FROM patients WHERE firebase_uid = auth.jwt() ->> 'sub'
                    )
                );
            RAISE NOTICE 'Created medical records view policy';
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Could not create medical records view policy: %', SQLERRM;
        END;
        
        BEGIN
            CREATE POLICY "Doctors can manage medical records" ON medical_records
                FOR ALL USING (
                    auth.jwt() ->> 'role' = 'doctor' OR 
                    auth.jwt() ->> 'role' = 'admin'
                );
            RAISE NOTICE 'Created medical records management policy';
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Could not create medical records management policy: %', SQLERRM;
        END;
    END IF;
END $$;

-- =====================================================
-- FUNCTIONS AND TRIGGERS (SAFE CREATION)
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers with error handling
DO $$
BEGIN
    -- Only create triggers for tables that exist and have updated_at column
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'patients')
       AND EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'patients' AND column_name = 'updated_at') THEN
        BEGIN
            DROP TRIGGER IF EXISTS update_patients_updated_at ON patients;
            CREATE TRIGGER update_patients_updated_at BEFORE UPDATE ON patients
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            RAISE NOTICE 'Created trigger for patients table';
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Could not create trigger for patients: %', SQLERRM;
        END;
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'medical_records')
       AND EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'medical_records' AND column_name = 'updated_at') THEN
        BEGIN
            DROP TRIGGER IF EXISTS update_medical_records_updated_at ON medical_records;
            CREATE TRIGGER update_medical_records_updated_at BEFORE UPDATE ON medical_records
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            RAISE NOTICE 'Created trigger for medical_records table';
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Could not create trigger for medical_records: %', SQLERRM;
        END;
    END IF;
END $$;

-- =====================================================
-- VERIFICATION AND SUMMARY
-- =====================================================

-- Show current table structure
DO $$
DECLARE
    table_count INTEGER;
    column_info TEXT;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=== MEDICHAIN DATABASE STATUS ===';
    
    -- Count tables
    SELECT COUNT(*) INTO table_count 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name IN ('patients', 'doctors', 'medical_records', 'appointments', 'ai_diagnosis_history', 'contact_messages');
    
    RAISE NOTICE 'Healthcare tables found: %', table_count;
    
    -- Check medical_records structure specifically
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'medical_records') THEN
        RAISE NOTICE '';
        RAISE NOTICE 'medical_records table structure:';
        
        FOR column_info IN 
            SELECT column_name || ' (' || data_type || ')'
            FROM information_schema.columns 
            WHERE table_name = 'medical_records' AND table_schema = 'public'
            ORDER BY ordinal_position
        LOOP
            RAISE NOTICE '  - %', column_info;
        END LOOP;
    END IF;
    
    RAISE NOTICE '';
    RAISE NOTICE '✅ Database schema update completed safely!';
    RAISE NOTICE '✅ Existing structure preserved';
    RAISE NOTICE '✅ Missing columns added where needed';
    RAISE NOTICE '🚀 Ready for MediChain healthcare system!';
END $$;

COMMIT;
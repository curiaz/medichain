-- Fix Row-Level Security (RLS) for doctor_profiles table
-- This allows the backend service to insert/update/select doctor profiles

-- Option 1: Disable RLS (simplest for development/backend service)
ALTER TABLE doctor_profiles DISABLE ROW LEVEL SECURITY;

-- Option 2: If you want to keep RLS enabled, uncomment these policies instead:
-- (Comment out the line above and uncomment the policies below)

/*
-- Enable RLS
ALTER TABLE doctor_profiles ENABLE ROW LEVEL SECURITY;

-- Allow service role to do everything (backend operations)
CREATE POLICY "Allow service role full access"
ON doctor_profiles
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- Allow authenticated users to read their own doctor profile
CREATE POLICY "Users can view their own doctor profile"
ON doctor_profiles
FOR SELECT
TO authenticated
USING (auth.uid()::text = firebase_uid);

-- Allow authenticated users to update their own doctor profile
CREATE POLICY "Users can update their own doctor profile"
ON doctor_profiles
FOR UPDATE
TO authenticated
USING (auth.uid()::text = firebase_uid)
WITH CHECK (auth.uid()::text = firebase_uid);

-- Allow public insert (for doctor signup)
CREATE POLICY "Allow doctor signup"
ON doctor_profiles
FOR INSERT
TO anon, authenticated
WITH CHECK (true);
*/


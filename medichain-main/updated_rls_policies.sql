-- Updated RLS policies without auth.users dependency
-- Run this in your Supabase SQL editor

-- First remove the foreign key constraint
ALTER TABLE profiles DROP CONSTRAINT IF EXISTS profiles_id_fkey;

-- Drop existing policies
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
DROP POLICY IF EXISTS "Service role can manage profiles" ON profiles;

-- Create new policies that don't depend on auth.uid()
-- Allow service role to manage all profiles
CREATE POLICY "Service role can manage profiles" ON profiles
    FOR ALL USING (auth.role() = 'service_role');

-- Allow public access for now (we'll handle auth in the backend)
CREATE POLICY "Allow profile access" ON profiles
    FOR ALL USING (true);

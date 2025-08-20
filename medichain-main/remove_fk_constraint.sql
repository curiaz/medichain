-- Remove the foreign key constraint on profiles table
-- This allows us to create profiles without requiring auth.users entries

-- Step 1: Drop the existing foreign key constraint that references auth.users
ALTER TABLE profiles DROP CONSTRAINT IF EXISTS profiles_id_fkey;

-- Step 2: Update RLS policies to allow service role access
-- Drop existing restrictive policies
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
DROP POLICY IF EXISTS "Service role can manage profiles" ON profiles;
DROP POLICY IF EXISTS "Allow authenticated profile access" ON profiles;

-- Create simple policies that allow backend operations
CREATE POLICY "Service role can manage profiles" ON profiles
    FOR ALL USING (auth.role() = 'service_role');

-- Allow authenticated users to access profiles (we'll handle auth in backend)
CREATE POLICY "Allow authenticated profile access" ON profiles
    FOR ALL TO authenticated USING (true);

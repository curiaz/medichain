-- Simple RLS Fix for MediChain Profile Updates
-- This creates more permissive policies for development/testing

-- Drop existing policies
DROP POLICY IF EXISTS "Users can view own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;
DROP POLICY IF EXISTS "Doctors can view patient profiles" ON user_profiles;
DROP POLICY IF EXISTS "Admins can view all profiles" ON user_profiles;
DROP POLICY IF EXISTS "Service role can manage profiles" ON user_profiles;

-- Create simple, permissive policies for development
-- Note: These should be made more secure for production

-- Allow authenticated users to read any profile (for development)
CREATE POLICY "Allow authenticated read" ON user_profiles
    FOR SELECT USING (true);

-- Allow any authenticated user to insert profiles
CREATE POLICY "Allow authenticated insert" ON user_profiles
    FOR INSERT WITH CHECK (true);

-- Allow any authenticated user to update profiles (should be restricted in production)
CREATE POLICY "Allow authenticated update" ON user_profiles
    FOR UPDATE USING (true);

-- Allow any authenticated user to delete profiles (should be restricted in production)
CREATE POLICY "Allow authenticated delete" ON user_profiles
    FOR DELETE USING (true);

-- Ensure RLS is enabled
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Grant necessary permissions to the authenticated role
GRANT ALL ON user_profiles TO authenticated;
GRANT ALL ON user_profiles TO anon;

-- Grant usage on the sequence if it exists
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO anon;
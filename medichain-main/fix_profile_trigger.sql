-- Fix the profile creation trigger to handle null values properly
-- This addresses the "null value in column 'first_name'" error

-- Drop the existing trigger and function if they exist
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP FUNCTION IF EXISTS public.handle_new_user();

-- Create the improved trigger function with COALESCE for default values
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (
    id,
    email,
    first_name,
    last_name,
    role,
    created_at,
    updated_at
  ) VALUES (
    NEW.id,
    NEW.email,
    -- Use COALESCE to provide default values if metadata is missing
    COALESCE(NEW.raw_user_meta_data->>'first_name', 'User'),
    COALESCE(NEW.raw_user_meta_data->>'last_name', 'Account'),
    COALESCE(NEW.raw_user_meta_data->>'role', 'patient'),
    NOW(),
    NOW()
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create the trigger
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Also update the existing profile record creation to handle metadata properly
-- This is an alternative approach that creates profiles manually if the trigger fails
CREATE OR REPLACE FUNCTION public.create_profile_safe(
  user_id UUID,
  user_email TEXT,
  user_first_name TEXT DEFAULT 'User',
  user_last_name TEXT DEFAULT 'Account', 
  user_role TEXT DEFAULT 'patient'
)
RETURNS JSON AS $$
DECLARE
  result JSON;
BEGIN
  -- Try to insert or update the profile with safe defaults
  INSERT INTO public.profiles (
    id,
    email,
    first_name,
    last_name,
    role,
    created_at,
    updated_at
  ) VALUES (
    user_id,
    user_email,
    COALESCE(user_first_name, 'User'),
    COALESCE(user_last_name, 'Account'),
    COALESCE(user_role, 'patient'),
    NOW(),
    NOW()
  )
  ON CONFLICT (id) DO UPDATE SET
    email = EXCLUDED.email,
    first_name = COALESCE(EXCLUDED.first_name, profiles.first_name, 'User'),
    last_name = COALESCE(EXCLUDED.last_name, profiles.last_name, 'Account'),
    role = COALESCE(EXCLUDED.role, profiles.role, 'patient'),
    updated_at = NOW()
  RETURNING to_json(profiles.*) INTO result;
  
  RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions
GRANT EXECUTE ON FUNCTION public.handle_new_user() TO authenticated, anon;
GRANT EXECUTE ON FUNCTION public.create_profile_safe(UUID, TEXT, TEXT, TEXT, TEXT) TO authenticated, anon, service_role;

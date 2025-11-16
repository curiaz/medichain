-- Add privacy columns to user_profiles table
-- These columns control user privacy settings and data sharing preferences

ALTER TABLE user_profiles
ADD COLUMN IF NOT EXISTS profile_visibility VARCHAR(20) DEFAULT 'private' CHECK (profile_visibility IN ('private', 'doctors_only', 'public')),
ADD COLUMN IF NOT EXISTS show_email BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS show_phone BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS medical_info_visible_to_doctors BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS allow_ai_analysis BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS share_data_for_research BOOLEAN DEFAULT FALSE;

-- Add comment for documentation
COMMENT ON COLUMN user_profiles.profile_visibility IS 'Controls who can see the user profile: private, doctors_only, or public';
COMMENT ON COLUMN user_profiles.show_email IS 'Whether to display email in profile';
COMMENT ON COLUMN user_profiles.show_phone IS 'Whether to display phone number in profile';
COMMENT ON COLUMN user_profiles.medical_info_visible_to_doctors IS 'Allow doctors to access medical information';
COMMENT ON COLUMN user_profiles.allow_ai_analysis IS 'Allow AI to analyze health data for insights';
COMMENT ON COLUMN user_profiles.share_data_for_research IS 'Share anonymized data for medical research';

-- Refresh the schema cache for PostgREST
NOTIFY pgrst, 'reload schema';

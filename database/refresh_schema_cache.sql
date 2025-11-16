-- Force refresh Supabase PostgREST schema cache
-- Run this after adding new columns to tables

-- Method 1: Notify PostgREST to reload schema
NOTIFY pgrst, 'reload schema';

-- Method 2: Check if columns exist
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'user_profiles'
  AND column_name IN (
    'profile_visibility',
    'show_email', 
    'show_phone',
    'medical_info_visible_to_doctors',
    'allow_ai_analysis',
    'share_data_for_research'
  )
ORDER BY column_name;

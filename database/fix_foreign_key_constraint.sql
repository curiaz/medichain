-- Remove the foreign key constraint on doctor_profiles.firebase_uid
-- We'll rely on triggers to maintain consistency instead

-- First, drop the existing foreign key constraint
ALTER TABLE doctor_profiles DROP CONSTRAINT IF EXISTS doctor_profiles_firebase_uid_fkey;

-- Add a regular (non-foreign key) index on firebase_uid for performance
CREATE INDEX IF NOT EXISTS idx_doctor_profiles_firebase_uid_lookup ON doctor_profiles(firebase_uid);

-- The triggers will ensure data consistency
-- Trigger 1: When doctor_profiles is inserted/updated, sync firebase_uid from user_profiles
CREATE OR REPLACE FUNCTION sync_doctor_firebase_uid()
RETURNS TRIGGER AS $$
BEGIN
    -- Get the firebase_uid from user_profiles using the user_id
    NEW.firebase_uid := (SELECT firebase_uid FROM public.user_profiles WHERE id = NEW.user_id);

    -- If no matching user found, raise an error
    IF NEW.firebase_uid IS NULL THEN
        RAISE EXCEPTION 'No user profile found for user_id %', NEW.user_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger 2: When user_profiles.firebase_uid changes, update all related doctor_profiles
CREATE OR REPLACE FUNCTION update_doctor_firebase_uid_on_user_change()
RETURNS TRIGGER AS $$
BEGIN
    -- Only update if firebase_uid actually changed
    IF OLD.firebase_uid IS DISTINCT FROM NEW.firebase_uid THEN
        UPDATE public.doctor_profiles
        SET firebase_uid = NEW.firebase_uid
        WHERE user_id = NEW.id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply the triggers
DROP TRIGGER IF EXISTS trg_sync_doctor_firebase_uid ON public.doctor_profiles;
CREATE TRIGGER trg_sync_doctor_firebase_uid
BEFORE INSERT OR UPDATE ON public.doctor_profiles
FOR EACH ROW EXECUTE FUNCTION sync_doctor_firebase_uid();

DROP TRIGGER IF EXISTS trg_update_doctor_firebase_uid_on_user_change ON public.user_profiles;
CREATE TRIGGER trg_update_doctor_firebase_uid_on_user_change
AFTER UPDATE ON public.user_profiles
FOR EACH ROW EXECUTE FUNCTION update_doctor_firebase_uid_on_user_change();

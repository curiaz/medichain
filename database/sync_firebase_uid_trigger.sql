-- Add trigger to automatically sync firebase_uid in doctor_profiles
-- This ensures doctor_profiles.firebase_uid always matches user_profiles.firebase_uid

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

-- Create the trigger
CREATE TRIGGER trg_sync_doctor_firebase_uid
BEFORE INSERT OR UPDATE ON public.doctor_profiles
FOR EACH ROW EXECUTE FUNCTION sync_doctor_firebase_uid();

-- Also create a trigger to update doctor_profiles when user_profiles.firebase_uid changes
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

-- Create trigger on user_profiles
CREATE TRIGGER trg_update_doctor_firebase_uid_on_user_change
AFTER UPDATE ON public.user_profiles
FOR EACH ROW EXECUTE FUNCTION update_doctor_firebase_uid_on_user_change();

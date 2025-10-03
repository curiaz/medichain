-- Migration: add secure license columns to doctor_profiles
-- Run this in your Supabase SQL editor or via psql connected to your database

BEGIN;

ALTER TABLE IF EXISTS public.doctor_profiles
    ADD COLUMN IF NOT EXISTS license_number_hash VARCHAR(64);

ALTER TABLE IF EXISTS public.doctor_profiles
    ADD COLUMN IF NOT EXISTS license_number_enc TEXT;

-- Optional index to speed up lookups by the deterministic SHA-256 hash
CREATE INDEX IF NOT EXISTS idx_doctor_profiles_license_hash ON public.doctor_profiles(license_number_hash);

COMMIT;

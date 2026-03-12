# Quick Fix: Appointments Not Fetching

## Problem
Appointments exist in the database but cannot be fetched. From your screenshot, I can see:
- **4 appointments** in the `appointments` table
- All appointments have `doctor_firebase_uid`: `fLmNDKoCp1e0vQrOAs7bSYLSB8y1`
- The logged-in user likely has a **different Firebase UID**

## Root Cause
**Firebase UID Mismatch** - Your logged-in Firebase UID doesn't match the `doctor_firebase_uid` in the appointments table.

## Quick Fix Options

### Option 1: Update Appointments to Match Your Current UID (Recommended)

**Step 1: Get your current Firebase UID**
1. Open browser console (F12)
2. Run: `JSON.parse(localStorage.getItem('medichain_user')).firebase_uid` or `JSON.parse(localStorage.getItem('medichain_user')).uid`
3. Copy the UID

**Step 2: Update the appointments table**
Run this SQL in Supabase SQL Editor:

```sql
-- Replace 'YOUR_CURRENT_FIREBASE_UID' with the UID from Step 1
UPDATE appointments 
SET doctor_firebase_uid = 'YOUR_CURRENT_FIREBASE_UID'
WHERE doctor_firebase_uid = 'fLmNDKoCp1e0vQrOAs7bSYLSB8y1';
```

**Step 3: Verify**
```sql
-- Check that appointments are updated
SELECT id, doctor_firebase_uid, appointment_date, appointment_time 
FROM appointments;
```

### Option 2: Update Your User Profile to Match Appointments

If you want to use the UID that's already in the appointments:

**Step 1: Update user_profiles**
```sql
-- Replace 'your-email@example.com' with your actual email
UPDATE user_profiles 
SET firebase_uid = 'fLmNDKoCp1e0vQrOAs7bSYLSB8y1'
WHERE email = 'your-email@example.com';
```

**Step 2: Log out and log back in**
- This will sync your Firebase account with the database

### Option 3: Use the Diagnostic Script

I've created a Python script to help diagnose the issue:

```bash
cd backend
python fix_appointment_uids.py
```

This will show you:
- All appointments in the database
- All doctor UIDs in appointments
- All doctor profiles
- UID mismatches
- Suggested SQL to fix the issue

## Testing the Fix

### Test 1: Check Backend Logs
After restarting the backend, check the logs when you load the doctor schedule:
```
🔍 Querying appointments for doctor_firebase_uid: <your-uid>
✅ Found 4 appointments for doctor <your-uid>
```

### Test 2: Use the Diagnostic Endpoint
```bash
# Get your auth token first, then:
curl http://localhost:5000/api/appointments/diagnostic \
  -H "Authorization: Bearer YOUR_TOKEN"
```

This will show:
- Your current UID
- All UIDs in the appointments table
- Whether there's a match
- The actual query results

### Test 3: Check Frontend
1. Go to the doctor schedule page
2. You should see all 4 appointments
3. Patient names should be displayed

## Expected Results After Fix

✅ **Backend Logs:**
```
✅ Found 4 appointments for doctor <your-uid>
📤 Returning 4 appointments to frontend
✅ Enriched appointment <id> with patient: Name='<name>' Email='<email>'
```

✅ **Frontend:**
- All 4 appointments visible
- Patient names displayed correctly
- Appointment dates and times shown
- Video call links available

## If Still Not Working

### Check 1: Verify Service Client
```python
# In backend, check if service_client is initialized
from db.supabase_client import SupabaseClient
supabase = SupabaseClient()
print(f"Service client: {supabase.service_client is not None}")
```

### Check 2: Verify Environment Variables
Make sure `backend/.env` has:
```
SUPABASE_SERVICE_KEY=your-service-role-key
```

### Check 3: Check Backend Logs
Look for these messages:
- `🔍 Querying appointments for doctor_firebase_uid: <uid>`
- `🔍 Available doctor UIDs in appointments: [...]`
- `⚠️  Doctor UID <uid> does not match any appointments in database`

### Check 4: Direct Database Query
Run this in Supabase SQL Editor to verify:
```sql
-- Check all appointments
SELECT 
    id,
    doctor_firebase_uid,
    patient_firebase_uid,
    appointment_date,
    appointment_time,
    status
FROM appointments;

-- Check your user profile
SELECT 
    firebase_uid,
    email,
    role,
    first_name,
    last_name
FROM user_profiles
WHERE role = 'doctor';
```

## Common Issues

### Issue: "User profile not found"
**Solution:** Make sure your Firebase UID exists in the `user_profiles` table

### Issue: "Supabase service_client not initialized"
**Solution:** Check that `SUPABASE_SERVICE_KEY` is set in `backend/.env`

### Issue: "No appointments found" but appointments exist
**Solution:** This is the UID mismatch - use Option 1 or Option 2 above

## SQL Quick Reference

### Update All Appointments for a Doctor
```sql
UPDATE appointments 
SET doctor_firebase_uid = 'NEW_UID'
WHERE doctor_firebase_uid = 'OLD_UID';
```

### Check UID Mismatches
```sql
-- Find appointments with UIDs that don't match any user profile
SELECT DISTINCT a.doctor_firebase_uid
FROM appointments a
LEFT JOIN user_profiles u ON a.doctor_firebase_uid = u.firebase_uid
WHERE u.firebase_uid IS NULL;
```

### Find Your Current UID
```sql
-- Find your user profile by email
SELECT firebase_uid, email, role
FROM user_profiles
WHERE email = 'your-email@example.com';
```

---

**Quick Fix Date:** 2025-01-27
**Status:** ✅ Ready to use

**Next Steps:**
1. Run the diagnostic script: `python backend/fix_appointment_uids.py`
2. Update appointments table with correct UID (Option 1)
3. Restart backend server
4. Test the doctor schedule page


### Check 3: Check Backend Logs
Look for these messages:
- `🔍 Querying appointments for doctor_firebase_uid: <uid>`
- `🔍 Available doctor UIDs in appointments: [...]`
- `⚠️  Doctor UID <uid> does not match any appointments in database`

### Check 4: Direct Database Query
Run this in Supabase SQL Editor to verify:
```sql
-- Check all appointments
SELECT 
    id,
    doctor_firebase_uid,
    patient_firebase_uid,
    appointment_date,
    appointment_time,
    status
FROM appointments;

-- Check your user profile
SELECT 
    firebase_uid,
    email,
    role,
    first_name,
    last_name
FROM user_profiles
WHERE role = 'doctor';
```

## Common Issues

### Issue: "User profile not found"
**Solution:** Make sure your Firebase UID exists in the `user_profiles` table

### Issue: "Supabase service_client not initialized"
**Solution:** Check that `SUPABASE_SERVICE_KEY` is set in `backend/.env`

### Issue: "No appointments found" but appointments exist
**Solution:** This is the UID mismatch - use Option 1 or Option 2 above

## SQL Quick Reference

### Update All Appointments for a Doctor
```sql
UPDATE appointments 
SET doctor_firebase_uid = 'NEW_UID'
WHERE doctor_firebase_uid = 'OLD_UID';
```

### Check UID Mismatches
```sql
-- Find appointments with UIDs that don't match any user profile
SELECT DISTINCT a.doctor_firebase_uid
FROM appointments a
LEFT JOIN user_profiles u ON a.doctor_firebase_uid = u.firebase_uid
WHERE u.firebase_uid IS NULL;
```

### Find Your Current UID
```sql
-- Find your user profile by email
SELECT firebase_uid, email, role
FROM user_profiles
WHERE email = 'your-email@example.com';
```

---

**Quick Fix Date:** 2025-01-27
**Status:** ✅ Ready to use

**Next Steps:**
1. Run the diagnostic script: `python backend/fix_appointment_uids.py`
2. Update appointments table with correct UID (Option 1)
3. Restart backend server
4. Test the doctor schedule page

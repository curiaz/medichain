# Appointment Fetch Debugging Guide

## Issue
Appointments exist in the database but cannot be fetched from the backend.

## Root Causes (Most Likely)

### 1. **Firebase UID Mismatch** ⚠️ MOST LIKELY
The logged-in user's Firebase UID doesn't match the `doctor_firebase_uid` or `patient_firebase_uid` in the appointments table.

**From your screenshot:**
- All appointments have `doctor_firebase_uid`: `fLmNDKoCp1e0vQrOAs7bSYLSB8y1`
- If you're logged in with a different Firebase UID, the query will return empty results

**Solution:**
1. Check what Firebase UID you're logged in with
2. Verify it matches the `doctor_firebase_uid` in the appointments table
3. If it doesn't match, either:
   - Update the appointments table to use the correct UID
   - Log in with the Firebase account that matches the UID in the database

### 2. **Supabase Service Client Not Initialized**
The `SUPABASE_SERVICE_KEY` environment variable might be missing, causing RLS policies to block queries.

**Solution:**
1. Check `backend/.env` file
2. Ensure `SUPABASE_SERVICE_KEY` is set
3. Restart the backend server after adding it

### 3. **RLS Policies Blocking Queries**
Even with service_client, if RLS policies are misconfigured, queries might fail.

**Solution:**
1. Verify service_client is being used (it bypasses RLS)
2. Check RLS policies in Supabase dashboard
3. Ensure service role has proper permissions

## Debugging Steps

### Step 1: Use the Diagnostic Endpoint

I've added a diagnostic endpoint to help debug the issue:

```bash
# Make a GET request to the diagnostic endpoint
curl -X GET "http://localhost:5000/api/appointments/diagnostic" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Or test it in your browser console (if logged in):
```javascript
const token = localStorage.getItem('medichain_token') || await getFirebaseToken();
fetch('http://localhost:5000/api/appointments/diagnostic', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json()).then(console.log);
```

**This will show:**
- Your current Firebase UID
- Whether Supabase client is initialized
- Total appointments in the table
- All unique doctor UIDs in appointments
- All unique patient UIDs in appointments
- Whether your UID matches any appointments
- The actual query results

### Step 2: Check Backend Logs

The backend now has comprehensive logging. Check your server logs for:

```
🔍 GET /api/appointments: Request from user UID: <uid>
🔍 Querying appointments for doctor_firebase_uid: <uid>
🔍 Test query - Total appointments in table: 4
🔍 Available doctor UIDs in appointments: ['fLmNDKoCp1e0vQrOAs7bSYLSB8y1']
🔍 Requested doctor UID: <your-uid>
⚠️  Doctor UID <your-uid> does not match any appointments in database
```

### Step 3: Verify Firebase UID

1. **Check your logged-in UID:**
   - Open browser console
   - Check `localStorage.getItem('medichain_user')`
   - Look for `firebase_uid` or `uid` field

2. **Check database UIDs:**
   - Go to Supabase dashboard
   - Check `appointments` table
   - Compare `doctor_firebase_uid` values with your logged-in UID

### Step 4: Check Environment Variables

Verify these are set in `backend/.env`:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key  # ⚠️ CRITICAL
```

## Solutions

### Solution 1: Fix UID Mismatch (If you're the doctor)

If you're logged in as a different Firebase account than the one in the database:

**Option A: Update Appointments Table**
```sql
-- In Supabase SQL Editor
UPDATE appointments 
SET doctor_firebase_uid = 'YOUR_CURRENT_FIREBASE_UID'
WHERE doctor_firebase_uid = 'fLmNDKoCp1e0vQrOAs7bSYLSB8y1';
```

**Option B: Update User Profile**
```sql
-- Update your user profile to use the UID from appointments
UPDATE user_profiles 
SET firebase_uid = 'fLmNDKoCp1e0vQrOAs7bSYLSB8y1'
WHERE email = 'your-email@example.com';
```

**Option C: Log in with the Correct Account**
- Log out
- Log in with the Firebase account that has UID: `fLmNDKoCp1e0vQrOAs7bSYLSB8y1`

### Solution 2: Verify Service Client

Check if service_client is initialized:

```python
# In backend, add this temporarily to check
print(f"Service client available: {supabase.service_client is not None}")
print(f"Service key set: {bool(os.getenv('SUPABASE_SERVICE_KEY'))}")
```

### Solution 3: Test Direct Query

Test if you can query appointments directly:

```python
# In Python console or temporary endpoint
from db.supabase_client import SupabaseClient
supabase = SupabaseClient()

# Test query
result = supabase.service_client.table("appointments").select("*").execute()
print(f"Total appointments: {len(result.data)}")
print(f"Sample: {result.data[0] if result.data else 'None'}")
```

## Quick Fix Script

If you want to quickly update all appointments to use your current UID:

```sql
-- ⚠️ WARNING: This will update ALL appointments to use your UID
-- Only run this if you're sure you want to do this!

-- First, get your current Firebase UID from the diagnostic endpoint
-- Then run:

UPDATE appointments 
SET doctor_firebase_uid = 'YOUR_CURRENT_FIREBASE_UID'
WHERE doctor_firebase_uid = 'fLmNDKoCp1e0vQrOAs7bSYLSB8y1';
```

## Expected Behavior After Fix

After fixing the UID mismatch, you should see:

1. **Backend Logs:**
```
✅ Found 4 appointments for doctor <your-uid>
📤 Returning 4 appointments to frontend
```

2. **Frontend:**
- Appointments appear in the doctor schedule
- Patient names are displayed
- All appointment details are visible

## Testing

1. **Test the diagnostic endpoint:**
   ```bash
   curl http://localhost:5000/api/appointments/diagnostic \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

2. **Test the appointments endpoint:**
   ```bash
   curl http://localhost:5000/api/appointments \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

3. **Check browser console:**
   - Open DevTools
   - Check Network tab
   - Look at the `/api/appointments` request
   - Verify the response contains appointments

## Additional Debugging

If the issue persists, check:

1. **Database Connection:**
   - Can you query other tables?
   - Are there any connection errors in logs?

2. **Authentication:**
   - Is the token valid?
   - Does the user profile exist?
   - Is the role correctly set?

3. **RLS Policies:**
   - Check Supabase dashboard → Authentication → Policies
   - Verify service role can bypass RLS

## Contact

If you're still having issues after trying these steps:
1. Run the diagnostic endpoint and share the output
2. Share the backend logs
3. Verify your Firebase UID matches the database

---

**Last Updated:** 2025-01-27
**Status:** ✅ Enhanced with diagnostic tools and comprehensive logging


## Issue
Appointments exist in the database but cannot be fetched from the backend.

## Root Causes (Most Likely)

### 1. **Firebase UID Mismatch** ⚠️ MOST LIKELY
The logged-in user's Firebase UID doesn't match the `doctor_firebase_uid` or `patient_firebase_uid` in the appointments table.

**From your screenshot:**
- All appointments have `doctor_firebase_uid`: `fLmNDKoCp1e0vQrOAs7bSYLSB8y1`
- If you're logged in with a different Firebase UID, the query will return empty results

**Solution:**
1. Check what Firebase UID you're logged in with
2. Verify it matches the `doctor_firebase_uid` in the appointments table
3. If it doesn't match, either:
   - Update the appointments table to use the correct UID
   - Log in with the Firebase account that matches the UID in the database

### 2. **Supabase Service Client Not Initialized**
The `SUPABASE_SERVICE_KEY` environment variable might be missing, causing RLS policies to block queries.

**Solution:**
1. Check `backend/.env` file
2. Ensure `SUPABASE_SERVICE_KEY` is set
3. Restart the backend server after adding it

### 3. **RLS Policies Blocking Queries**
Even with service_client, if RLS policies are misconfigured, queries might fail.

**Solution:**
1. Verify service_client is being used (it bypasses RLS)
2. Check RLS policies in Supabase dashboard
3. Ensure service role has proper permissions

## Debugging Steps

### Step 1: Use the Diagnostic Endpoint

I've added a diagnostic endpoint to help debug the issue:

```bash
# Make a GET request to the diagnostic endpoint
curl -X GET "http://localhost:5000/api/appointments/diagnostic" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Or test it in your browser console (if logged in):
```javascript
const token = localStorage.getItem('medichain_token') || await getFirebaseToken();
fetch('http://localhost:5000/api/appointments/diagnostic', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json()).then(console.log);
```

**This will show:**
- Your current Firebase UID
- Whether Supabase client is initialized
- Total appointments in the table
- All unique doctor UIDs in appointments
- All unique patient UIDs in appointments
- Whether your UID matches any appointments
- The actual query results

### Step 2: Check Backend Logs

The backend now has comprehensive logging. Check your server logs for:

```
🔍 GET /api/appointments: Request from user UID: <uid>
🔍 Querying appointments for doctor_firebase_uid: <uid>
🔍 Test query - Total appointments in table: 4
🔍 Available doctor UIDs in appointments: ['fLmNDKoCp1e0vQrOAs7bSYLSB8y1']
🔍 Requested doctor UID: <your-uid>
⚠️  Doctor UID <your-uid> does not match any appointments in database
```

### Step 3: Verify Firebase UID

1. **Check your logged-in UID:**
   - Open browser console
   - Check `localStorage.getItem('medichain_user')`
   - Look for `firebase_uid` or `uid` field

2. **Check database UIDs:**
   - Go to Supabase dashboard
   - Check `appointments` table
   - Compare `doctor_firebase_uid` values with your logged-in UID

### Step 4: Check Environment Variables

Verify these are set in `backend/.env`:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key  # ⚠️ CRITICAL
```

## Solutions

### Solution 1: Fix UID Mismatch (If you're the doctor)

If you're logged in as a different Firebase account than the one in the database:

**Option A: Update Appointments Table**
```sql
-- In Supabase SQL Editor
UPDATE appointments 
SET doctor_firebase_uid = 'YOUR_CURRENT_FIREBASE_UID'
WHERE doctor_firebase_uid = 'fLmNDKoCp1e0vQrOAs7bSYLSB8y1';
```

**Option B: Update User Profile**
```sql
-- Update your user profile to use the UID from appointments
UPDATE user_profiles 
SET firebase_uid = 'fLmNDKoCp1e0vQrOAs7bSYLSB8y1'
WHERE email = 'your-email@example.com';
```

**Option C: Log in with the Correct Account**
- Log out
- Log in with the Firebase account that has UID: `fLmNDKoCp1e0vQrOAs7bSYLSB8y1`

### Solution 2: Verify Service Client

Check if service_client is initialized:

```python
# In backend, add this temporarily to check
print(f"Service client available: {supabase.service_client is not None}")
print(f"Service key set: {bool(os.getenv('SUPABASE_SERVICE_KEY'))}")
```

### Solution 3: Test Direct Query

Test if you can query appointments directly:

```python
# In Python console or temporary endpoint
from db.supabase_client import SupabaseClient
supabase = SupabaseClient()

# Test query
result = supabase.service_client.table("appointments").select("*").execute()
print(f"Total appointments: {len(result.data)}")
print(f"Sample: {result.data[0] if result.data else 'None'}")
```

## Quick Fix Script

If you want to quickly update all appointments to use your current UID:

```sql
-- ⚠️ WARNING: This will update ALL appointments to use your UID
-- Only run this if you're sure you want to do this!

-- First, get your current Firebase UID from the diagnostic endpoint
-- Then run:

UPDATE appointments 
SET doctor_firebase_uid = 'YOUR_CURRENT_FIREBASE_UID'
WHERE doctor_firebase_uid = 'fLmNDKoCp1e0vQrOAs7bSYLSB8y1';
```

## Expected Behavior After Fix

After fixing the UID mismatch, you should see:

1. **Backend Logs:**
```
✅ Found 4 appointments for doctor <your-uid>
📤 Returning 4 appointments to frontend
```

2. **Frontend:**
- Appointments appear in the doctor schedule
- Patient names are displayed
- All appointment details are visible

## Testing

1. **Test the diagnostic endpoint:**
   ```bash
   curl http://localhost:5000/api/appointments/diagnostic \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

2. **Test the appointments endpoint:**
   ```bash
   curl http://localhost:5000/api/appointments \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

3. **Check browser console:**
   - Open DevTools
   - Check Network tab
   - Look at the `/api/appointments` request
   - Verify the response contains appointments

## Additional Debugging

If the issue persists, check:

1. **Database Connection:**
   - Can you query other tables?
   - Are there any connection errors in logs?

2. **Authentication:**
   - Is the token valid?
   - Does the user profile exist?
   - Is the role correctly set?

3. **RLS Policies:**
   - Check Supabase dashboard → Authentication → Policies
   - Verify service role can bypass RLS

## Contact

If you're still having issues after trying these steps:
1. Run the diagnostic endpoint and share the output
2. Share the backend logs
3. Verify your Firebase UID matches the database

---

**Last Updated:** 2025-01-27
**Status:** ✅ Enhanced with diagnostic tools and comprehensive logging


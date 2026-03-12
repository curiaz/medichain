# 🚨 QUICK FIX: Appointments Not Fetching

## The Problem
Your appointments exist in the database but aren't showing because your **Firebase UID doesn't match** the `doctor_firebase_uid` in the appointments table.

## ✅ Solution (3 Steps)

### Step 1: Get Your Current Firebase UID

**Option A: Use the new API endpoint**
```bash
# Make sure backend is running, then:
curl http://localhost:5000/api/appointments/my-uid \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Option B: Check browser console**
1. Open browser console (F12)
2. Go to Application/Storage → Local Storage
3. Look for `medichain_user` or check console for logged UID

**Option C: Check backend logs**
When you load the doctor schedule page, look for:
```
🔍 GET /api/appointments: Request from user UID: <YOUR_UID>
```

### Step 2: Update Appointments Table

Run this SQL in **Supabase SQL Editor**:

```sql
-- Replace 'YOUR_CURRENT_UID' with the UID from Step 1
-- Replace 'fLmNDKoCp1e0vQrOAs7bSYLSB8y1' with the OLD UID (from your screenshot)

UPDATE appointments 
SET doctor_firebase_uid = 'YOUR_CURRENT_UID'
WHERE doctor_firebase_uid = 'fLmNDKoCp1e0vQrOAs7bSYLSB8y1';
```

### Step 3: Verify and Test

```sql
-- Check that appointments are updated
SELECT id, doctor_firebase_uid, appointment_date, appointment_time 
FROM appointments;
```

Then refresh the doctor schedule page - you should see all 4 appointments!

---

## 🔍 How to Debug

### Check Backend Logs
When you load the doctor schedule, you should see:
```
🔍 Querying appointments for doctor_firebase_uid: <YOUR_UID>
🔍 Test query - Total appointments in table: 4
🔍 Appointments matching doctor UID <YOUR_UID>: 0  ← This is the problem!
```

If you see `0` matching appointments, that's the UID mismatch.

### Use Diagnostic Endpoint
```bash
curl http://localhost:5000/api/appointments/diagnostic \
  -H "Authorization: Bearer YOUR_TOKEN"
```

This will show:
- Your current UID
- All UIDs in appointments table
- Whether there's a match

---

## 📝 Example SQL Commands

### Find All Doctor UIDs in Appointments
```sql
SELECT DISTINCT doctor_firebase_uid, COUNT(*) as appointment_count
FROM appointments
GROUP BY doctor_firebase_uid;
```

### Find Your User Profile
```sql
SELECT firebase_uid, email, role, first_name, last_name
FROM user_profiles
WHERE role = 'doctor';
```

### Update All Appointments (if needed)
```sql
-- Update appointments to match your current UID
UPDATE appointments 
SET doctor_firebase_uid = 'YOUR_NEW_UID'
WHERE doctor_firebase_uid = 'OLD_UID';
```

---

## ✅ Expected Result After Fix

**Backend Logs:**
```
✅ Found 4 appointments for doctor <YOUR_UID>
📤 Returning 4 appointments to frontend
```

**Frontend:**
- All 4 appointments visible
- Patient names displayed
- Dates and times shown correctly

---

**Status:** Ready to fix! Just follow the 3 steps above.


## The Problem
Your appointments exist in the database but aren't showing because your **Firebase UID doesn't match** the `doctor_firebase_uid` in the appointments table.

## ✅ Solution (3 Steps)

### Step 1: Get Your Current Firebase UID

**Option A: Use the new API endpoint**
```bash
# Make sure backend is running, then:
curl http://localhost:5000/api/appointments/my-uid \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Option B: Check browser console**
1. Open browser console (F12)
2. Go to Application/Storage → Local Storage
3. Look for `medichain_user` or check console for logged UID

**Option C: Check backend logs**
When you load the doctor schedule page, look for:
```
🔍 GET /api/appointments: Request from user UID: <YOUR_UID>
```

### Step 2: Update Appointments Table

Run this SQL in **Supabase SQL Editor**:

```sql
-- Replace 'YOUR_CURRENT_UID' with the UID from Step 1
-- Replace 'fLmNDKoCp1e0vQrOAs7bSYLSB8y1' with the OLD UID (from your screenshot)

UPDATE appointments 
SET doctor_firebase_uid = 'YOUR_CURRENT_UID'
WHERE doctor_firebase_uid = 'fLmNDKoCp1e0vQrOAs7bSYLSB8y1';
```

### Step 3: Verify and Test

```sql
-- Check that appointments are updated
SELECT id, doctor_firebase_uid, appointment_date, appointment_time 
FROM appointments;
```

Then refresh the doctor schedule page - you should see all 4 appointments!

---

## 🔍 How to Debug

### Check Backend Logs
When you load the doctor schedule, you should see:
```
🔍 Querying appointments for doctor_firebase_uid: <YOUR_UID>
🔍 Test query - Total appointments in table: 4
🔍 Appointments matching doctor UID <YOUR_UID>: 0  ← This is the problem!
```

If you see `0` matching appointments, that's the UID mismatch.

### Use Diagnostic Endpoint
```bash
curl http://localhost:5000/api/appointments/diagnostic \
  -H "Authorization: Bearer YOUR_TOKEN"
```

This will show:
- Your current UID
- All UIDs in appointments table
- Whether there's a match

---

## 📝 Example SQL Commands

### Find All Doctor UIDs in Appointments
```sql
SELECT DISTINCT doctor_firebase_uid, COUNT(*) as appointment_count
FROM appointments
GROUP BY doctor_firebase_uid;
```

### Find Your User Profile
```sql
SELECT firebase_uid, email, role, first_name, last_name
FROM user_profiles
WHERE role = 'doctor';
```

### Update All Appointments (if needed)
```sql
-- Update appointments to match your current UID
UPDATE appointments 
SET doctor_firebase_uid = 'YOUR_NEW_UID'
WHERE doctor_firebase_uid = 'OLD_UID';
```

---

## ✅ Expected Result After Fix

**Backend Logs:**
```
✅ Found 4 appointments for doctor <YOUR_UID>
📤 Returning 4 appointments to frontend
```

**Frontend:**
- All 4 appointments visible
- Patient names displayed
- Dates and times shown correctly

---

**Status:** Ready to fix! Just follow the 3 steps above.


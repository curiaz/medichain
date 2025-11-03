# 📧 Email Notification Fix for Doctor Signup

## ✅ Email System Test Result
**Status**: Email configuration is **WORKING!** ✅

I just sent you a test email to verify the configuration.

---

## 🔍 Issue Found

The `doctor_profiles` table is **missing columns** needed for the verification token system:
- `verification_token`
- `token_expires_at`
- `verified_at`
- `declined_at`

**This is why the email isn't being sent** - the database update is failing silently.

---

## ✅ Solution: Run This SQL Migration

### **Step 1: Open Supabase SQL Editor**
1. Go to: https://supabase.com/dashboard
2. Select your MediChain project
3. Click **"SQL Editor"** in left sidebar
4. Click **"New Query"**

### **Step 2: Run This SQL**

```sql
-- Add verification token columns to doctor_profiles

ALTER TABLE doctor_profiles 
ADD COLUMN IF NOT EXISTS verification_token VARCHAR(255);

ALTER TABLE doctor_profiles 
ADD COLUMN IF NOT EXISTS token_expires_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE doctor_profiles 
ADD COLUMN IF NOT EXISTS verified_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE doctor_profiles 
ADD COLUMN IF NOT EXISTS declined_at TIMESTAMP WITH TIME ZONE;

-- Add index for faster lookups
CREATE INDEX IF NOT EXISTS idx_doctor_profiles_verification_token 
ON doctor_profiles(verification_token);
```

### **Step 3: Click "Run"**
You should see: **"Success. No rows returned"** ✅

---

## 🧪 Test Again

### **Step 1: Restart Backend**
```powershell
# Stop backend (Ctrl+C if running)
cd medichain\backend
python app.py
```

### **Step 2: Sign Up as Doctor**
1. Go to: http://localhost:3000/signup?role=doctor
2. Fill in all fields
3. Upload a document
4. Click "Create Account"

### **Step 3: Expected Backend Logs**
```
[DEBUG] 🏥 Doctor signup request received
[DEBUG] ✅ Firebase user created: doctor@example.com
[DEBUG] ✅ Verification file saved: abc123_...jpg
[DEBUG] ✅ User profile created: doctor@example.com
[DEBUG] ✅ Doctor profile created: doctor@example.com
[DEBUG] ✅ Admin notification email sent for doctor verification  ← SHOULD SEE THIS!
201 Created
```

### **Step 4: Check Your Email**
**To**: `medichain173@gmail.com`

You should receive:
📧 **Subject**: "Doctor Verification Request - Dr. [Name]"

Email will have:
- ✅ **APPROVE DOCTOR** button (green)
- ❌ **DECLINE APPLICATION** button (red)  
- 📎 Attached verification document

---

## 🔍 If Still No Email

### **Check Backend Logs**
Look for these messages:

✅ **Good**:
```
[DEBUG] ✅ Admin notification email sent for doctor verification
```

❌ **Problem**:
```
[DEBUG] ⚠️  Failed to send admin notification email
[DEBUG] ⚠️  Email notification error: ...
```

### **Common Issues**

| Issue | Solution |
|---|---|
| "Failed to send email" | Check `.env` has `ADMIN_EMAIL_PASSWORD` |
| "Column doesn't exist" | Run the SQL migration above |
| No log message at all | Backend might have crashed - check terminal |
| Gmail blocked | Check Gmail "Less secure app access" or use App Password |

---

## 📊 Verify Database After Migration

Run this SQL to check if columns exist:

```sql
SELECT 
  column_name, 
  data_type, 
  is_nullable
FROM information_schema.columns
WHERE table_name = 'doctor_profiles'
  AND column_name IN (
    'verification_token', 
    'token_expires_at', 
    'verified_at', 
    'declined_at'
  )
ORDER BY column_name;
```

**Expected Output**:
| column_name | data_type | is_nullable |
|---|---|---|
| declined_at | timestamp with time zone | YES |
| token_expires_at | timestamp with time zone | YES |
| verification_token | character varying | YES |
| verified_at | timestamp with time zone | YES |

---

## 🎯 Quick Checklist

- [ ] Run SQL migration in Supabase
- [ ] Verify columns exist (run verification query)
- [ ] Restart backend
- [ ] Sign up as doctor
- [ ] Check backend logs for "Admin notification email sent"
- [ ] Check email inbox for notification

---

## 📝 Summary

**Root Cause**: Missing database columns  
**Fix**: Run SQL migration  
**Test**: Sign up again after migration  
**Expected**: Email with APPROVE/DECLINE buttons

---

**Status**: Ready to fix!  
**Next Step**: Run the SQL migration above, then test signup again.


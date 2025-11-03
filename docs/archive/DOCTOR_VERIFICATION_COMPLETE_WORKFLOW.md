# 🔄 Doctor Verification Workflow - Complete Implementation

## Overview

Implemented a complete doctor verification workflow where:
1. ✅ Doctor creates account → OTP sent to email
2. ✅ Doctor verifies email with OTP → Admin verification email sent automatically  
3. ✅ Doctor can access dashboard with pending/approved/declined status
4. ✅ Access control blocks pending/declined doctors from system

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ 1. DOCTOR SIGNUP                                            │
├─────────────────────────────────────────────────────────────┤
│ Doctor fills form:                                          │
│  - Email, Password, Name                                    │
│  - Specialization                                           │
│  - Verification Document (PDF/JPG/PNG)                      │
│                                                              │
│ POST /api/auth/doctor-signup                                │
│  ↓                                                           │
│  - Creates Firebase account                                 │
│  - Saves to user_profiles (verification_status: 'pending')  │
│  - Saves to doctor_profiles                                 │
│  - Sends OTP to doctor's email                              │
│  - Does NOT send admin email yet ❗                         │
│                                                              │
│ Response: "Please verify your email with OTP sent to inbox" │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. EMAIL OTP VERIFICATION                                   │
├─────────────────────────────────────────────────────────────┤
│ Doctor receives email with 6-digit OTP                      │
│ Enters OTP in verification form                             │
│                                                              │
│ POST /api/auth/verify-otp (for password reset flow)         │
│ OR                                                           │
│ POST /api/auth/send-verification-after-email-confirmation   │
│  ↓                                                           │
│  - Verifies OTP is correct                                  │
│  - Checks if user is a doctor                               │
│  - Sends admin verification email NOW ✅                    │
│  - Updates last_verification_request_sent timestamp         │
│                                                              │
│ Response: "Email verified! Admin notified."                 │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. ADMIN RECEIVES VERIFICATION EMAIL                        │
├─────────────────────────────────────────────────────────────┤
│ Admin email: testmedichain1@gmail.com                       │
│                                                              │
│ Email contains:                                              │
│  - Doctor name, email, specialization                       │
│  - Verification document attachment                          │
│  - [APPROVE DOCTOR] button                                   │
│  - [DECLINE APPLICATION] button                              │
│                                                              │
│ Admin clicks button → Token-based URL                        │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. ADMIN APPROVES/DECLINES                                  │
├─────────────────────────────────────────────────────────────┤
│ GET /api/auth/approve-doctor?token=xxx&doctor_id=xxx        │
│  ↓                                                           │
│  - Updates verification_status to 'approved'                │
│  - Sends notification email to doctor                       │
│                                                              │
│ OR                                                           │
│                                                              │
│ GET /api/auth/decline-doctor?token=xxx&doctor_id=xxx        │
│  ↓                                                           │
│  - Updates verification_status to 'declined'                │
│  - Sends notification email to doctor                       │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. DOCTOR ACCESSES DASHBOARD                                │
├─────────────────────────────────────────────────────────────┤
│ Doctor can login at ANY time (even while pending)           │
│                                                              │
│ On dashboard load:                                           │
│  - Fetches verification_status from database                │
│  - Shows VerificationStatus component                       │
│                                                              │
│ If status = 'pending':                                       │
│  🕐 "Verification Pending" card stays visible               │
│  ✉️ Shows "Request Verification Review" button              │
│  📊 Shows cooldown timer (24hr limit)                       │
│                                                              │
│ If status = 'approved':                                      │
│  ✅ "Verified Doctor" card appears                          │
│  ⏱️  Auto-hides after 4 seconds with fade animation        │
│  🎉 Full system access granted                              │
│                                                              │
│ If status = 'declined':                                      │
│  ❌ "Verification Declined" card stays visible              │
│  📞 Shows "Contact Support" button                          │
│  🚫 API calls return 403 errors (access denied)             │
└─────────────────────────────────────────────────────────────┘
```

## Backend Changes

### 1. `backend/doctor_verification.py`

#### Modified `doctor_signup()` endpoint:
```python
# BEFORE: Sent admin email immediately
email_sent = send_admin_notification_email(doctor_data, file_path, doctor_id, verification_token)

# AFTER: Send OTP instead, admin email comes after verification
from services.simple_otp_manager import simple_otp_manager
otp_result = simple_otp_manager.send_otp(email)

return jsonify({
    "message": "Doctor account created! Please verify your email with the OTP sent to your inbox.",
    "requires_email_verification": True,
    "otp_sent": otp_result["success"]
})
```

#### New endpoint `/send-verification-after-email-confirmation`:
```python
@doctor_verification_bp.route("/send-verification-after-email-confirmation", methods=["POST"])
def send_verification_after_email_confirmation():
    """
    Send doctor verification request to admin after email OTP is verified
    This is called automatically after email verification is complete
    """
    # Get firebase_uid from request
    # Check if doctor profile exists
    # Check if email was already sent (prevent duplicates)
    # Send admin notification email
    # Update last_verification_request_sent timestamp
```

#### Modified `submit_doctor_verification()` endpoint:
```python
# BEFORE: Sent admin email immediately
email_sent = send_admin_notification_email(...)

# AFTER: Admin email sent after OTP verification
return jsonify({
    "message": "Doctor profile created successfully! Please verify your email to complete registration.",
    "requires_email_verification": True
})
```

### 2. `backend/auth/auth_routes.py`

#### Modified `verify-otp()` endpoint:
Added logic to automatically send doctor verification email after OTP is verified:

```python
if verification_result["success"]:
    # Check if this is a doctor account
    user_check = supabase.table("user_profiles").select("*").eq("email", email).execute()
    if user_check.data and user_check.data[0].get("role") == "doctor":
        # Send doctor verification email to admin
        email_sent = send_admin_notification_email(...)
        # Update timestamp to prevent duplicates
        supabase.table("doctor_profiles").update({
            "last_verification_request_sent": datetime.utcnow().isoformat()
        }).eq("firebase_uid", firebase_uid).execute()
```

### 3. `backend/auth/firebase_auth.py`

#### Enhanced `@firebase_auth_required` decorator:
```python
# Check if user is a doctor and verify their approval status
if user_role == "doctor":
    if verification_status == "declined":
        return jsonify({
            "error": "Access denied",
            "message": "Your doctor verification has been declined. Please contact support.",
            "verification_status": "declined"
        }), 403
    elif verification_status == "pending":
        return jsonify({
            "error": "Access denied", 
            "message": "Your account is pending verification. You'll receive an email once approved.",
            "verification_status": "pending"
        }), 403
```

## Frontend Changes

### Current State
The frontend currently calls `/api/auth/doctor-signup` which now returns:
```json
{
  "success": true,
  "message": "Doctor account created! Please verify your email with the OTP sent to your inbox.",
  "requires_email_verification": true,
  "otp_sent": true
}
```

### Required Frontend Updates

The frontend needs to:
1. ✅ Show OTP verification modal after doctor signup
2. ✅ Call OTP verification endpoint with the OTP code
3. ✅ Admin email will be sent automatically after OTP verification (backend handles this)
4. ✅ Redirect to dashboard after successful verification

**Note**: If the frontend already has OTP verification flow for password reset, it can be reused here. The backend now automatically detects if it's a doctor account and sends the verification email after OTP is confirmed.

## Database Schema

### `user_profiles` table:
- `verification_status`: 'pending' | 'approved' | 'declined'
- Set to 'pending' on doctor signup
- Updated by admin through email links

### `doctor_profiles` table:
- `last_verification_request_sent`: TIMESTAMPTZ
- Prevents duplicate verification emails
- Updated when admin email is sent

## Email Flow

### 1. Doctor Signup Email (OTP):
**To**: Doctor's email  
**Subject**: "MediChain - Verify Your Email"  
**Content**:
- 6-digit OTP code
- Expires in 5 minutes
- Use to verify account

### 2. Admin Verification Email:
**To**: testmedichain1@gmail.com  
**Subject**: "MediChain Doctor Verification"  
**Content**:
- Doctor details (name, email, specialization)
- Verification document attachment
- [APPROVE DOCTOR] button → Approve endpoint
- [DECLINE APPLICATION] button → Decline endpoint
- Token expires in 24 hours

### 3. Doctor Notification Email (After Admin Decision):
**To**: Doctor's email  
**Subject**: "MediChain - Verification Status Update"  
**Content**:
- Approval: "Congratulations! Your account has been verified."
- Decline: "Your verification was not approved. Please contact support."

## Access Control Matrix

| Verification Status | Can Login? | Can Access Dashboard? | What Happens?                     |
|---------------------|------------|-----------------------|-----------------------------------|
| **Pending**         | ✅ Yes     | ⚠️ Limited            | Shows "Pending" card, can view but limited API access |
| **Approved**        | ✅ Yes     | ✅ Full               | Auto-hide card, full system access |
| **Declined**        | ✅ Yes     | ❌ Blocked            | Shows "Declined" card, 403 errors on API calls |

**Important**: Doctors can login with any status, but API calls check `verification_status` and return 403 for pending/declined.

## Testing Instructions

### Test Complete Flow:

1. **Doctor Signup**:
```bash
# Use frontend or Postman
POST http://localhost:5000/api/auth/doctor-signup
Form Data:
  - email: test@example.com
  - password: Test123!
  - firstName: John
  - lastName: Doe
  - specialization: Cardiology
  - verificationFile: [PDF/JPG/PNG file]

Expected: "Please verify your email with OTP"
```

2. **Check Email for OTP**:
- Check test@example.com inbox
- Find 6-digit OTP code

3. **Verify OTP**:
```bash
POST http://localhost:5000/api/auth/verify-otp
{
  "email": "test@example.com",
  "otp": "123456"
}

Expected: "Verification code validated!"
Backend automatically sends admin email ✅
```

4. **Check Admin Email**:
- Check testmedichain1@gmail.com inbox
- Find "MediChain Doctor Verification" email
- Has APPROVE/DECLINE buttons

5. **Login to Dashboard**:
```bash
# Doctor can login now (even while pending)
POST http://localhost:3001/login
{
  "email": "test@example.com",
  "password": "Test123!"
}

Expected: Dashboard loads with "Verification Pending" card
```

6. **Admin Approves**:
- Click [APPROVE DOCTOR] button in email
- Or use helper script: `python approve_doctor.py`

7. **Doctor Sees Approved Status**:
- Refresh dashboard
- "Verified Doctor" card appears
- Card auto-hides after 4 seconds ✨
- Full system access granted

## Helper Scripts

### Approve Doctor:
```bash
python approve_doctor.py
# Sets status to 'approved'
```

### Reset to Pending:
```bash
python reset_to_pending.py
# Sets status to 'pending'
```

### Check Status:
```bash
python check_doctor_status.py
# Shows current verification_status
```

### Test Access Control:
```bash
python test_access_control.py
# Interactive menu to test different scenarios
```

## Files Modified

### Backend:
1. ✅ `backend/doctor_verification.py`
   - Modified `doctor_signup()` - Send OTP instead of admin email
   - Modified `submit_doctor_verification()` - Delay admin email
   - Added `send_verification_after_email_confirmation()` - New endpoint

2. ✅ `backend/auth/auth_routes.py`
   - Modified `verify-otp()` - Auto-send doctor verification email

3. ✅ `backend/auth/firebase_auth.py`
   - Enhanced `@firebase_auth_required` - Check verification status

### Frontend:
4. ⚠️ `src/frontend/MedichainSignup.jsx`
   - Already handles doctor signup
   - May need OTP verification flow (check if exists)

5. ✅ `src/components/VerificationStatus.jsx`
   - Already shows verification status
   - Already has auto-hide for approved status

6. ✅ `src/config/axios.js`
   - Already handles 403 errors
   - Shows alerts and logs out

## Current Status

### ✅ Completed:
- Backend workflow fully implemented
- OTP sent on doctor signup
- Admin email sent after OTP verification
- Access control for pending/declined doctors
- Auto-hide verification card for approved doctors
- Helper scripts for testing

### ⚠️ Needs Frontend Update:
- Verify OTP verification flow exists in signup
- May need to add OTP input modal after doctor signup
- Should call `/api/auth/verify-otp` after OTP is entered
- Backend handles the rest automatically

### 🧪 Ready to Test:
System is ready for testing! The backend automatically handles:
1. Send OTP on signup ✅
2. Send admin email after OTP verification ✅
3. Block access for pending/declined doctors ✅
4. Auto-hide approved verification card ✅

## Next Steps

1. **Test doctor signup flow**:
   - Create doctor account
   - Check if OTP email arrives
   - Verify if OTP verification flow exists in frontend

2. **If OTP verification missing**:
   - Add OTP input modal to signup flow
   - Call `/api/auth/verify-otp` endpoint
   - Redirect to dashboard after verification

3. **Test admin approval**:
   - Check admin email inbox
   - Click approve button
   - Verify doctor can access system

4. **Test access control**:
   - Try accessing dashboard while pending
   - Verify 403 errors and auto-logout
   - Test approved access and auto-hide card

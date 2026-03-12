# Doctor Verification Resend Feature

## Overview
This feature allows doctors with pending verification status to resend their verification request to the admin email. It includes a 24-hour cooldown period to prevent spam.

## Implementation Summary

### 🗄️ Database Changes
**File**: `database/add_verification_request_timestamp.sql`

Added column to track verification request timestamps:
- **Column**: `last_verification_request_sent` (TIMESTAMPTZ)
- **Purpose**: Store when the last verification request email was sent
- **Default**: NULL
- **Index**: Created for efficient querying

**To apply the migration:**
```sql
-- Run this in Supabase SQL Editor
-- File: database/add_verification_request_timestamp.sql
```

### 🔧 Backend API Routes
**File**: `backend/doctor_verification.py`

#### 1. POST `/api/auth/resend-verification-request`
Resends the verification request email to admin.

**Request Body:**
```json
{
  "firebase_uid": "user_firebase_uid"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Verification request has been resent to admin...",
  "email_sent": true,
  "next_request_available": "2025-10-22T12:00:00Z"
}
```

**Cooldown Active Response (429):**
```json
{
  "success": false,
  "error": "Cooldown period active",
  "message": "You can request verification again in 12.5 hours",
  "hours_remaining": 12.5,
  "can_resend": false
}
```

**Error Response (400/404/500):**
```json
{
  "success": false,
  "error": "Error message"
}
```

**Features:**
- ✅ Validates doctor profile exists
- ✅ Checks if account is already approved
- ✅ Enforces 24-hour cooldown period
- ✅ Generates new verification token
- ✅ Updates timestamp in database
- ✅ Sends email to admin with verification link
- ✅ Returns next available request time

#### 2. GET `/api/auth/verification-status?firebase_uid={uid}`
Gets verification status and cooldown information.

**Success Response (200):**
```json
{
  "success": true,
  "can_resend": false,
  "hours_remaining": 8.3,
  "last_request_sent": "2025-10-21T04:00:00Z",
  "next_available_time": "2025-10-22T04:00:00Z"
}
```

**Features:**
- ✅ Returns whether doctor can resend
- ✅ Calculates hours remaining in cooldown
- ✅ Shows when last request was sent
- ✅ Shows when next request is available

### 🎨 Frontend UI Changes
**File**: `src/components/VerificationStatus.jsx`

**New Features:**
- ✅ "Request Verification Review" button in pending verification section
- ✅ Real-time cooldown timer display
- ✅ Automatic status updates every minute
- ✅ Success/error message display
- ✅ Loading state during request
- ✅ Disabled state when cooldown active
- ✅ Last request timestamp display

**Visual States:**
1. **Can Resend**: Blue button with "Request Verification Review"
2. **Cooldown Active**: Gray disabled button with "Available in X hours"
3. **Sending**: Spinning icon with "Sending..."
4. **Success**: Green success message banner
5. **Error**: Red error message banner

**File**: `src/components/VerificationStatus.css`

**New Styles:**
- `.resend-verification-btn` - Main button styling with gradient
- `.resend-verification-btn.disabled` - Gray disabled state
- `.spinning` - Rotation animation for loading icon
- `.cooldown-note` - Italic note about 24-hour cooldown
- `.verification-message-alert` - Success/error message banners

### 📋 User Flow

#### Doctor's Perspective:
1. Doctor signs up and submits verification
2. Dashboard shows "Verification Pending" status
3. Doctor sees "Request Verification Review" button
4. Doctor clicks button → Email sent to admin
5. Button becomes disabled showing "Available in 24 hours"
6. Success message: "Verification request resent successfully!"
7. Timer counts down until next request available
8. After 24 hours, button becomes active again

#### Admin's Perspective:
1. Receives email with doctor details
2. Reviews attached verification document
3. Clicks "APPROVE DOCTOR" or "DECLINE APPLICATION"
4. Doctor receives email notification of decision

### 🔒 Security Features

1. **24-Hour Cooldown**: Prevents spam by limiting requests to once per 24 hours
2. **Firebase Authentication**: All API calls require valid Firebase auth token
3. **Validation**: 
   - Checks if user exists
   - Checks if user is a doctor
   - Checks if already approved
   - Validates cooldown period
4. **Service Client**: Uses Supabase service role to bypass RLS for admin operations
5. **New Token Generation**: Each resend creates a new unique verification token

### ⚙️ Configuration

**Environment Variables Needed:**
```bash
ADMIN_EMAIL=medichain173@gmail.com
ADMIN_EMAIL_PASSWORD=your_app_password
ADMIN_NOTIFICATION_EMAIL=medichain173@gmail.com
BASE_URL=http://localhost:5000
```

### 🧪 Testing Checklist

- [ ] Run database migration in Supabase
- [ ] Restart backend server
- [ ] Login as doctor with pending status
- [ ] Test initial verification status fetch
- [ ] Click "Request Verification Review" button
- [ ] Verify success message appears
- [ ] Verify button becomes disabled with countdown
- [ ] Verify admin receives email
- [ ] Check database for updated `last_verification_request_sent`
- [ ] Wait 1 minute and verify countdown updates
- [ ] Try clicking disabled button (should not work)
- [ ] Test error handling (network errors, etc.)
- [ ] Verify approved doctors don't see the button

### 📊 Database Impact

**Before Migration:**
```sql
doctor_profiles
├── id
├── firebase_uid
├── first_name
├── last_name
├── specialization
├── verification_token
└── verification_document_path
```

**After Migration:**
```sql
doctor_profiles
├── id
├── firebase_uid
├── first_name
├── last_name
├── specialization
├── verification_token
├── verification_document_path
└── last_verification_request_sent  ← NEW
```

### 🚀 Deployment Steps

1. **Database Migration:**
   ```bash
   # In Supabase SQL Editor, run:
   # database/add_verification_request_timestamp.sql
   ```

2. **Backend Deployment:**
   - Backend code already includes new routes
   - Restart backend server to apply changes
   - Verify environment variables are set

3. **Frontend Deployment:**
   - Frontend code already updated
   - Component will automatically use new API routes
   - No additional configuration needed

4. **Verification:**
   - Test with a pending doctor account
   - Verify email sending works
   - Check cooldown period enforcement

### 📝 Notes

- **Cooldown Calculation**: Uses UTC timezone for consistency
- **Email Template**: Reuses existing admin notification template
- **Token Expiry**: Admin verification link still expires in 24 hours
- **Multiple Requests**: Each resend generates a new token, invalidating previous ones
- **Automatic Updates**: Timer refreshes every 60 seconds
- **Graceful Degradation**: If API fails, user sees error message but can retry

### 🔄 Future Enhancements

- [ ] Admin notification when doctor requests review
- [ ] Email to doctor confirming request was resent
- [ ] Analytics/logging of resend requests
- [ ] Customizable cooldown period (admin setting)
- [ ] Display verification link expiry time
- [ ] Option to upload new verification document
- [ ] In-app notification when verification status changes

### 🐛 Troubleshooting

**Button always disabled:**
- Check if `last_verification_request_sent` is populated
- Verify system time is correct (uses UTC)
- Check browser console for API errors

**Email not sending:**
- Verify ADMIN_EMAIL_PASSWORD environment variable
- Check Gmail app password is valid
- Review backend logs for SMTP errors

**API returns 404:**
- Ensure doctor_profile exists in database
- Verify firebase_uid matches correctly
- Check Supabase connection

**Cooldown calculation wrong:**
- Ensure timestamp stored in UTC
- Check for timezone conversion issues
- Verify datetime parsing in frontend

## Success Criteria

✅ Doctor can resend verification request from dashboard  
✅ 24-hour cooldown prevents spam  
✅ Admin receives email with verification link  
✅ UI shows clear feedback and countdown timer  
✅ System tracks all verification requests  
✅ Security validated with Firebase auth  
✅ Error handling provides helpful messages

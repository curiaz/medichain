# Doctor Account Reactivation Flow

## Overview
When a doctor account is deactivated and the doctor attempts to log in, they will be prompted with a confirmation modal to reactivate their account.

## User Experience Flow

### Step 1: Login Attempt
1. Deactivated doctor enters credentials on login page
2. Firebase authenticates successfully
3. Backend detects account is deactivated (`is_active: false`)

### Step 2: Reactivation Prompt
- **Modal appears automatically** with:
  - Title: "Reactivate Your Doctor Account"
  - Icon: Warning/Alert icon (yellow)
  - Message: "Your account is currently deactivated. Would you like to reactivate it?"

### Step 3: Information Display
The modal shows what will happen upon reactivation:
- ✓ Regain full access to doctor dashboard
- ✓ Be able to manage patient records
- ✓ Continue providing medical services
- ✓ Access all professional data
- Note: "Your profile has remained visible to patients during deactivation"

### Step 4: User Decision
**Two options:**
1. **Cancel** - Remains deactivated, returns to login page
2. **Yes, Reactivate My Account** - Proceeds with reactivation

### Step 5: Reactivation Process (if confirmed)
1. Frontend calls `/api/auth/reactivate-account` endpoint
2. Backend updates database:
   - `user_profiles.is_active` → `true`
   - `user_profiles.deactivated_at` → `null`
   - `user_profiles.reactivated_at` → current timestamp
   - `doctor_profiles.account_status` → `'active'`
3. Firebase user account re-enabled
4. Success message: "Account reactivated successfully!"
5. Automatic redirect to dashboard

## Technical Implementation

### Backend Changes

#### File: `backend/auth/firebase_auth_routes.py`

##### Modified: Login Endpoint
```python
@auth_firebase_bp.route('/login', methods=['POST'])
def login():
    # ... existing authentication logic ...
    
    # Check if account is deactivated (for doctors)
    is_deactivated = False
    if user_profile['role'] == 'doctor' and not user_profile.get('is_active', True):
        is_deactivated = True
    
    return jsonify({
        'success': True,
        'token': id_token,
        'user': {...},
        'requires_reactivation': is_deactivated  # New flag
    })
```

##### New Endpoint: Reactivate Account
```python
@auth_firebase_bp.route('/reactivate-account', methods=['POST'])
@firebase_auth_required
def reactivate_account():
    """Reactivate a deactivated doctor account"""
    
    # Get user from JWT token
    uid = request.firebase_user['uid']
    
    # Verify user is a doctor
    # Verify account is deactivated
    
    # Update database
    supabase.update('user_profiles', {
        'is_active': True,
        'deactivated_at': None,
        'reactivated_at': datetime.utcnow().isoformat()
    })
    
    supabase.update('doctor_profiles', {
        'account_status': 'active'
    })
    
    # Re-enable Firebase user
    auth.update_user(uid, disabled=False)
    
    return {'success': True, 'message': 'Account reactivated'}
```

**Endpoint:** `POST /api/auth/reactivate-account`  
**Auth:** Requires JWT token  
**Role:** Doctors only  
**Status:** 200 OK on success

### Frontend Changes

#### File: `src/context/AuthContext.jsx`

Modified login function to detect reactivation requirement:
```javascript
const login = async (email, password) => {
  // ... Firebase authentication ...
  
  const response = await axios.post('/auth/login', { id_token });
  
  if (response.data.requires_reactivation) {
    return {
      success: true,
      requiresReactivation: true,
      message: 'Account is deactivated',
      user: response.data.user,
      token: idToken
    };
  }
  
  // ... normal login flow ...
};
```

#### File: `src/frontend/MedichainLogin.jsx`

**New State Variables:**
- `showReactivationModal` - Controls modal visibility
- `reactivationToken` - Stores JWT for reactivation API call
- `isReactivating` - Loading state during reactivation

**Modified handleSubmit:**
```javascript
const result = await login(email, password);

if (result.requiresReactivation) {
  setReactivationToken(result.token);
  setShowReactivationModal(true);
  showToast.info("Your account is deactivated. Please confirm reactivation.");
  return; // Don't proceed with normal login
}
```

**New Handler: handleReactivateAccount**
```javascript
const handleReactivateAccount = async () => {
  // Call reactivation endpoint
  const response = await fetch('/api/auth/reactivate-account', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${reactivationToken}`
    }
  });
  
  if (result.success) {
    // Store credentials
    localStorage.setItem('medichain_token', reactivationToken);
    
    // Get updated user data
    // Navigate to dashboard
  }
};
```

**New Handler: handleCancelReactivation**
```javascript
const handleCancelReactivation = () => {
  setShowReactivationModal(false);
  setReactivationToken(null);
  showToast.info("Reactivation cancelled. Your account remains deactivated.");
};
```

**Modal UI Component:**
```jsx
{showReactivationModal && (
  <div className="profile-modal-overlay">
    <div className="profile-modal-content">
      {/* Header with warning icon */}
      {/* Information about reactivation */}
      {/* Buttons: Cancel | Yes, Reactivate */}
    </div>
  </div>
)}
```

## Database Schema Updates

### New Column: `user_profiles.reactivated_at`
```sql
ALTER TABLE user_profiles 
ADD COLUMN reactivated_at TIMESTAMP;
```

**Purpose:** Track when account was last reactivated for audit purposes

### Updated Columns During Reactivation
```sql
UPDATE user_profiles SET
  is_active = TRUE,
  deactivated_at = NULL,
  reactivated_at = NOW()
WHERE firebase_uid = ?;

UPDATE doctor_profiles SET
  account_status = 'active'
WHERE firebase_uid = ?;
```

## Security Considerations

1. **Authentication Required**: Reactivation endpoint requires valid JWT token
2. **Role Validation**: Only doctor accounts can be reactivated
3. **Status Check**: Prevents reactivating already-active accounts
4. **Firebase Sync**: Ensures Firebase user status matches database
5. **Audit Trail**: `reactivated_at` timestamp for tracking

## Edge Cases Handled

1. **Patient Login**: Patients don't see reactivation modal (role check)
2. **Active Account**: Already-active doctors login normally
3. **Multiple Reactivations**: Can deactivate and reactivate multiple times
4. **Token Expiration**: User must re-login if token expires during modal
5. **Network Failure**: Error handling with user-friendly messages
6. **Cancel Action**: Modal can be dismissed, account stays deactivated

## Testing Checklist

- [ ] Deactivated doctor logs in → reactivation modal appears
- [ ] Active doctor logs in → normal login flow (no modal)
- [ ] Patient logs in → no reactivation modal
- [ ] Click "Cancel" → modal closes, user returned to login
- [ ] Click "Reactivate" → account reactivated, redirected to dashboard
- [ ] After reactivation → doctor can access all features
- [ ] Backend validates JWT token for reactivation
- [ ] Backend prevents non-doctors from reactivating
- [ ] Backend prevents reactivating active accounts
- [ ] Firebase user re-enabled after reactivation
- [ ] Database timestamps updated correctly
- [ ] Error messages display on failure

## User Notifications

| Event | Toast Message | Type |
|-------|--------------|------|
| Reactivation Required | "Your account is deactivated. Please confirm reactivation." | Info (blue) |
| Reactivation Success | "Account reactivated successfully!" | Success (green) |
| Reactivation Cancelled | "Reactivation cancelled. Your account remains deactivated." | Info (blue) |
| Reactivation Failed | "Failed to reactivate account. Please try again." | Error (red) |

## API Response Examples

### Login with Deactivated Account
```json
{
  "success": true,
  "requires_reactivation": true,
  "token": "eyJhbGciOiJSUzI1NiIs...",
  "user": {
    "uid": "abc123",
    "email": "doctor@example.com",
    "profile": {
      "role": "doctor",
      "is_active": false,
      "deactivated_at": "2024-11-10T08:30:00Z"
    }
  }
}
```

### Reactivation Success
```json
{
  "success": true,
  "message": "Account reactivated successfully",
  "profile": {
    "is_active": true,
    "deactivated_at": null,
    "reactivated_at": "2024-11-11T10:15:00Z"
  }
}
```

### Reactivation Error (Not a Doctor)
```json
{
  "success": false,
  "error": "Only doctor accounts can be reactivated"
}
```

## Related Features

- **Account Deactivation**: See `DOCTOR_PATIENT_ACCOUNT_MANAGEMENT.md`
- **Profile Management**: Patient vs Doctor profiles
- **Authentication Flow**: Firebase + Supabase integration

## Future Enhancements

1. **Email Notification**: Send email when account is reactivated
2. **Admin Approval**: Require admin approval for reactivation
3. **Reactivation History**: Track all deactivation/reactivation events
4. **Automatic Deactivation**: Deactivate after X days of inactivity
5. **Reason for Reactivation**: Optional text field for why reactivating
6. **Two-Factor Verification**: Require 2FA for reactivation

## Deployment Checklist

- [ ] Backend changes deployed and tested
- [ ] Frontend changes built and deployed
- [ ] Database migration run (add `reactivated_at` column)
- [ ] Existing deactivated doctors notified of new feature
- [ ] Documentation updated
- [ ] Support team trained on reactivation flow

---

**Implementation Date**: November 11, 2025  
**Status**: ✅ Complete  
**Version**: 1.0

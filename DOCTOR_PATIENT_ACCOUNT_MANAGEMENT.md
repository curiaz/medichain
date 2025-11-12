# Doctor/Patient Account Management Implementation

## Overview
This document describes the implementation of separate account management for doctors and patients in MediChain:
- **Patients**: Can fully delete their accounts (complete data removal)
- **Doctors**: Can only deactivate their accounts (profile remains visible, login disabled)

## Why Separate Deletion vs Deactivation?

### Doctor Deactivation
- Patients need to access historical medical records
- Doctor profiles must remain visible for data continuity
- Medical history references need to remain intact
- Regulatory compliance requires maintaining healthcare provider information

### Patient Deletion
- Complete data removal for privacy compliance
- No downstream dependencies (patients don't provide services)
- Full GDPR/data privacy compliance

## Backend Implementation

### File: `backend/profile_routes.py`

#### DELETE /api/profile/delete-account Endpoint

**Doctor Flow:**
1. Verify user authentication via JWT token
2. Check user role from `user_profiles` table
3. For doctors:
   - Set `is_active: False` in `user_profiles`
   - Add `deactivated_at` timestamp
   - Update `doctor_profiles` with `account_status: 'deactivated'`
   - Disable Firebase Authentication account
   - Return `action: 'deactivated'` message

**Patient Flow:**
1. Verify user authentication via JWT token
2. Check user role from `user_profiles` table
3. For patients:
   - Delete from `appointments` table
   - Delete from `prescriptions` table
   - Delete from `medical_records` table
   - Delete from `ai_diagnoses` table
   - Delete from `user_documents` table
   - Delete from `privacy_settings` table
   - Delete from `blockchain_transactions` table
   - Delete from `credential_updates` table
   - Delete from `user_profiles` table (cascade)
   - Delete Firebase Authentication account
   - Return `action: 'deleted'` message

**Code Structure:**
```python
@profile_bp.route('/delete-account', methods=['DELETE'])
def delete_account():
    # Get user from JWT token
    user_id = request.user['uid']
    
    # Fetch user role
    user_response = supabase_client.table('user_profiles')...
    role = user_response.data[0]['role']
    
    if role == 'doctor':
        # DEACTIVATION FLOW
        # 1. Update user_profiles (is_active=False, deactivated_at)
        # 2. Update doctor_profiles (account_status='deactivated')
        # 3. Disable Firebase user
        return {'action': 'deactivated'}
    else:
        # DELETION FLOW
        # 1. Delete all related data from 9 tables
        # 2. Delete Firebase user
        return {'action': 'deleted'}
```

### File: `backend/auth/firebase_auth_routes.py`

#### POST /api/auth/verify-password Endpoint

Validates user password before allowing account deletion/deactivation:
- Detects OAuth users (Google Sign-In) - automatically verified
- Validates password via Firebase REST API
- Returns user-friendly error messages

## Frontend Implementation

### New File: `src/pages/DoctorProfilePage.jsx`

Complete profile management page for doctors with:
- Role validation (doctors only)
- Account deactivation modal (2-step process)
- Password verification
- Deactivation warnings and information
- Professional profile sections

**Key Features:**
- Uses `ShieldOff` icon for deactivation (vs `Trash2` for deletion)
- Custom messaging: "deactivate" instead of "delete"
- Explains profile remains visible after deactivation
- Two-step modal: password → confirmation

### Updated File: `src/pages/ProfilePage.jsx`

Enhanced patient profile page with:
- Role validation (patients only - blocks doctors)
- Complete account deletion modal
- Password verification
- Privacy-focused deletion warnings

**Changes Made:**
```jsx
// Added role check in loadProfile()
if (user.profile?.role === 'doctor') {
  setError('Access denied. This page is for patients only.');
  return;
}
```

### Routing Configuration

#### File: `src/App.js`

Added separate routes:
```jsx
import DoctorProfilePage from './pages/DoctorProfilePage';

// Routes
<Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
<Route path="/doctor-profile" element={<ProtectedRoute><DoctorProfilePage /></ProtectedRoute>} />
```

#### New File: `src/components/ProfileRouter.jsx`

Auto-redirects users to correct profile based on role:
```jsx
if (user.profile?.role === 'doctor') {
  navigate('/doctor-profile');
} else {
  navigate('/profile');
}
```

### Navigation Updates

#### File: `src/pages/Header.jsx`

Updated profile click handler:
```jsx
const handleProfileClick = () => {
  if (user?.profile?.role === 'doctor') {
    navigate('/doctor-profile');
  } else {
    navigate('/profile');
  }
};
```

#### File: `src/components/DashboardLayout.jsx`

Updated profile navigation:
```jsx
const handleProfileClick = () => {
  if (user?.profile?.role === 'doctor') {
    navigate('/doctor-profile');
  } else {
    navigate('/profile');
  }
};
```

## Modal Flow Comparison

### Patient Deletion Modal (ProfilePage.jsx)

**Step 1: Password Verification**
- Title: "Verify Your Identity"
- Icon: AlertCircle (yellow warning)
- Warning box explains permanent deletion
- Password input field
- Button: "Verify Password"

**Step 2: Final Confirmation**
- Title: "Final Confirmation"
- Icon: Trash2 (red danger)
- Lists what will be deleted:
  - ✓ All medical records
  - ✓ All appointments
  - ✓ All prescriptions
  - ✓ All AI diagnoses
  - ✓ All documents
  - ✓ Account settings
- Warning: Cannot be recovered
- Buttons: "No, Keep My Account" | "Yes, Delete My Account"

### Doctor Deactivation Modal (DoctorProfilePage.jsx)

**Step 1: Password Verification**
- Title: "Verify Your Identity"
- Icon: AlertCircle (yellow warning)
- Warning box explains deactivation vs deletion
- Lists what happens:
  - Disable login access
  - Keep profile visible to patients
  - Preserve medical records
  - Maintain patient care continuity
  - Allow profile viewing but not editing
- Password input field
- Button: "Verify Password"

**Step 2: Final Confirmation**
- Title: "Final Confirmation"
- Icon: ShieldOff (red danger)
- Lists deactivation details:
  - ✓ Login access disabled
  - ✓ Patients can still view profile
  - ✓ All medical records remain accessible
  - ✓ Patient care continuity maintained
  - ✓ Professional data preserved
- Note: Contact support to reactivate
- Buttons: "No, Keep My Account Active" | "Yes, Deactivate My Account"

## Database Schema Impact

### Doctor Deactivation Changes

**user_profiles table:**
```sql
is_active: false
deactivated_at: '2024-01-15 10:30:00'
```

**doctor_profiles table:**
```sql
account_status: 'deactivated'
```

**firebase_auth:**
```
disabled: true
```

### Patient Deletion Changes

**All tables:**
- Complete data removal from 9 tables
- Cascade deletion from `user_profiles`
- Firebase user completely deleted

## Security Considerations

1. **JWT Authentication**: All endpoints require valid token
2. **Password Verification**: Required before any account action
3. **OAuth Detection**: Google Sign-In users auto-verified (session-based)
4. **Role Validation**: Backend validates role to prevent unauthorized actions
5. **Frontend Guards**: Role checks prevent wrong profile access

## User Experience

### For Doctors:
1. Navigate to Doctor Profile → Account Security tab
2. Click "Deactivate Account" button
3. Enter password for verification
4. Review deactivation details
5. Confirm deactivation
6. Logged out and redirected to landing page
7. **Profile remains visible to patients**

### For Patients:
1. Navigate to Profile → Account Security tab
2. Click "Delete Account" button
3. Enter password for verification
4. Review deletion warnings
5. Confirm deletion
6. Logged out and redirected to landing page
7. **All data permanently removed**

## Testing Checklist

- [ ] Doctor can access `/doctor-profile`
- [ ] Patient can access `/profile`
- [ ] Doctor blocked from `/profile`
- [ ] Patient blocked from `/doctor-profile`
- [ ] Doctor deactivation sets `is_active: false`
- [ ] Doctor profile visible after deactivation
- [ ] Doctor cannot login after deactivation
- [ ] Patient deletion removes all data
- [ ] Patient profile not accessible after deletion
- [ ] Password verification works for both flows
- [ ] OAuth users auto-verified
- [ ] Navigation redirects to correct profile page
- [ ] Header profile icon navigates correctly
- [ ] Dashboard profile link navigates correctly

## Future Enhancements

1. **Doctor Reactivation**: Admin interface to reactivate doctors
2. **Soft Delete for Patients**: Optional "deactivate" instead of delete
3. **Data Export**: Allow users to download data before deletion
4. **Grace Period**: 30-day window before permanent deletion
5. **Audit Trail**: Log all account status changes
6. **Email Notifications**: Confirmation emails for account changes

## API Endpoints Summary

| Endpoint | Method | Role | Action |
|----------|--------|------|--------|
| `/api/profile/delete-account` | DELETE | Doctor | Deactivate account |
| `/api/profile/delete-account` | DELETE | Patient | Delete account |
| `/api/auth/verify-password` | POST | Both | Verify password |

## File Changes Summary

### New Files:
1. `src/pages/DoctorProfilePage.jsx` - Doctor profile management
2. `src/components/ProfileRouter.jsx` - Role-based routing helper

### Modified Files:
1. `backend/profile_routes.py` - Role-based deletion/deactivation logic
2. `src/pages/ProfilePage.jsx` - Added role validation for patients
3. `src/App.js` - Added doctor profile route
4. `src/pages/Header.jsx` - Role-based profile navigation
5. `src/components/DashboardLayout.jsx` - Role-based profile navigation

## Deployment Notes

1. Restart backend server after changes
2. Clear frontend build cache
3. Test with both doctor and patient accounts
4. Verify database RLS policies allow deactivation updates
5. Check Firebase Admin SDK permissions for disabling users

---

**Implementation Date**: January 2024  
**Status**: ✅ Complete  
**Tested**: ⏳ Pending user testing

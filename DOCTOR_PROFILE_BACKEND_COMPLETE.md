# Doctor Profile Backend - Migration & Setup Guide

## ✅ What's Been Implemented

### Backend Endpoints Created
All new endpoints in `backend/profile_routes.py`:

1. **PUT /api/profile/doctor/update** - Update personal, professional info, and privacy settings
2. **GET /api/profile/doctor/details** - Get complete doctor profile
3. **POST /api/profile/doctor/documents/upload** - Upload verification documents
4. **GET /api/profile/doctor/documents** - Get all uploaded documents
5. **PUT /api/profile/doctor/privacy** - Update privacy settings
6. **GET /api/profile/doctor/activity** - Get activity history

### Frontend Integration
All save handlers connected in `src/pages/DoctorProfilePage.jsx`:

- ✅ Personal Info tab - saves all fields including address
- ✅ Professional Info tab - saves license, specialization, experience, affiliation
- ✅ Documents tab - file upload with status display
- ✅ Privacy Settings tab - toggles and dropdowns with save button
- ✅ Activity History tab - automatically loads recent activities
- ✅ All operations logged to activity log

### Database Changes Required
Migration file created: `backend/migrations/add_doctor_profile_enhancements.sql`

## 🚀 Quick Start - Run Migration

### Option 1: Using Supabase Dashboard (Recommended)

1. **Go to your Supabase Dashboard**
   - Navigate to: https://supabase.com/dashboard
   - Select your MediChain project

2. **Open SQL Editor**
   - Click "SQL Editor" in the left sidebar
   - Click "+ New Query"

3. **Copy and paste the entire SQL from:**
   ```
   backend/migrations/add_doctor_profile_enhancements.sql
   ```

4. **Click "Run" button** (or press Ctrl+Enter)

5. **Verify the changes:**
   - Check "Table Editor" for new tables: `activity_logs`, `doctor_documents`
   - Check `user_profiles` for new columns: address, city, state, zip_code
   - Check `doctor_profiles` for new columns: privacy settings

### Option 2: Using psql Command Line

```bash
# If you have psql installed and your DATABASE_URL configured:
psql $DATABASE_URL -f backend/migrations/add_doctor_profile_enhancements.sql
```

## 📋 What the Migration Does

### 1. User Profiles Table Enhancement
Adds address fields:
- `address` VARCHAR(255)
- `city` VARCHAR(100)
- `state` VARCHAR(100)
- `zip_code` VARCHAR(20)

### 2. Doctor Profiles Table Enhancement
Adds privacy settings:
- `profile_visibility` VARCHAR(50) - Options: 'public', 'patients', 'private'
- `show_email` BOOLEAN - Display email on profile
- `show_phone` BOOLEAN - Display phone on profile
- `allow_patient_messages` BOOLEAN - Allow direct messages
- `data_sharing` BOOLEAN - Share anonymized data for research

### 3. New Table: activity_logs
Tracks all profile activities:
- `id` UUID (Primary Key)
- `firebase_uid` VARCHAR(255) - User identifier
- `action` VARCHAR(255) - Action performed
- `details` TEXT - Additional details
- `timestamp` TIMESTAMP - When it occurred

**Indexes:** firebase_uid, timestamp (for fast queries)

### 4. New Table: doctor_documents
Stores uploaded verification documents:
- `id` UUID (Primary Key)
- `firebase_uid` VARCHAR(255) - Doctor identifier
- `document_type` VARCHAR(50) - 'license', 'certificate', 'verification'
- `filename` VARCHAR(500) - Original filename
- `file_size` INTEGER - File size in bytes
- `file_type` VARCHAR(100) - MIME type
- `uploaded_at` TIMESTAMP - Upload time
- `status` VARCHAR(50) - 'pending', 'approved', 'rejected'

**Indexes:** firebase_uid, status

### 5. Row Level Security (RLS)
- Users can only view their own activity logs
- Doctors can only view and insert their own documents
- Admin access requires service role key (already configured)

## 🧪 Testing the Backend

### 1. Start Backend Server
```bash
cd backend
python app.py
```

### 2. Test Endpoints

**Update Personal Info:**
```bash
curl -X PUT http://localhost:5000/api/profile/doctor/update \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Dr. John",
    "last_name": "Smith",
    "phone": "555-0123",
    "address": "123 Medical Plaza",
    "city": "Boston",
    "state": "MA",
    "zip_code": "02101"
  }'
```

**Update Professional Info:**
```bash
curl -X PUT http://localhost:5000/api/profile/doctor/update \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "specialization": "Cardiology",
    "license_number": "MD123456",
    "years_of_experience": 10,
    "hospital_affiliation": "Massachusetts General Hospital"
  }'
```

**Upload Document:**
```bash
curl -X POST http://localhost:5000/api/profile/doctor/documents/upload \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -F "file=@/path/to/license.pdf" \
  -F "type=license"
```

**Get Activity Log:**
```bash
curl -X GET http://localhost:5000/api/profile/doctor/activity \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"
```

## ✨ Features Now Available

### Personal Information Tab
- Save first name, last name, phone, email
- Save full address (street, city, state, zip)
- Automatic activity logging on save

### Professional Information Tab
- Save medical license number
- Save specialization
- Save years of experience
- Save hospital affiliation
- Edit mode with cancel option

### Documents Tab
- Upload medical license (PDF, JPG, PNG up to 5MB)
- Upload professional certificates
- Upload verification documents
- View upload status (pending/approved/rejected)
- See upload date and file size

### Privacy Settings Tab
- Control profile visibility (public/patients only/private)
- Toggle email display on profile
- Toggle phone display on profile
- Toggle patient direct messaging
- Toggle anonymized data sharing for research
- Save all settings at once

### Account Security Tab
- Change password (existing functionality)
- Account deactivation with password verification
- Two-factor authentication (UI ready, backend pending)

### Activity History Tab
- Auto-loads recent activities
- Shows timestamp, action, and details
- Updates automatically after each profile change
- Last 50 activities displayed

## 🔧 Troubleshooting

### Migration Errors

**"relation already exists"**
- This is normal if you've run parts of the migration before
- The migration uses `IF NOT EXISTS` to avoid conflicts
- You can safely ignore these messages

**"permission denied"**
- Make sure you're using the service role key, not the anon key
- Check your `.env` file has `SUPABASE_SERVICE_ROLE_KEY`

**"syntax error"**
- Make sure you copied the entire SQL file
- Check that no characters were corrupted during copy/paste

### Runtime Errors

**"firebase_uid not found"**
- User is not properly authenticated
- Check that Firebase token is valid and not expired

**"No data provided"**
- Frontend is sending empty request body
- Check browser console for errors

**"File too large"**
- Files must be under 5MB
- Compress or reduce file size before uploading

## 📝 Next Steps

After running the migration:

1. **Restart backend server** to load new endpoints
2. **Clear browser cache** to avoid stale JavaScript
3. **Test each tab** of the doctor profile:
   - Edit and save personal info
   - Edit and save professional info
   - Upload a test document
   - Change privacy settings
   - View activity log

4. **Check Supabase Tables:**
   - user_profiles - verify address fields populated
   - doctor_profiles - verify privacy settings saved
   - activity_logs - verify activities are being logged
   - doctor_documents - verify uploaded files are tracked

## 🎉 Success Indicators

You'll know everything is working when:

- ✅ All 6 tabs load without errors
- ✅ Save buttons show "Saved successfully!" messages
- ✅ Activity log populates with recent actions
- ✅ Documents show upload status
- ✅ Privacy toggles persist after page refresh
- ✅ No console errors in browser or backend logs

## 💡 Tips

- **Activity Log** is your friend - it shows when things are working
- **Browser DevTools Network tab** shows API requests and responses
- **Backend console** shows detailed logs with [DEBUG] and [ERROR] markers
- **Supabase Table Editor** lets you inspect data directly

---

**Ready to go!** Run the migration and start using your fully functional doctor profile! 🎉

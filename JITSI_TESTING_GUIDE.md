# Jitsi Integration - Testing Guide

## ✅ Database Migration Complete

The database migration has been completed. Here's how to test the full integration:

## 🧪 Testing Steps

### 1. **Start Backend Server**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python app.py
```

### 2. **Start Frontend**
```powershell
npm start
```

### 3. **Test Appointment Creation**
1. Login as a **patient**
2. Navigate to "Book Appointment"
3. Select a doctor and time slot
4. Submit the appointment
5. **Expected Results:**
   - ✅ Appointment created successfully
   - ✅ Notification appears for patient
   - ✅ Notification appears for doctor
   - ✅ Meeting link stored in database

### 4. **Test Notifications**
1. Check notifications page (`/notifications`)
2. **Expected Results:**
   - ✅ Patient sees: "Your appointment with Dr. {name} is scheduled..."
   - ✅ Doctor sees: "You have a new appointment with {patient_name}..."
   - ✅ Both notifications include meeting URL

### 5. **Test Video Links**
1. **As Patient:**
   - Go to "My Appointments" (`/my-appointments`)
   - Click "Join Video Consultation" button
   - ✅ Opens Jitsi meeting in new tab

2. **As Doctor:**
   - Go to "Schedule Management" (`/doctor-schedule`)
   - Click "Join Video Consultation" button
   - ✅ Opens same Jitsi meeting room

### 6. **Verify Database**
Run in Supabase SQL Editor:
```sql
-- Check appointments have meeting_link
SELECT id, appointment_date, appointment_time, meeting_link 
FROM appointments 
WHERE meeting_link IS NOT NULL 
ORDER BY created_at DESC 
LIMIT 5;

-- Check notifications were created
SELECT user_id, title, category, action_url, metadata 
FROM notifications 
WHERE category = 'appointment' 
ORDER BY created_at DESC 
LIMIT 10;
```

## 🔍 Verification Checklist

- [ ] Backend server running on port 5000
- [ ] Frontend running on port 3000
- [ ] Can create appointments
- [ ] Meeting links appear in appointment lists
- [ ] Notifications created for both users
- [ ] Video links open Jitsi meetings
- [ ] Both patient and doctor can join same room
- [ ] Database has meeting_link values
- [ ] Notifications stored in database

## 🐛 Troubleshooting

### Meeting links not appearing?
- Check backend logs for errors
- Verify `meeting_link` column exists: `SELECT column_name FROM information_schema.columns WHERE table_name = 'appointments' AND column_name = 'meeting_link';`
- Check appointment response includes `meeting_url` field

### Notifications not created?
- Check backend logs for notification service errors
- Verify notifications table exists: `SELECT COUNT(*) FROM notifications;`
- Check Supabase RLS policies allow inserts

### Video links not working?
- Verify Jitsi URL format: Should start with `https://meet.jit.si/`
- Check browser console for errors
- Try opening link directly in browser

## 📊 Expected Database State

### Appointments Table:
- `meeting_link` column exists ✅
- Contains Jitsi URLs like: `https://meet.jit.si/medichain-{doctor}-{date}-{time}-{random}` ✅

### Notifications Table:
- Contains appointment notifications ✅
- `category` = 'appointment' ✅
- `metadata` includes `meeting_url` ✅
- `action_url` points to appointment or meeting ✅

## 🎉 Success Indicators

✅ **Integration is working if:**
1. Appointments create with meeting links
2. Both users receive notifications
3. Video links appear in UI
4. Clicking links opens Jitsi meetings
5. Both users can join the same room

## 🚀 Next Steps

Once testing is complete:
1. Test with real users
2. Monitor notification delivery
3. Test video call quality
4. Consider adding appointment reminders (24h before)
5. Consider adding "starting soon" notifications (5min before)


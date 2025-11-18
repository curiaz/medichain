# MediChain Complete Setup Guide - Jitsi Integration

## Prerequisites
- Python 3.8+ installed
- Node.js and npm installed
- Supabase account and credentials configured in `backend/.env`

## Backend Setup

1. **Install Dependencies**
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Start Backend Server**
   ```powershell
   python app.py
   ```
   Backend will be available at: https://medichain.clinic

## Frontend Setup

1. **Install Dependencies** (if not already done)
   ```powershell
   npm install
   ```

2. **Start Frontend**
   ```powershell
   npm start
   ```
   Frontend will be available at: http://localhost:3000

## Testing the Appointment System with Jitsi

### As a Patient:

1. **Login** → Navigate to Patient Dashboard
2. **Book Appointment** → Click "Book an Appointment"
3. **Select GP** → Choose a doctor with availability
4. **Complete Booking** → Fill appointment form and submit
   - A Jitsi meeting room will be automatically created
   - Meeting URL will be stored in appointment notes
5. **View Appointments** → Go to "My Appointments"
   - See your scheduled appointments
   - Click "Join Jitsi Room" to join the video call

### As a Doctor:

1. **Login** → Navigate to Doctor Dashboard
2. **Schedule Management** → Click "Schedule Management"
   - View all upcoming appointments
   - See patient names and appointment times
   - Click "Join Jitsi Room" to join as host
3. **Manage Availability** → Use the availability manager on the right
   - Add dates and time slots
   - Save availability to database

## Features Implemented

✅ **Jitsi Video Conferencing**
- Automatic room generation on appointment creation
- Unique room names: `medichain-{doctorUid}-{date}-{time}-{suffix}`
- Meeting URLs stored in appointment notes for history/records
- Accessible from both patient and doctor dashboards

✅ **Database Persistence**
- Appointments stored in Supabase `appointments` table
- Meeting URLs preserved in notes field for historical records
- Patient and doctor can access meeting links anytime

✅ **Schedule Management**
- Doctor dashboard shows all appointments with patient info
- Patient dashboard shows own appointments with join links
- Real-time availability updates

✅ **End-to-End Flow**
- Patient books → Meeting created → Both sides notified
- Meeting links visible in schedule management
- All appointments saved to database for records

## API Endpoints

- `GET /api/appointments` - Get user's appointments (with meeting URLs parsed)
- `POST /api/appointments` - Create appointment (generates Jitsi room)
- `GET /api/appointments/doctors/approved` - List approved doctors
- `PUT /api/appointments/availability` - Update doctor availability

## Troubleshooting

**Backend won't start:**
- Check `backend/.env` has correct Supabase credentials
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Check port 5000 is not in use

**Frontend won't start:**
- Check port 3000 is not in use
- Run `npm install` to ensure dependencies installed

**Appointments not showing:**
- Verify backend is running on port 5000
- Check browser console for errors
- Ensure authentication token is valid

**Jitsi links not appearing:**
- Verify appointment was created successfully
- Check appointment notes contain "Meeting: https://meet.jit.si/..."
- Backend parses meeting URL from notes automatically

## Next Steps (Optional Enhancements)

- Email notifications with meeting links
- Appointment cancellation/rescheduling
- Meeting recording storage
- Push notifications for appointment reminders


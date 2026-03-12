# Fix Hardcoded Localhost URLs

## Files Fixed ✅
1. ✅ src/services/aiService.js
2. ✅ src/services/patientService.js
3. ✅ src/services/notificationService.js
4. ✅ src/services/databaseService.js
5. ✅ src/pages/SelectGP.jsx
6. ✅ src/pages/SelectDateTime.jsx

## Files Still Need Fixing ⚠️

### Pages (High Priority)
- src/pages/Notifications.jsx (5 instances)
- src/pages/ProfilePage.jsx (5 instances)
- src/pages/HealthRecord.jsx (4 instances)
- src/pages/BookAppointmentForm.jsx (2 instances)
- src/pages/PrescriptionVerification.jsx (2 instances)
- src/pages/DoctorSchedule.jsx (1 instance)
- src/pages/DoctorMedicalReports.jsx (4 instances)
- src/pages/DoctorProfilePage.jsx (2 instances)
- src/pages/DoctorAIDiagnosisReview.jsx (6 instances)
- src/pages/DoctorAvailability.jsx (3 instances)
- src/pages/DoctorDashboard.jsx (4 instances)
- src/pages/PatientAppointments.jsx (1 instance)
- src/pages/SymptomsSelection.jsx (1 instance)
- src/pages/AIHealth_Modern.jsx (1 instance)

### Components
- src/components/NotificationTable.jsx (1 instance)
- src/components/JitsiVideoConference.jsx (2 instances)
- src/components/VerificationStatus.jsx (2 instances)

### Frontend
- src/frontend/MedichainSignup.jsx (1 instance)

## Pattern to Use
Replace:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
// or
'http://localhost:5000/api/...'
```

With:
```javascript
import { API_CONFIG } from '../config/api';
// then use
API_CONFIG.BASE_URL
// or
API_CONFIG.API_URL
```


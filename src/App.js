import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import BottomNavigation from './components/BottomNavigation';
import LandingPage from './pages/LandingPage';
import MedichainLogin from './frontend/MedichainLogin';
import MedichainSignup from './frontend/MedichainSignup';
import ResetPassword from './frontend/ResetPassword'; // Updated reset password component
import FirebaseDebugTest from './components/FirebaseDebugTest'; // Debug tool
import Dashboard from './pages/Dashboard'; // Role-based dashboard router
import AIHealth from './pages/AIHealth'; // New standalone AI Health page
import PatientAIHistory from './pages/PatientAIHistory'; // For doctors to view patient AI history
import HealthRecord from './pages/HealthRecord'; // Patient health record page
import ProfilePage from './pages/ProfilePage'; // Profile management page
import PatientList from './pages/PatientList'; // Patient list management page
import Notifications from './pages/Notifications'; // Notifications page
import BookAppointment from './pages/BookAppointment'; // Book appointment page
import SelectGP from './pages/SelectGP'; // Select GP page
import SymptomsSelection from './pages/SymptomsSelection'; // Symptoms selection page
import DocumentUpload from './pages/DocumentUpload'; // Document upload page
import SelectDateTime from './pages/SelectDateTime'; // Select Date & Time page
import BookAppointmentForm from './pages/BookAppointmentForm'; // Appointment booking form
import DoctorAvailability from './pages/DoctorAvailability'; // Doctor availability management
import DoctorSchedule from './pages/DoctorSchedule'; // Doctor schedule management
import DoctorAIDiagnosisReview from './pages/DoctorAIDiagnosisReview'; // Doctor AI diagnosis review page
import DoctorMedicalReports from './pages/DoctorMedicalReports'; // Doctor medical reports page
import PatientAppointments from './pages/PatientAppointments'; // Patient appointments list
import PrescriptionVerification from './pages/PrescriptionVerification'; // Prescription QR verification page
import ProtectedRoute from './components/ProtectedRoute';
import JitsiVideoConference from './components/JitsiVideoConference'; // Jitsi video conference component
import './App.css';
import './assets/styles/AndroidApp.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            {/* Landing page as the default route */}
            <Route path="/" element={<LandingPage />} />
            
            {/* Auth routes */}
            <Route path="/login" element={<MedichainLogin />} />
            <Route path="/signup" element={<MedichainSignup />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="/debug-firebase" element={<FirebaseDebugTest />} />
            
            {/* Public prescription verification route (for pharmacy QR scanning) */}
            <Route path="/verify-prescription/:appointmentId" element={<PrescriptionVerification />} />
            
            {/* Protected Dashboard routes */}
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/patients" 
              element={
                <ProtectedRoute>
                  <PatientList />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/ai-health" 
              element={<AIHealth />} 
            />
            
            <Route 
              path="/health-record" 
              element={
                <ProtectedRoute>
                  <HealthRecord />
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/my-appointments" 
              element={
                <ProtectedRoute>
                  <PatientAppointments />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/patient-ai-history" 
              element={
                <ProtectedRoute>
                  <PatientAIHistory />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/notifications" 
              element={
                <ProtectedRoute>
                  <Notifications />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/profile" 
              element={
                <ProtectedRoute>
                  <ProfilePage />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/book-appointment" 
              element={
                <ProtectedRoute>
                  <BookAppointment />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/select-gp" 
              element={
                <ProtectedRoute>
                  <SelectGP />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/symptoms-selection" 
              element={
                <ProtectedRoute>
                  <SymptomsSelection />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/document-upload" 
              element={
                <ProtectedRoute>
                  <DocumentUpload />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/select-date-time" 
              element={
                <ProtectedRoute>
                  <SelectDateTime />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/book-appointment-form" 
              element={
                <ProtectedRoute>
                  <BookAppointmentForm />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/doctor-availability" 
              element={
                <ProtectedRoute>
                  <DoctorAvailability />
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/doctor-schedule" 
              element={
                <ProtectedRoute allowedRoles={["doctor"]} requireDoctorVerified={true}>
                  <DoctorSchedule />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/doctor-ai-diagnosis/:appointmentId?" 
              element={
                <ProtectedRoute allowedRoles={["doctor"]} requireDoctorVerified={true}>
                  <DoctorAIDiagnosisReview />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/doctor-medical-reports" 
              element={
                <ProtectedRoute allowedRoles={["doctor"]} requireDoctorVerified={true}>
                  <DoctorMedicalReports />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/video/:roomName" 
              element={
                <ProtectedRoute>
                  <JitsiVideoConference />
                </ProtectedRoute>
              } 
            />
            
            {/* Redirect any unknown routes to landing page */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
          
          {/* Android-style Bottom Navigation */}
          <BottomNavigation />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;

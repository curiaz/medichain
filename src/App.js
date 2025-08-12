import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import LandingPage from './pages/LandingPage';
import MedichainLogin from './frontend/MedichainLogin';
import MedichainSignup from './frontend/MedichainSignup';
import Dashboard from './pages/Dashboard'; // Use the correct Dashboard component
import ProtectedRoute from './components/ProtectedRoute';
import './App.css';

// Create placeholder components
const ResetPassword = () => (
  <div style={{ padding: '2rem', textAlign: 'center' }}>
    <h2>Reset Password</h2>
    <p>Reset password component coming soon...</p>
  </div>
);

// Placeholder components for other routes
const Patients = () => (
  <div style={{ padding: '2rem', textAlign: 'center', marginTop: '80px' }}>
    <h2>Patients</h2>
    <p>Patients management coming soon...</p>
  </div>
);

const AIAssistant = () => (
  <div style={{ padding: '2rem', textAlign: 'center', marginTop: '80px' }}>
    <h2>AI Assistant</h2>
    <p>AI Assistant feature coming soon...</p>
  </div>
);

const Prescriptions = () => (
  <div style={{ padding: '2rem', textAlign: 'center', marginTop: '80px' }}>
    <h2>Prescriptions</h2>
    <p>Prescriptions management coming soon...</p>
  </div>
);

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
                  <Patients />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/ai-assistant" 
              element={
                <ProtectedRoute>
                  <AIAssistant />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/prescriptions" 
              element={
                <ProtectedRoute>
                  <Prescriptions />
                </ProtectedRoute>
              } 
            />
            
            {/* Redirect any unknown routes to landing page */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;

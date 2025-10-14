import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import LoadingSpinner from './LoadingSpinner';

const ProtectedRoute = ({ children, allowedRoles = [], requireDoctorVerified = false }) => {
  const { isAuthenticated, user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <LoadingSpinner fullScreen={true} text="Checking authentication..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(user?.role)) {
    return <Navigate to="/dashboard" replace />;
  }

  // If route requires verified doctor, enforce it
  if (requireDoctorVerified && user?.role === 'doctor') {
    const status = user?.doctor_profile?.verification_status || user?.profile?.verification_status;
    if (status !== 'approved') {
      // Redirect to doctor dashboard where we display the status component
      return <Navigate to="/doctor" state={{ reason: 'verification_required' }} replace />;
    }
  }

  return children;
};

export default ProtectedRoute;

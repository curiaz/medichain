import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import LoadingSpinner from './LoadingSpinner';

const ProtectedRoute = ({ children, allowedRoles = [], requireDoctorVerified = false }) => {
  const { isAuthenticated, user, loading } = useAuth();
  const location = useLocation();

  // DEBUG: Log protection check
  console.log("🔒 ProtectedRoute: Checking access for", location.pathname);
  console.log("🔒 ProtectedRoute: isAuthenticated =", isAuthenticated);
  console.log("🔒 ProtectedRoute: user =", user);
  console.log("🔒 ProtectedRoute: allowedRoles =", allowedRoles);
  console.log("🔒 ProtectedRoute: loading =", loading);

  if (loading) {
    console.log("⏳ ProtectedRoute: Still loading, showing spinner...");
    return <LoadingSpinner fullScreen={true} text="Checking authentication..." />;
  }

  if (!isAuthenticated) {
    console.log("❌ ProtectedRoute: Not authenticated, redirecting to /login");
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(user?.role)) {
    console.log("❌ ProtectedRoute: Role mismatch! User role:", user?.role, "Allowed:", allowedRoles);
    console.log("❌ ProtectedRoute: Redirecting to /dashboard");
    return <Navigate to="/dashboard" replace />;
  }

  console.log("✅ ProtectedRoute: Access granted!");

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

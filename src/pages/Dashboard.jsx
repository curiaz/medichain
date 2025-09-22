/* Dashboard.jsx - Router for role-based dashboards */
import React from "react"
import { useAuth } from "../context/AuthContext"
import DoctorDashboard from "./DoctorDashboard"
import PatientDashboard from "./PatientDashboard"
import AdminDashboard from "./AdminDashboard"
import LoadingSpinner from "../components/LoadingSpinner"

const Dashboard = () => {
  const { user, loading } = useAuth();

  // Show loading while user data is being fetched
  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        flexDirection: 'column',
        gap: '1rem'
      }}>
        <LoadingSpinner />
        <span>Loading dashboard...</span>
      </div>
    );
  }

  // Show error if no user data
  if (!user) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        flexDirection: 'column',
        gap: '1rem',
        color: '#666'
      }}>
        <h2>Access Denied</h2>
        <p>Please log in to access the dashboard.</p>
      </div>
    );
  }

  // Route to appropriate dashboard based on user role
  const userRole = user.profile?.role || user.role;
  
  if (userRole === 'doctor') {
    return <DoctorDashboard />;
  } else if (userRole === 'patient') {
    return <PatientDashboard />;
  } else if (userRole === 'admin') {
    return <AdminDashboard />;
  } else {
    // Default fallback for unknown roles
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        flexDirection: 'column',
        gap: '1rem',
        color: '#666'
      }}>
        <h2>Unknown User Role</h2>
        <p>Unable to determine the appropriate dashboard for your role: {userRole || 'undefined'}</p>
        <p>User data: {JSON.stringify(user, null, 2)}</p>
        <p>Please contact support for assistance.</p>
      </div>
    );
  }
}

export default Dashboard
import React from 'react';
import { useAuth } from '../context/AuthContext';
import DashboardLayout from '../components/DashboardLayout';

const AdminDashboard = () => {
  const { user } = useAuth();

  return (
    <DashboardLayout>
      <div className="dashboard-content">
        <div className="dashboard-header">
          <h1>Admin Dashboard</h1>
          <p>Welcome back, {user?.profile?.first_name || user?.email}!</p>
        </div>

        <div className="dashboard-grid">
          <div className="dashboard-card">
            <h3>System Overview</h3>
            <p>Manage users, view system statistics, and configure application settings.</p>
          </div>

          <div className="dashboard-card">
            <h3>User Management</h3>
            <p>View and manage all users in the system.</p>
          </div>

          <div className="dashboard-card">
            <h3>System Settings</h3>
            <p>Configure application settings and preferences.</p>
          </div>

          <div className="dashboard-card">
            <h3>Reports</h3>
            <p>View system reports and analytics.</p>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default AdminDashboard;

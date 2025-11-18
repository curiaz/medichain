import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import Header from './Header';
import AdminStats from '../components/AdminStats';
import UserManagementTable from '../components/UserManagementTable';
import DoctorVerificationTable from '../components/DoctorVerificationTable';
import AuditLedger from '../components/AuditLedger';
import '../assets/styles/ModernDashboard.css';
import '../assets/styles/AdminDashboard.css';

const AdminDashboard = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'users', label: 'User Management' },
    { id: 'doctors', label: 'Doctor Verification' },
    { id: 'audit', label: 'Audit Ledger' }
  ];

  const userName = user?.profile?.first_name || user?.first_name || user?.name || 'Admin';

  return (
    <div className="dashboard-container fade-in">
      {/* Background crosses */}
      <div className="background-crosses">
        {[...Array(24)].map((_, i) => (
          <span key={i} className={`cross cross-${i + 1}`}>
            +
          </span>
        ))}
      </div>

      <Header />

      <main className="dashboard-main-content">
        <div className="dashboard-header-section" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
          <div className="dashboard-title-section" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <h1 className="dashboard-title" style={{ marginBottom: '16px' }}>ADMIN DASHBOARD</h1>
            {user && (
              <div className="user-welcome" style={{ textAlign: 'center' }}>
                <span>Welcome back, <strong>{userName}</strong></span>
                <span className="user-role">SYSTEM ADMINISTRATOR</span>
              </div>
            )}
          </div>
        </div>

        {/* Tabs */}
        <div className="admin-dashboard-tabs">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`admin-tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label.toUpperCase()}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="admin-dashboard-content">
          {activeTab === 'overview' && (
            <div className="admin-overview">
              <AdminStats />
            </div>
          )}

          {activeTab === 'users' && (
            <div className="admin-users">
              <UserManagementTable />
            </div>
          )}

          {activeTab === 'doctors' && (
            <div className="admin-doctors">
              <DoctorVerificationTable />
            </div>
          )}

          {activeTab === 'audit' && (
            <div className="admin-audit">
              <AuditLedger />
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default AdminDashboard;

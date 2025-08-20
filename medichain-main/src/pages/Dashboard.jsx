/* Dashboard.jsx */
import React, { useEffect, useState } from "react"
import Header from "./Header"
import { Plus, Users, Clock, Activity, CheckCircle, AlertCircle, UserCheck } from "lucide-react"
import { useAuth } from "../context/AuthContext"
import "../assets/styles/Dashboard.css"

// Simple toast replacement
const toast = {
  info: (message) => {
    alert(`ℹ️ ${message}`);
  }
};

const Dashboard = () => {
  const { user } = useAuth(); // Removed refreshProfile
  const [stats, setStats] = useState({
    totalPatients: 0,
    pendingApprovals: 0,
    activeRecords: 0,
    recentActivity: 0
  })

  useEffect(() => {
    // Load dashboard stats (placeholder for now)
    loadDashboardStats()
  }, [])

  const loadDashboardStats = () => {
    // Placeholder stats - in real app, this would fetch from API
    setStats({
      totalPatients: 5,
      pendingApprovals: 2,
      activeRecords: 12,
      recentActivity: 8
    })
  }

  const handleNewPatient = () => {
    toast.info("New Patient feature coming soon!")
  }
  
  return (
    <div className="dashboard-container">
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
        <div className="dashboard-header-section">
          <div className="dashboard-title-section">
            <h1 className="dashboard-title">DASHBOARD</h1>
            {user && (
              <div className="user-welcome">
                <span>Welcome back, <strong>{user.name}</strong></span>
                <span className="user-role">({user.role})</span>
              </div>
            )}
          </div>
          <div className="dashboard-actions">
            <button className="new-patient-btn" onClick={handleNewPatient}>
              <Plus size={20} /> New Patient
            </button>
          </div>
        </div>

        <div className="dashboard-grid">
          <div className="stats-cards-row">
            <div className="stat-card">
              <div className="stat-icon">
                <Users size={32} />
              </div>
              <div className="stat-info">
                <span className="stat-label">Total Patients</span>
                <span className="stat-value">{stats.totalPatients}</span>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">
                <Clock size={32} />
              </div>
              <div className="stat-info">
                <span className="stat-label">Pending Approvals</span>
                <span className="stat-value">{stats.pendingApprovals}</span>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">
                <Activity size={32} />
              </div>
              <div className="stat-info">
                <span className="stat-label">Active Records</span>
                <span className="stat-value">{stats.activeRecords}</span>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">
                <CheckCircle size={32} />
              </div>
              <div className="stat-info">
                <span className="stat-label">Recent Activity</span>
                <span className="stat-value">{stats.recentActivity}</span>
              </div>
            </div>
          </div>

          <div className="main-and-sidebar-grid">
            <div className="main-content-area">
              <div className="content-card">
                <h3>
                  <Activity size={24} />
                  Recent Activity
                </h3>
                <div className="activity-list">
                  <div className="activity-item">
                    <span className="activity-time">2 hours ago</span>
                    <span className="activity-text">New patient record created</span>
                  </div>
                  <div className="activity-item">
                    <span className="activity-time">5 hours ago</span>
                    <span className="activity-text">Medical report updated</span>
                  </div>
                  <div className="activity-item">
                    <span className="activity-time">1 day ago</span>
                    <span className="activity-text">Prescription issued</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="sidebar-area">
              <div className="pending-approvals-card">
                <h3 className="card-title">
                  <AlertCircle size={20} />
                  Pending Approvals
                </h3>
                <div className="approval-item">John Doe - Lab Results</div>
                <div className="approval-item">Jane Smith - Prescription</div>
                {stats.pendingApprovals === 0 && (
                  <div className="approval-item empty">No pending approvals</div>
                )}
              </div>
              <div className="user-info-card">
                <h3 className="card-title">
                  <UserCheck size={20} />
                  User Information
                </h3>
                {user ? (
                  <div className="user-details">
                    <div className="user-detail">
                      <strong>Name:</strong> {user.name || 'N/A'}
                    </div>
                    <div className="user-detail">
                      <strong>Email:</strong> {user.email || 'N/A'}
                    </div>
                    <div className="user-detail">
                      <strong>Role:</strong> {user.role || 'N/A'}
                    </div>
                    <div className="user-detail">
                      <strong>Member since:</strong> {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'Today'}
                    </div>
                  </div>
                ) : (
                  <div className="user-details">
                    <div className="user-detail">Loading user information...</div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default Dashboard
import React, { useEffect, useState } from "react"
import Header from "./Header"
import { Plus, Users, Clock, Activity, CheckCircle, AlertCircle, UserCheck, Brain, FileText, Heart, Calendar } from "lucide-react"
import { useAuth } from "../context/AuthContext"
import { useNavigate } from "react-router-dom"
import "../assets/styles/ModernDashboard.css"
import "../assets/styles/PatientDashboard.css"

// Simple toast replacement
const toast = {
  info: (message) => {
    alert(`ℹ️ ${message}`);
  }
};

const PatientDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalConsultations: 0,
    aiDiagnoses: 0,
    lastCheckup: 0,
    healthScore: 0
  })

  useEffect(() => {
    // Load patient dashboard stats
    loadPatientStats()
  }, [])

  const loadPatientStats = () => {
    // Placeholder stats - in real app, this would fetch from API
    setStats({
      totalConsultations: 3,
      aiDiagnoses: 2,
      lastCheckup: 15, // days ago
      healthScore: 85
    })
  }

  const handleHealthRecord = () => {
    navigate('/health-record')
  }

  const handleAIDiagnosis = () => {
    navigate('/ai-health')
  }

  const handleNewAppointment = () => {
    toast.info("Appointment booking feature coming soon!")
  }
  
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
        <div className="dashboard-header-section">
          <div className="dashboard-title-section">
            <h1 className="dashboard-title">PATIENT DASHBOARD</h1>
            {user && (
              <div className="user-welcome">
                <span>Welcome back, <strong>{user.first_name || user.name}</strong></span>
                <span className="user-role">Patient Portal</span>
              </div>
            )}
          </div>
          <div className="dashboard-actions">
            <button className="primary-action-btn" onClick={handleNewAppointment}>
              <Plus size={20} /> Book Appointment
            </button>
          </div>
        </div>

        <div className="dashboard-grid">
          <div className="stats-cards-row">
            <div className="stat-card patient-stat">
              <div className="stat-icon">
                <Activity size={32} />
              </div>
              <div className="stat-info">
                <span className="stat-label">Total Consultations</span>
                <span className="stat-value">{stats.totalConsultations}</span>
              </div>
            </div>
            
            <div className="stat-card patient-stat">
              <div className="stat-icon">
                <Brain size={32} />
              </div>
              <div className="stat-info">
                <span className="stat-label">AI Diagnoses</span>
                <span className="stat-value">{stats.aiDiagnoses}</span>
              </div>
            </div>
            
            <div className="stat-card patient-stat">
              <div className="stat-icon">
                <Calendar size={32} />
              </div>
              <div className="stat-info">
                <span className="stat-label">Last Checkup</span>
                <span className="stat-value">{stats.lastCheckup} days ago</span>
              </div>
            </div>
            
            <div className="stat-card patient-stat">
              <div className="stat-icon">
                <Heart size={32} />
              </div>
              <div className="stat-info">
                <span className="stat-label">Health Score</span>
                <span className="stat-value">{stats.healthScore}%</span>
              </div>
            </div>
          </div>

          <div className="main-and-sidebar-grid">
            <div className="main-content-area">
              <div className="patient-actions-grid">
                <div className="action-card" onClick={handleHealthRecord}>
                  <div className="action-icon">
                    <FileText size={48} />
                  </div>
                  <div className="action-content">
                    <h3>My Health Record</h3>
                    <p>View your complete medical history, prescriptions, and health reports</p>
                    <span className="action-status">Coming Soon</span>
                  </div>
                </div>

                <div className="action-card" onClick={handleAIDiagnosis}>
                  <div className="action-icon ai-icon">
                    <Brain size={48} />
                  </div>
                  <div className="action-content">
                    <h3>AI Health Assistant</h3>
                    <p>Get instant AI-powered health insights and symptom analysis</p>
                    <span className="action-status available">Available Now</span>
                  </div>
                </div>
              </div>

              <div className="content-card">
                <h3>
                  <Activity size={24} />
                  Recent Health Activity
                </h3>
                <div className="activity-list">
                  <div className="activity-item">
                    <span className="activity-time">2 days ago</span>
                    <span className="activity-text">AI consultation for headache symptoms</span>
                    <span className="activity-status completed">Completed</span>
                  </div>
                  <div className="activity-item">
                    <span className="activity-time">1 week ago</span>
                    <span className="activity-text">Doctor review on flu symptoms</span>
                    <span className="activity-status reviewed">Reviewed</span>
                  </div>
                  <div className="activity-item">
                    <span className="activity-time">2 weeks ago</span>
                    <span className="activity-text">AI diagnosis for cold symptoms</span>
                    <span className="activity-status completed">Completed</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="sidebar-area">
              <div className="health-summary-card">
                <h3 className="card-title">
                  <Heart size={20} />
                  Health Summary
                </h3>
                <div className="health-metrics">
                  <div className="health-metric">
                    <span className="metric-label">Overall Health</span>
                    <div className="metric-value">
                      <div className="health-score-bar">
                        <div 
                          className="health-score-fill" 
                          style={{ width: `${stats.healthScore}%` }}
                        ></div>
                      </div>
                      <span className="metric-text">{stats.healthScore}%</span>
                    </div>
                  </div>
                  <div className="health-metric">
                    <span className="metric-label">Last AI Consultation</span>
                    <span className="metric-text">2 days ago</span>
                  </div>
                  <div className="health-metric">
                    <span className="metric-label">Next Appointment</span>
                    <span className="metric-text">Not scheduled</span>
                  </div>
                </div>
              </div>

              <div className="user-info-card">
                <h3 className="card-title">
                  <UserCheck size={20} />
                  My Information
                </h3>
                {user ? (
                  <div className="user-details">
                    <div className="user-detail">
                      <strong>Name:</strong> {user.first_name ? `${user.first_name} ${user.last_name}` : (user.name || 'N/A')}
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

              <div className="quick-access-card">
                <h3 className="card-title">
                  <Plus size={20} />
                  Quick Actions
                </h3>
                <div className="quick-actions">
                  <button className="quick-action-btn" onClick={handleAIDiagnosis}>
                    <Brain size={16} />
                    Start AI Consultation
                  </button>
                  <button className="quick-action-btn" onClick={handleHealthRecord}>
                    <FileText size={16} />
                    View Health Record
                  </button>
                  <button className="quick-action-btn" onClick={handleNewAppointment}>
                    <Calendar size={16} />
                    Book Appointment
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default PatientDashboard

import React, { useEffect, useState } from "react"
import Header from "./Header"
import { Plus, Activity, Brain, FileText, Heart, Calendar, UserCheck, RefreshCw } from "lucide-react"
import { useAuth } from "../context/AuthContext"
import { useNavigate } from "react-router-dom"
import DatabaseService from "../services/databaseService"
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
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    // Load patient dashboard stats when component mounts or user changes
    if (user?.uid) {
      loadPatientStats()
    }
  }, [user]) // eslint-disable-line react-hooks/exhaustive-deps

  const loadPatientStats = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const result = await DatabaseService.getPatientStats(user.uid)
      
      if (result.success) {
        setStats(result.data)
      } else {
        console.warn('Failed to load patient stats:', result.error)
        setError('Failed to load dashboard statistics')
        // Keep existing stats as fallback
      }
    } catch (err) {
      console.error('Error loading patient stats:', err)
      setError('Error connecting to database')
    } finally {
      setLoading(false)
    }
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
            {user && user.profile && (
              <div className="user-welcome">
                <span>Welcome back, <strong>{user.profile.first_name || user.profile.name}</strong></span>
                <span className="user-role">Patient Portal</span>
              </div>
            )}
            {error && (
              <div className="error-message" style={{ color: '#e74c3c', fontSize: '0.9rem', marginTop: '8px' }}>
                {error} - Using offline data
              </div>
            )}
          </div>
          <div className="dashboard-actions">
            <button className="primary-action-btn" onClick={handleNewAppointment}>
              <Plus size={20} /> Book Appointment
            </button>
            {loading && (
              <div className="loading-indicator" style={{ marginLeft: '10px', fontSize: '0.9rem', color: '#666' }}>
                <RefreshCw size={16} className="spinning" /> Loading stats...
              </div>
            )}
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
                {user && user.profile ? (
                  <div className="user-details">
                    <div className="user-detail">
                      <strong>Name:</strong> {user.profile.first_name ? `${user.profile.first_name} ${user.profile.last_name}` : (user.profile.name || 'N/A')}
                    </div>
                    <div className="user-detail">
                      <strong>Email:</strong> {user.profile.email || user.email || 'N/A'}
                    </div>
                    <div className="user-detail">
                      <strong>Role:</strong> {user.profile.role ? user.profile.role.charAt(0).toUpperCase() + user.profile.role.slice(1) : 'N/A'}
                    </div>
                    <div className="user-detail">
                      <strong>Member since:</strong> {user.profile.created_at ? new Date(user.profile.created_at).toLocaleDateString() : 'Today'}
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

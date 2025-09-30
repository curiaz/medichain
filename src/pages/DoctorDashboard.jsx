import React, { useEffect, useState } from "react"
import Header from "./Header"
import { Users, Activity, AlertCircle, Brain, Stethoscope, RefreshCw } from "lucide-react"
import { useAuth } from "../context/AuthContext"
import { useNavigate } from "react-router-dom"
import DatabaseService from "../services/databaseService"
import VerificationStatus from "../components/VerificationStatus"
import "../assets/styles/ModernDashboard.css"
import "../assets/styles/DoctorDashboard.css"



const DoctorDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalPatients: 0,
    pendingReviews: 0,
    aiConsultations: 0,
    recentActivity: 0
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    // Load doctor dashboard stats when component mounts or user changes
    if (user?.uid) {
      loadDoctorStats()
    }
  }, [user]) // eslint-disable-line react-hooks/exhaustive-deps

  const loadDoctorStats = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const result = await DatabaseService.getDoctorStats(user.uid)
      
      if (result.success) {
        setStats(result.data)
      } else {
        console.warn('Failed to load doctor stats:', result.error)
        setError('Failed to load dashboard statistics')
        // Keep existing stats as fallback
      }
    } catch (err) {
      console.error('Error loading doctor stats:', err)
      setError('Error connecting to database')
    } finally {
      setLoading(false)
    }
  }

  const handlePatientAIHistory = () => {
    navigate('/patient-ai-history')
  }

  const handlePatientList = () => {
    navigate('/patients')
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
            <h1 className="dashboard-title">MEDICAL DASHBOARD</h1>
            {user && user.profile && (
              <div className="user-welcome">
                <span>Welcome, <strong>Dr. {user.profile.first_name || user.profile.name}</strong></span>
                <span className="user-role">LICENSED MEDICAL PRACTITIONER</span>
              </div>
            )}
            
            {/* Doctor Verification Status */}
            <VerificationStatus 
              status={user?.profile?.verification_status || user?.doctor_profile?.verification_status}
              userType={user?.profile?.role}
              doctorProfile={user?.doctor_profile}
            />
            
            {error && (
              <div className="error-message" style={{ color: '#e74c3c', fontSize: '0.9rem', marginTop: '8px' }}>
                {error} - Using offline data
              </div>
            )}
          </div>
          <div className="dashboard-actions">
            {loading && (
              <div className="loading-indicator" style={{ fontSize: '0.9rem', color: '#666' }}>
                <RefreshCw size={16} className="spinning" /> Loading stats...
              </div>
            )}
          </div>
        </div>

        <div className="dashboard-grid">
          <div className="stats-cards-row">
            <div className="stat-card doctor-stat">
              <div className="stat-icon">
                <Users size={32} />
              </div>
              <div className="stat-info">
                <span className="stat-label">ACTIVE PATIENTS</span>
                <span className="stat-value">{stats.totalPatients}</span>
              </div>
            </div>
            
            <div className="stat-card doctor-stat">
              <div className="stat-icon">
                <AlertCircle size={32} />
              </div>
              <div className="stat-info">
                <span className="stat-label">PENDING AI REVIEWS</span>
                <span className="stat-value">{stats.pendingReviews}</span>
              </div>
            </div>
            
            <div className="stat-card doctor-stat">
              <div className="stat-icon">
                <Brain size={32} />
              </div>
              <div className="stat-info">
                <span className="stat-label">AI CONSULTATIONS</span>
                <span className="stat-value">{stats.aiConsultations}</span>
              </div>
            </div>
            
            <div className="stat-card doctor-stat">
              <div className="stat-icon">
                <Activity size={32} />
              </div>
              <div className="stat-info">
                <span className="stat-label">RECENT ACTIVITY</span>
                <span className="stat-value">{stats.recentActivity}</span>
              </div>
            </div>
          </div>

          <div className="main-and-sidebar-grid">
            <div className="main-content-area">
              <div className="doctor-actions-grid">
                <div className="action-card" onClick={handlePatientList}>
                  <div className="action-icon">
                    <Users size={48} />
                  </div>
                  <div className="action-content">
                    <h3>Patient Records</h3>
                    <p>Access patient files, medical history, and treatment plans</p>
                    <span className="action-status">Secure Access</span>
                  </div>
                </div>

                <div className="action-card" onClick={handlePatientAIHistory}>
                  <div className="action-icon ai-icon">
                    <Brain size={48} />
                  </div>
                  <div className="action-content">
                    <h3>AI Diagnostic Reviews</h3>
                    <p>Review AI-assisted diagnoses and validate treatment recommendations</p>
                    <span className="action-status available">Review Required</span>
                  </div>
                </div>
              </div>

              <div className="content-card">
                <h3>
                  <Activity size={24} />
                  Clinical Activity Log
                </h3>
                <div className="activity-list">
                  <div className="activity-item">
                    <span className="activity-time">45 min ago</span>
                    <span className="activity-text">Validated AI diagnosis - Migraine headache</span>
                    <span className="activity-status completed">Approved</span>
                  </div>
                  <div className="activity-item">
                    <span className="activity-time">2 hours ago</span>
                    <span className="activity-text">Treatment plan updated - Hypertension management</span>
                    <span className="activity-status pending">In Progress</span>
                  </div>
                  <div className="activity-item">
                    <span className="activity-time">4 hours ago</span>
                    <span className="activity-text">Lab results reviewed - Blood panel normal</span>
                    <span className="activity-status completed">Reviewed</span>
                  </div>
                  <div className="activity-item">
                    <span className="activity-time">6 hours ago</span>
                    <span className="activity-text">Prescription authorized - Antibiotic therapy</span>
                    <span className="activity-status modified">Dispensed</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="sidebar-area">
              <div className="pending-reviews-card">
                <h3 className="card-title">
                  <AlertCircle size={20} />
                  Clinical Reviews Required
                </h3>
                <div className="review-item">
                  <div className="patient-name">Patient #1024</div>
                  <div className="consultation-info">Tension headache - High confidence</div>
                  <div className="consultation-time">2 hours ago</div>
                  <button className="review-btn" onClick={handlePatientAIHistory}>
                    Validate
                  </button>
                </div>
                <div className="review-item">
                  <div className="patient-name">Patient #1025</div>
                  <div className="consultation-info">Viral syndrome - Very high confidence</div>
                  <div className="consultation-time">4 hours ago</div>
                  <button className="review-btn" onClick={handlePatientAIHistory}>
                    Validate
                  </button>
                </div>
                <div className="review-item">
                  <div className="patient-name">Patient #1026</div>
                  <div className="consultation-info">Chest pain - Moderate confidence</div>
                  <div className="consultation-time">6 hours ago</div>
                  <button className="review-btn urgent" onClick={handlePatientAIHistory}>
                    Priority Review
                  </button>
                </div>
              </div>

              <div className="user-info-card">
                <h3 className="card-title">
                  <Stethoscope size={20} />
                  Doctor Information
                </h3>
                {user && user.profile ? (
                  <div className="user-details">
                    <div className="user-detail">
                      <strong>Name:</strong> Dr. {user.profile.first_name ? `${user.profile.first_name} ${user.profile.last_name}` : (user.profile.name || 'N/A')}
                    </div>
                    <div className="user-detail">
                      <strong>Email:</strong> {user.profile.email || user.email || 'N/A'}
                    </div>
                    <div className="user-detail">
                      <strong>Role:</strong> {user.profile.role ? user.profile.role.charAt(0).toUpperCase() + user.profile.role.slice(1) : 'N/A'}
                    </div>
                    <div className="user-detail">
                      <strong>License:</strong> {user.doctor_profile?.license_number || `MD-${user.uid ? String(user.uid).slice(-6).toUpperCase() : 'XXXXXX'}`}
                    </div>
                  </div>
                ) : (
                  <div className="user-details">
                    <div className="user-detail">Loading doctor information...</div>
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

export default DoctorDashboard;

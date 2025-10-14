import React, { useEffect, useState } from "react"
import Header from "./Header"
import { Users, Activity, AlertCircle, Brain, Stethoscope, RefreshCw, FileText, Calendar, Settings } from "lucide-react"
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

  const handleSettings = () => {
    navigate('/settings')
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
        <div className="dashboard-header-section" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
          <div className="dashboard-title-section" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <h1 className="dashboard-title" style={{ marginBottom: '16px' }}>DOCTOR DASHBOARD</h1>
            {user && user.profile && (
              <div className="user-welcome" style={{ textAlign: 'center' }}>
                <span>Welcome back, <strong>Dr. {user.profile.first_name || user.profile.name}</strong></span>
                <span className="user-role">MEDICAL PROFESSIONAL</span>
              </div>
            )}
            
            {/* Doctor Verification Status */}
            <div style={{ display: 'flex', justifyContent: 'center', marginTop: '12px' }}>
              <VerificationStatus 
                status={user?.profile?.verification_status || user?.doctor_profile?.verification_status}
                userType={user?.profile?.role}
                doctorProfile={user?.doctor_profile}
              />
            </div>
            
            {error && (
              <div className="error-message" style={{ color: '#e74c3c', fontSize: '0.9rem', marginTop: '8px', textAlign: 'center' }}>
                {error} - Using offline data
              </div>
            )}
          </div>
          <div className="dashboard-actions" style={{ display: 'flex', justifyContent: 'center' }}>
            {loading && (
              <div className="loading-indicator" style={{ fontSize: '0.9rem', color: '#666' }}>
                <RefreshCw size={16} className="spinning" /> Loading stats...
              </div>
            )}
          </div>
        </div>

        <div className="dashboard-grid">
          <div className="stats-cards-row">
            <div className="stat-card doctor-stat primary">
              <div className="stat-icon">
                <Users size={32} />
              </div>
              <div className="stat-info">
                <span className="stat-label">My Patients</span>
                <span className="stat-value">{stats.totalPatients}</span>
                <span className="stat-trend">↑ Active care</span>
              </div>
            </div>
            
            <div className="stat-card doctor-stat urgent">
              <div className="stat-icon">
                <AlertCircle size={32} />
              </div>
              <div className="stat-info">
                <span className="stat-label">Pending Reviews</span>
                <span className="stat-value">{stats.pendingReviews}</span>
                <span className="stat-trend">Needs attention</span>
              </div>
            </div>
            
            <div className="stat-card doctor-stat success">
              <div className="stat-icon">
                <Brain size={32} />
              </div>
              <div className="stat-info">
                <span className="stat-label">AI Consultations</span>
                <span className="stat-value">{stats.aiConsultations}</span>
                <span className="stat-trend">Today</span>
              </div>
            </div>
            
            <div className="stat-card doctor-stat info">
              <div className="stat-icon">
                <Activity size={32} />
              </div>
              <div className="stat-info">
                <span className="stat-label">Today's Activity</span>
                <span className="stat-value">{stats.recentActivity}</span>
                <span className="stat-trend">Consultations</span>
              </div>
            </div>
          </div>

          <div className="main-and-sidebar-grid">
            <div className="main-content-area">
              <div className="doctor-actions-grid">
                <div className="action-card primary-action" onClick={handlePatientList}>
                  <div className="action-icon">
                    <Users size={48} />
                  </div>
                  <div className="action-content">
                    <h3>Patient Records</h3>
                    <p>Access comprehensive patient histories, medical records, and treatment plans</p>
                    <span className="action-status available">
                      <span className="status-dot"></span>
                      Ready to Access
                    </span>
                  </div>
                </div>

                <div className="action-card ai-action" onClick={handlePatientAIHistory}>
                  <div className="action-icon ai-icon">
                    <Brain size={48} />
                  </div>
                  <div className="action-content">
                    <h3>AI Diagnosis Review</h3>
                    <p>Review AI-generated diagnoses, validate recommendations, and provide expert oversight</p>
                    <span className="action-status urgent">
                      <span className="status-dot urgent"></span>
                      {stats.pendingReviews} Pending Reviews
                    </span>
                  </div>
                </div>

                <div className="action-card secondary-action">
                  <div className="action-icon">
                    <FileText size={48} />
                  </div>
                  <div className="action-content">
                    <h3>Medical Reports</h3>
                    <p>Generate detailed reports, prescriptions, and treatment summaries</p>
                    <span className="action-status available">
                      <span className="status-dot"></span>
                      Generate Reports
                    </span>
                  </div>
                </div>

                <div className="action-card secondary-action">
                  <div className="action-icon">
                    <Calendar size={48} />
                  </div>
                  <div className="action-content">
                    <h3>Schedule Management</h3>
                    <p>Manage appointments, consultations, and follow-up sessions</p>
                    <span className="action-status info">
                      <span className="status-dot info"></span>
                      View Schedule
                    </span>
                  </div>
                </div>
              </div>

              <div className="content-card activity-card">
                <div className="card-header">
                  <h3>
                    <Activity size={24} />
                    Recent Medical Activity
                  </h3>
                  <button className="view-all-btn">View All</button>
                </div>
                <div className="activity-list">
                  <div className="activity-item high-priority">
                    <div className="activity-icon">
                      <Brain size={16} />
                    </div>
                    <div className="activity-details">
                      <span className="activity-text">AI consultation reviewed for <strong>John Doe</strong></span>
                      <span className="activity-description">Respiratory symptoms - Diagnosis confirmed</span>
                      <span className="activity-time">1 hour ago</span>
                    </div>
                    <span className="activity-status completed">✓ Reviewed</span>
                  </div>
                  <div className="activity-item urgent">
                    <div className="activity-icon">
                      <AlertCircle size={16} />
                    </div>
                    <div className="activity-details">
                      <span className="activity-text">Urgent AI diagnosis for <strong>Jane Smith</strong></span>
                      <span className="activity-description">Cardiac symptoms - Requires immediate review</span>
                      <span className="activity-time">2 hours ago</span>
                    </div>
                    <span className="activity-status pending">Review Now</span>
                  </div>
                  <div className="activity-item normal">
                    <div className="activity-icon">
                      <Users size={16} />
                    </div>
                    <div className="activity-details">
                      <span className="activity-text">Follow-up consultation with <strong>Robert Wilson</strong></span>
                      <span className="activity-description">Diabetes management - Treatment adjusted</span>
                      <span className="activity-time">4 hours ago</span>
                    </div>
                    <span className="activity-status completed">✓ Completed</span>
                  </div>
                  <div className="activity-item normal">
                    <div className="activity-icon">
                      <FileText size={16} />
                    </div>
                    <div className="activity-details">
                      <span className="activity-text">Prescription updated for <strong>Mary Johnson</strong></span>
                      <span className="activity-description">Hypertension medication - Dosage modified</span>
                      <span className="activity-time">6 hours ago</span>
                    </div>
                    <span className="activity-status modified">✓ Updated</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="sidebar-area">
              <div className="pending-reviews-card">
                <h3 className="card-title">
                  <AlertCircle size={20} />
                  Pending AI Reviews
                </h3>
                <div className="review-item">
                  <div className="patient-name">John Doe</div>
                  <div className="consultation-info">Headache symptoms - 85% confidence</div>
                  <div className="consultation-time">2 hours ago</div>
                  <button className="review-btn" onClick={handlePatientAIHistory}>
                    Review
                  </button>
                </div>
                <div className="review-item">
                  <div className="patient-name">Jane Smith</div>
                  <div className="consultation-info">Flu symptoms - 92% confidence</div>
                  <div className="consultation-time">4 hours ago</div>
                  <button className="review-btn" onClick={handlePatientAIHistory}>
                    Review
                  </button>
                </div>
                <div className="review-item">
                  <div className="patient-name">Mike Johnson</div>
                  <div className="consultation-info">Chest pain - 78% confidence</div>
                  <div className="consultation-time">6 hours ago</div>
                  <button className="review-btn urgent" onClick={handlePatientAIHistory}>
                    Review (Urgent)
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
                <button className="settings-btn" onClick={handleSettings} style={{ marginTop: '1rem', width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', padding: '0.75rem', background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)', color: '#fff', border: 'none', borderRadius: '0.75rem', cursor: 'pointer', fontWeight: '600', transition: 'all 0.3s ease' }}>
                  <Settings size={16} />
                  Account Settings
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default DoctorDashboard;

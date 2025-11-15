import React, { useEffect, useState } from "react"
import Header from "./Header"
import { Plus, Activity, FileText, Calendar, User } from "lucide-react"
import { useAuth } from "../context/AuthContext"
import { useNavigate } from "react-router-dom"
import DatabaseService from "../services/databaseService"
import "../assets/styles/ModernDashboard.css"
import "../assets/styles/PatientDashboard.css"


const PatientDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [, setStats] = useState({
    totalConsultations: 0,
    aiDiagnoses: 0,
    lastCheckup: 0,
    healthScore: 0
  })
  const [, setLoading] = useState(true)
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

  const handleNewAppointment = () => {
    navigate('/book-appointment')
  }

  const handleMyAppointments = () => {
    navigate('/my-appointments')
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
                {(() => {
                  const p = user.profile || user;
                  const first = p.first_name || p.firstName || '';
                  const last = p.last_name || p.lastName || '';
                  const name = (first || last) ? `${first} ${last}`.trim() : (p.name || user.displayName || 'User');
                  return (
                    <>
                      <span>Welcome back, <strong>{name}</strong></span>
                      <span className="user-role">Patient</span>
                    </>
                  );
                })()}
              </div>
            )}
            {error && (
              <div className="error-message" style={{ color: '#e74c3c', fontSize: '0.9rem' }}>
                {error} - Using offline data
              </div>
            )}
          </div>
        </div>

        <div className="dashboard-grid">
          <div className="main-and-sidebar-grid">
            <div className="main-content-area">
              <div className="patient-actions-grid">
                <div className="action-card" onClick={handleNewAppointment}>
                  <div className="action-icon appointment-icon">
                    <Calendar size={48} />
                  </div>
                  <div className="action-content">
                    <h3>Book an Appointment</h3>
                    <p>Schedule a consultation with our verified doctors</p>
                    <span className="action-status available">Available Now</span>
                  </div>
                </div>

                <div className="action-card" onClick={handleMyAppointments}>
                  <div className="action-icon">
                    <Calendar size={48} />
                  </div>
                  <div className="action-content">
                    <h3>My Appointments</h3>
                    <p>View scheduled consultations and join video calls</p>
                    <span className="action-status available">Available Now</span>
                  </div>
                </div>

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
              <div className="user-info-card">
                <h3 className="card-title">
                  <User size={20} />
                  My Information
                </h3>
                {user ? (
                  <div className="user-details">
                    {(() => {
                      const p = user.profile || user;
                      const name = p.first_name || p.firstName
                        ? `${p.first_name || p.firstName} ${p.last_name || p.lastName || ''}`.trim()
                        : (p.name || user.displayName || 'N/A');
                      const email = p.email || user.email || 'N/A';
                      const role = (p.role || user.role || 'N/A');
                      const roleCap = typeof role === 'string' ? role.charAt(0).toUpperCase() + role.slice(1) : 'N/A';
                      const createdAt = p.created_at || p.createdAt;
                      const memberSince = createdAt ? new Date(createdAt).toLocaleDateString() : 'Today';
                      return (
                        <>
                          <div className="user-detail">
                            <strong>Name:</strong> {name}
                          </div>
                          <div className="user-detail">
                            <strong>Email:</strong> {email}
                          </div>
                          <div className="user-detail">
                            <strong>Role:</strong> {roleCap}
                          </div>
                          <div className="user-detail">
                            <strong>Member since:</strong> {memberSince}
                          </div>
                        </>
                      );
                    })()}
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

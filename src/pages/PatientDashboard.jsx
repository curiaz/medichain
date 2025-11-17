import React, { useEffect, useState } from "react"
import Header from "./Header"
import { Plus, Activity, FileText, Calendar, User } from "lucide-react"
import { useAuth } from "../context/AuthContext"
import { useNavigate } from "react-router-dom"
import DatabaseService from "../services/databaseService"
import axios from "axios"
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
  const [recentActivities, setRecentActivities] = useState([])

  useEffect(() => {
    // Load patient dashboard stats when component mounts or user changes
    const userUid = user?.uid || user?.firebase_uid || user?.profile?.firebase_uid || user?.id;
    if (userUid) {
      loadPatientStats()
      loadRecentActivities()
    }

    // Listen for appointment booked event to refresh activities
    const handleAppointmentBooked = () => {
      setTimeout(() => {
        loadRecentActivities()
      }, 1500) // Delay to allow backend to process
    }

    window.addEventListener('appointmentBooked', handleAppointmentBooked)

    // Auto-refresh activities every 30 seconds
    const activityInterval = setInterval(() => {
      if (userUid) {
        loadRecentActivities()
      }
    }, 30000)

    return () => {
      window.removeEventListener('appointmentBooked', handleAppointmentBooked)
      clearInterval(activityInterval)
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

  const loadRecentActivities = async () => {
    try {
      const token = localStorage.getItem('medichain_token')
      if (!token) {
        setRecentActivities([])
        return
      }

      const userUid = user?.uid || user?.firebase_uid || user?.profile?.firebase_uid || user?.id;
      if (!userUid) {
        setRecentActivities([])
        return
      }

      const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://medichain.clinic';
      const activities = []

      // Fetch appointments
      try {
        const appointmentsResp = await axios.get(`${API_BASE_URL}/api/appointments`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        
        if (appointmentsResp.data?.success && Array.isArray(appointmentsResp.data.appointments)) {
          const appointments = appointmentsResp.data.appointments.slice(0, 10) // Get last 10
          appointments.forEach(appt => {
            // Use created_at from appointment if available
            const createdDate = appt.created_at || new Date().toISOString()
            activities.push({
              id: `appointment-${appt.id}`,
              type: 'appointment',
              action: 'Booked an appointment',
              description: `Appointment with Dr. ${appt.doctor?.first_name || ''} ${appt.doctor?.last_name || ''}`.trim() || 'Booked an appointment',
              date: createdDate,
              status: appt.status || 'scheduled',
              icon: Calendar
            })
          })
        }
      } catch (apptErr) {
        console.error('Error fetching appointments for activity:', apptErr)
      }

      // Fetch profile to check for updates
      try {
        const profileResp = await axios.get(`${API_BASE_URL}/api/profile/patient`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        
        if (profileResp.data?.success && profileResp.data.profile) {
          const profile = profileResp.data.profile
          const createdDate = profile.created_at || profile.createdAt
          const updatedDate = profile.updated_at || profile.updatedAt
          
          // Check if profile was updated (not just created)
          if (updatedDate && createdDate) {
            const created = new Date(createdDate)
            const updated = new Date(updatedDate)
            const timeDiff = updated.getTime() - created.getTime()
            
            // If updated more than 1 minute after creation, it's an update
            if (timeDiff > 60000) {
              activities.push({
                id: `profile-update-${updatedDate}`,
                type: 'profile',
                action: 'Updated profile',
                description: 'Updated personal information',
                date: updatedDate,
                status: 'completed',
                icon: User
              })
            }
          }
          
          // Add account creation if recent (within last 30 days)
          if (createdDate) {
            const created = new Date(createdDate)
            const now = new Date()
            const daysSinceCreation = (now.getTime() - created.getTime()) / (1000 * 60 * 60 * 24)
            
            if (daysSinceCreation <= 30) {
              activities.push({
                id: `profile-created-${createdDate}`,
                type: 'profile',
                action: 'Account created',
                description: 'Joined MediChain',
                date: createdDate,
                status: 'completed',
                icon: User
              })
            }
          }
        }
      } catch (profileErr) {
        console.error('Error fetching profile for activity:', profileErr)
      }

      // Sort activities by date (newest first)
      activities.sort((a, b) => {
        const dateA = new Date(a.date)
        const dateB = new Date(b.date)
        return dateB - dateA // Newest first
      })

      // Take only the 5 most recent
      setRecentActivities(activities.slice(0, 5))
    } catch (err) {
      console.error('Error loading recent activities:', err)
      setRecentActivities([])
    }
  }

  const formatTimeAgo = (dateStr) => {
    if (!dateStr) return 'Unknown time'
    try {
      const date = new Date(dateStr)
      const now = new Date()
      const diffMs = now - date
      const diffMins = Math.floor(diffMs / 60000)
      const diffHours = Math.floor(diffMs / 3600000)
      const diffDays = Math.floor(diffMs / 86400000)
      const diffWeeks = Math.floor(diffDays / 7)

      if (diffMins < 1) return 'Just now'
      if (diffMins < 60) return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`
      if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`
      if (diffDays < 7) return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`
      if (diffWeeks < 4) return `${diffWeeks} week${diffWeeks !== 1 ? 's' : ''} ago`
      
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined })
    } catch (e) {
      return 'Unknown time'
    }
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
                  {recentActivities.length > 0 ? (
                    recentActivities.map((activity) => {
                      const ActivityIcon = activity.icon || Activity
                      return (
                        <div key={activity.id} className="activity-item">
                          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1 }}>
                            <div style={{
                              width: '36px',
                              height: '36px',
                              borderRadius: '8px',
                              background: activity.type === 'appointment' 
                                ? 'linear-gradient(135deg, #2196F3 0%, #1976D2 100%)'
                                : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              flexShrink: 0
                            }}>
                              <ActivityIcon size={18} color="white" />
                            </div>
                            <div style={{ flex: 1, minWidth: 0 }}>
                              <div className="activity-text" style={{ marginBottom: '4px' }}>
                                {activity.description || activity.action}
                              </div>
                              <span className="activity-time">{formatTimeAgo(activity.date)}</span>
                            </div>
                          </div>
                          <span className={`activity-status ${activity.status === 'scheduled' ? 'pending' : 'completed'}`}>
                            {activity.status === 'scheduled' ? 'Scheduled' : 'Completed'}
                          </span>
                        </div>
                      )
                    })
                  ) : (
                    <div className="activity-item" style={{ justifyContent: 'center', padding: '20px' }}>
                      <span style={{ color: '#64748b', fontSize: '14px' }}>No recent activity</span>
                    </div>
                  )}
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

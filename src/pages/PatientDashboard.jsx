import React, { useEffect, useState } from "react"
import Header from "./Header"
import { Activity, FileText, Calendar, User } from "lucide-react"
import { useAuth } from "../context/AuthContext"
import { useNavigate } from "react-router-dom"
import DatabaseService from "../services/databaseService"
import axios from "axios"
import WelcomePopup from "../components/WelcomePopup"
import OnboardingFormPopup from "../components/OnboardingFormPopup"
import SkipConfirmationPopup from "../components/SkipConfirmationPopup"
import SuccessPopup from "../components/SuccessPopup"
import { API_CONFIG } from "../config/api"
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
  const [showWelcomePopup, setShowWelcomePopup] = useState(false)
  const [showOnboardingForm, setShowOnboardingForm] = useState(false)
  const [showSkipConfirmation, setShowSkipConfirmation] = useState(false)
  const [showSuccessPopup, setShowSuccessPopup] = useState(false)
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    // Load patient dashboard stats when component mounts or user changes
    const userUid = user?.uid || user?.firebase_uid || user?.profile?.firebase_uid || user?.id;
    if (userUid) {
      loadPatientStats()
      loadRecentActivities()
      checkAndShowWelcomePopup()
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

  const checkAndShowWelcomePopup = () => {
    console.log('🔍 Checking welcome popup conditions...');
    
    // FIRST: Check if user just signed up (highest priority - for new accounts)
    const justSignedUp = sessionStorage.getItem('medichain_just_signed_up');
    console.log('🔍 Just signed up flag:', justSignedUp);
    
    if (justSignedUp === 'true') {
      console.log('✅ New signup detected - showing welcome popup');
      sessionStorage.removeItem('medichain_just_signed_up');
      setTimeout(() => {
        setShowWelcomePopup(true);
      }, 500);
      return;
    }

    // SECOND: Check if popup has already been shown for this user
    const welcomeShown = localStorage.getItem('medichain_welcome_shown');
    const onboardingCompleted = localStorage.getItem('medichain_onboarding_completed');
    
    console.log('🔍 Welcome shown:', welcomeShown, 'Onboarding completed:', onboardingCompleted);
    
    if (welcomeShown === 'true' || onboardingCompleted) {
      console.log('ℹ️ Welcome popup already shown or onboarding completed');
      return;
    }

    // THIRD: Check if account was created recently (within last 7 days)
    const userProfile = user?.profile || user;
    const createdAt = userProfile?.created_at || userProfile?.createdAt;
    
    console.log('🔍 User created_at:', createdAt);
    
    if (createdAt) {
      try {
        const createdDate = new Date(createdAt);
        const now = new Date();
        const daysSinceCreation = (now.getTime() - createdDate.getTime()) / (1000 * 60 * 60 * 24);
        
        console.log('🔍 Days since creation:', daysSinceCreation);
        
        // Show popup if account was created within last 7 days
        if (daysSinceCreation <= 7 && daysSinceCreation >= 0) {
          console.log('✅ Account created within 7 days - showing welcome popup');
          // Small delay to ensure dashboard is fully loaded
          setTimeout(() => {
            setShowWelcomePopup(true);
          }, 500);
        } else {
          console.log('ℹ️ Account created more than 7 days ago');
        }
      } catch (e) {
        console.error('Error checking account creation date:', e);
      }
    } else {
      console.log('ℹ️ No created_at date found in user profile');
    }
  }

  const handleGetStarted = () => {
    setShowWelcomePopup(false);
    localStorage.setItem('medichain_welcome_shown', 'true');
    // Show onboarding form
    setShowOnboardingForm(true);
  }

  const handleOnboardingSkip = () => {
    setShowOnboardingForm(false);
    setShowSkipConfirmation(true);
  }

  const handleSkipConfirmationOk = () => {
    setShowSkipConfirmation(false);
    localStorage.setItem('medichain_onboarding_completed', 'skipped');
  }

  const handleOnboardingContinue = async (formData) => {
    setIsSaving(true);
    try {
      const token = localStorage.getItem('medichain_token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const API_BASE_URL = API_CONFIG.API_URL;
      const endpoint = `${API_BASE_URL}/profile/patient/update`;
      
      console.log('Saving onboarding data:', {
        endpoint,
        formData,
        hasToken: !!token
      });
      
      // Save to backend
      const response = await axios.put(
        endpoint,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          timeout: 30000 // 30 second timeout
        }
      );

      console.log('Backend response:', response.data);

      if (response.data?.success) {
        setShowOnboardingForm(false);
        setShowSuccessPopup(true);
        localStorage.setItem('medichain_onboarding_completed', 'completed');
        
        // Update user context if needed
        if (response.data.profile) {
          // Optionally update the user in context
          console.log('Profile updated successfully:', response.data.profile);
        }
      } else {
        throw new Error(response.data?.error || response.data?.message || 'Failed to save profile');
      }
    } catch (error) {
      console.error('Error saving onboarding data:', error);
      
      // Get detailed error message
      let errorMessage = 'Failed to save your information. Please try again later or update it in your profile.';
      
      if (error.response) {
        // Server responded with error status
        const status = error.response.status;
        const data = error.response.data;
        errorMessage = data?.error || data?.message || `Server error (${status}). Please try again.`;
        console.error('Server error response:', { status, data });
      } else if (error.request) {
        // Request was made but no response received
        errorMessage = 'Unable to connect to server. Please check your internet connection and try again.';
        console.error('No response received:', error.request);
      } else {
        // Error setting up the request
        errorMessage = error.message || 'An unexpected error occurred. Please try again.';
        console.error('Request setup error:', error.message);
      }
      
      alert(errorMessage);
      setShowOnboardingForm(false);
    } finally {
      setIsSaving(false);
    }
  }

  const handleSuccessContinue = () => {
    setShowSuccessPopup(false);
    // Just close the popup - user stays on dashboard
    // No reload needed - auth state is preserved
    // Profile data will be refreshed on next component render or when user navigates
  }

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

      const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://medichainn.onrender.com';
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
      {/* Welcome Popup */}
      {showWelcomePopup && (
        <WelcomePopup 
          onGetStarted={handleGetStarted}
        />
      )}

      {/* Onboarding Form Popup */}
      {showOnboardingForm && (
        <OnboardingFormPopup
          onSkip={handleOnboardingSkip}
          onContinue={handleOnboardingContinue}
          user={user}
          isSaving={isSaving}
        />
      )}

      {/* Skip Confirmation Popup */}
      {showSkipConfirmation && (
        <SkipConfirmationPopup
          onOk={handleSkipConfirmationOk}
        />
      )}

      {/* Success Popup */}
      {showSuccessPopup && (
        <SuccessPopup
          onContinue={handleSuccessContinue}
        />
      )}

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
                    <span className="action-status available">View Records</span>
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
          </div>
        </div>
      </main>
    </div>
  )
}

export default PatientDashboard

import React, { useEffect, useState } from "react"
import Header from "./Header"
import { Users, Activity, AlertCircle, Brain, Stethoscope, RefreshCw, FileText, Calendar } from "lucide-react"
import { useAuth } from "../context/AuthContext"
import { useNavigate } from "react-router-dom"
import DatabaseService from "../services/databaseService"
import VerificationStatus from "../components/VerificationStatus"
import axios from "axios"
import { auth } from "../config/firebase"
import "../assets/styles/ModernDashboard.css"
import "../assets/styles/DoctorDashboard.css"

const DoctorDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    pendingReviews: 0,
    aiDiagnosisReviewed: 0,
    todaysActivity: 0
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [recentActivity, setRecentActivity] = useState([])
  // Prioritize doctor_profiles.verification_status over user_profiles.verification_status
  // This is the source of truth for doctor verification
  const verificationStatus = user?.doctor_profile?.verification_status || 
                             (user?.role === 'doctor' ? (user?.profile?.verification_status || 'pending') : null)

  useEffect(() => {
    // Load doctor dashboard stats when component mounts or user changes
    if (user?.uid) {
      loadDoctorStats()
      loadRecentActivity()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user])

  // Listen for medical report saved events to refresh statistics
  useEffect(() => {
    const handleMedicalReportSaved = () => {
      // Refresh statistics when a medical report is saved
      if (user?.uid) {
        loadDoctorStats()
        loadRecentActivity()
      }
    }

    window.addEventListener('medicalReportSaved', handleMedicalReportSaved)
    
    return () => {
      window.removeEventListener('medicalReportSaved', handleMedicalReportSaved)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user])

  const loadDoctorStats = async () => {
    try {
      setLoading(true)
      setError(null)
      console.log('🔍 [DoctorDashboard] Loading stats for doctor:', user.uid)
      const result = await DatabaseService.getDoctorStats(user.uid)
      console.log('🔍 [DoctorDashboard] Stats result:', result)
      if (result.success) {
        console.log('✅ [DoctorDashboard] Stats loaded successfully:', result.data)
        setStats(result.data)
      } else {
        console.warn('❌ [DoctorDashboard] Failed to load dashboard statistics:', result.error)
        setError('Failed to load dashboard statistics')
        // Set default values on error
        setStats({
          pendingReviews: 0,
          aiDiagnosisReviewed: 0,
          todaysActivity: 0
        })
      }
    } catch (err) {
      console.error('❌ [DoctorDashboard] Error loading doctor stats:', err)
      setError('Error connecting to database')
      // Set default values on error
      setStats({
        pendingReviews: 0,
        aiDiagnosisReviewed: 0,
        todaysActivity: 0
      })
    } finally {
      setLoading(false)
    }
  }

  const blockIfUnverified = (actionName) => {
    if (verificationStatus !== 'approved') {
      alert(`Access restricted: Your account is ${verificationStatus || 'pending'}.\n\nPlease wait for verification or check your email for updates.\n\nTrying: ${actionName}`)
      return true
    }
    return false
  }

  const handlePatientList = () => {
    if (blockIfUnverified('Patient List')) return
    navigate('/patients')
  }

  const handleSchedule = () => {
    if (blockIfUnverified('Schedule Management')) return
    navigate('/doctor-schedule')
  }

  const loadRecentActivity = async () => {
    try {
      if (!user?.uid) {
        setRecentActivity([]);
        return;
      }
      
      let token = null;
      try {
        if (auth.currentUser) {
          token = await auth.currentUser.getIdToken(true);
        } else {
          token = localStorage.getItem('medichain_token');
        }
      } catch (err) {
        console.warn('Error getting token:', err);
        token = localStorage.getItem('medichain_token');
      }

      if (!token) {
        console.warn('No authentication token available for recent activity');
        setRecentActivity([]);
        return;
      }

      // Fetch recent medical reports (ordered by updated_at, so updates appear first)
      const response = await axios.get('https://medichainn.onrender.com/api/medical-reports/doctor', {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data?.success && response.data.medical_reports) {
        const reports = response.data.medical_reports || [];
        
        if (reports.length === 0) {
          setRecentActivity([]);
          return;
        }
        
        // Get patient names and format activity items
        const activityItems = await Promise.all(
          reports.slice(0, 5).map(async (report) => {
            try {
              let patientName = 'Unknown Patient';
              
              // Try to get patient name from appointment first
              if (report.appointment_id) {
                try {
                  const appointmentResponse = await axios.get(`https://medichainn.onrender.com/api/appointments/${report.appointment_id}`, {
                    headers: { Authorization: `Bearer ${token}` }
                  });
                  
                  if (appointmentResponse.data?.success && appointmentResponse.data.appointment?.patient) {
                    const appointment = appointmentResponse.data.appointment;
                    patientName = `${appointment.patient?.first_name || ''} ${appointment.patient?.last_name || ''}`.trim() || patientName;
                  }
                } catch (appointmentErr) {
                  // If appointment fetch fails, try to get patient name directly from user_profiles
                  console.warn(`Could not fetch appointment ${report.appointment_id}, trying direct patient lookup:`, appointmentErr.response?.status || appointmentErr.message);
                }
              }
              
              // Fallback 1: Check if patient info is already in the report (from backend join)
              if (patientName === 'Unknown Patient') {
                if (report.user_profiles) {
                  const profile = report.user_profiles;
                  patientName = `${profile.first_name || ''} ${profile.last_name || ''}`.trim() || patientName;
                } else if (report.patient_info) {
                  const profile = report.patient_info;
                  patientName = `${profile.first_name || ''} ${profile.last_name || ''}`.trim() || patientName;
                }
              }
              
              // Fallback 2: Get patient name directly from user_profiles table via backend API
              if (patientName === 'Unknown Patient' && report.patient_firebase_uid) {
                try {
                  // Try to get patient profile via user_profiles endpoint (doctor can query other users)
                  // First, try fetching via appointments endpoint which includes patient info
                  const allAppointmentsResponse = await axios.get('https://medichainn.onrender.com/api/appointments', {
                    headers: { Authorization: `Bearer ${token}` }
                  });
                  
                  if (allAppointmentsResponse.data?.success && allAppointmentsResponse.data.appointments) {
                    const appointments = allAppointmentsResponse.data.appointments || [];
                    // Find appointment with matching patient_firebase_uid
                    const matchingAppointment = appointments.find(apt => 
                      apt.patient_firebase_uid === report.patient_firebase_uid && apt.patient
                    );
                    if (matchingAppointment?.patient) {
                      patientName = `${matchingAppointment.patient.first_name || ''} ${matchingAppointment.patient.last_name || ''}`.trim() || patientName;
                    }
                  }
                  
                  // If still unknown, try fetching patient profile directly from backend
                  if (patientName === 'Unknown Patient') {
                    // Use Supabase service client query via backend - we need a new endpoint for this
                    // For now, try to get from appointment if available
                    if (report.appointment_id) {
                      try {
                        const aptResponse = await axios.get(`https://medichainn.onrender.com/api/appointments/${report.appointment_id}`, {
                          headers: { Authorization: `Bearer ${token}` }
                        });
                        if (aptResponse.data?.success && aptResponse.data.appointment?.patient) {
                          patientName = `${aptResponse.data.appointment.patient.first_name || ''} ${aptResponse.data.appointment.patient.last_name || ''}`.trim() || patientName;
                        }
                      } catch (aptErr) {
                        console.warn(`Could not fetch appointment for patient name:`, aptErr.response?.status || aptErr.message);
                      }
                    }
                  }
                } catch (profileErr) {
                  console.warn(`Could not fetch patient profile for ${report.patient_firebase_uid}:`, profileErr.response?.status || profileErr.message);
                  // Don't show patient ID - just show "Unknown Patient"
                  patientName = 'Unknown Patient';
                }
              }
              
              // Final check: If we still don't have a name, ensure we never show patient ID
              if (patientName === 'Unknown Patient' || (patientName.includes('Patient ') && patientName.includes('...'))) {
                patientName = 'Unknown Patient';
              }
              
              // Determine if it's an update or creation
              const createdAt = report.created_at ? new Date(report.created_at) : new Date();
              const updatedAt = report.updated_at ? new Date(report.updated_at) : createdAt;
              const isUpdated = Math.abs(createdAt.getTime() - updatedAt.getTime()) > 1000; // More than 1 second difference

              const actionText = isUpdated ? 'updated for' : 'created for';
              const timeAgo = getTimeAgo(report.updated_at || report.created_at);
              
              return {
                id: report.id,
                type: 'medical_report',
                patientName: patientName,
                description: report.diagnosis ? `${report.diagnosis.substring(0, 50)}...` : 'Medical report details',
                timeAgo: timeAgo,
                status: 'completed',
                action: actionText
              };
            } catch (err) {
              console.error(`Error processing activity item for report ${report.id}:`, err);
              // Return a basic activity item even if patient name fetch fails
              // NEVER show patient ID - always use "Unknown Patient" as fallback
              const createdAt = report.created_at ? new Date(report.created_at) : new Date();
              const updatedAt = report.updated_at ? new Date(report.updated_at) : createdAt;
              const isUpdated = Math.abs(createdAt.getTime() - updatedAt.getTime()) > 1000;
              
              // Try to get patient name from report data one more time
              let patientName = 'Unknown Patient';
              if (report.user_profiles) {
                const profile = report.user_profiles;
                patientName = `${profile.first_name || ''} ${profile.last_name || ''}`.trim() || patientName;
              } else if (report.patient_info) {
                const profile = report.patient_info;
                patientName = `${profile.first_name || ''} ${profile.last_name || ''}`.trim() || patientName;
              }
              
              return {
                id: report.id,
                type: 'medical_report',
                patientName: patientName, // Never show patient ID
                description: report.diagnosis ? `${report.diagnosis.substring(0, 50)}...` : 'Medical report details',
                timeAgo: getTimeAgo(report.updated_at || report.created_at),
                status: 'completed',
                action: isUpdated ? 'updated for' : 'created for'
              };
            }
          })
        );

        // Filter out null items and ensure we always show activities if reports exist
        const validActivities = activityItems.filter(item => item !== null);
        
        // If we have reports but no valid activities, create basic activities from reports
        if (validActivities.length === 0 && reports.length > 0) {
          console.warn('No valid activity items could be created from reports, creating basic items');
          const basicActivities = reports.slice(0, 5).map(report => {
            const createdAt = report.created_at ? new Date(report.created_at) : new Date();
            const updatedAt = report.updated_at ? new Date(report.updated_at) : createdAt;
            const isUpdated = Math.abs(createdAt.getTime() - updatedAt.getTime()) > 1000;
            
            // Try to get patient name from any available source
            // NEVER show patient ID - always use "Unknown Patient" as fallback
            let patientName = 'Unknown Patient';
            if (report.user_profiles) {
              const profile = report.user_profiles;
              patientName = `${profile.first_name || ''} ${profile.last_name || ''}`.trim() || patientName;
            } else if (report.patient_info) {
              const profile = report.patient_info;
              patientName = `${profile.first_name || ''} ${profile.last_name || ''}`.trim() || patientName;
            }
            // Note: We don't show patient_firebase_uid even as fallback - only show "Unknown Patient"
            
            return {
              id: report.id,
              type: 'medical_report',
              patientName: patientName,
              description: report.diagnosis ? `${report.diagnosis.substring(0, 50)}...` : 'Medical report details',
              timeAgo: getTimeAgo(report.updated_at || report.created_at),
              status: 'completed',
              action: isUpdated ? 'updated for' : 'created for'
            };
          });
          setRecentActivity(basicActivities);
        } else {
          setRecentActivity(validActivities);
        }
      } else {
        console.warn('Failed to fetch medical reports:', response.data?.error || 'Unknown error');
        setRecentActivity([]);
      }
    } catch (err) {
      console.error('Error loading recent activity:', err.response?.data || err.message);
      // Don't set error, just use empty array
      setRecentActivity([]);
    }
  }

  const getTimeAgo = (dateStr) => {
    if (!dateStr) return 'Unknown time';
    try {
      const date = new Date(dateStr);
      const now = new Date();
      const diffMs = now - date;
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMs / 3600000);
      const diffDays = Math.floor(diffMs / 86400000);

      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
      if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
      if (diffDays < 7) return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
      return formatDate(dateStr);
    } catch (e) {
      return 'Unknown time';
    }
  }

  const formatDate = (dateStr) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } catch (e) {
      return dateStr;
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
        <div className="dashboard-header-section" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
          <div className="dashboard-title-section" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <h1 className="dashboard-title" style={{ marginBottom: '16px' }}>DOCTOR DASHBOARD</h1>
            {user && (
              <div className="user-welcome" style={{ textAlign: 'center' }}>
                {(() => {
                  const p = user.profile || user;
                  const first = p.first_name || p.firstName || '';
                  const last = p.last_name || p.lastName || '';
                  const name = (first || last) ? `${first} ${last}`.trim() : (p.name || user.displayName || 'Doctor');
                  return (
                    <>
                      <span>Welcome back, <strong>Dr. {name}</strong></span>
                      <span className="user-role">MEDICAL PROFESSIONAL</span>
                    </>
                  );
                })()}
              </div>
            )}

            {/* Doctor Verification Status */}
            <div style={{ display: 'flex', justifyContent: 'center', marginTop: '12px' }}>
              <VerificationStatus 
                status={verificationStatus}
                userType={user?.role}
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
                <span className="stat-label">AI Diagnosis Reviewed</span>
                <span className="stat-value">{stats.aiDiagnosisReviewed}</span>
                <span className="stat-trend">Total reviewed</span>
              </div>
            </div>
            
            <div className="stat-card doctor-stat info">
              <div className="stat-icon">
                <Activity size={32} />
              </div>
              <div className="stat-info">
                <span className="stat-label">Today's Activity</span>
                <span className="stat-value">{stats.todaysActivity}</span>
                <span className="stat-trend">Patients reviewed</span>
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
                    <h3>Patient List</h3>
                    <p>View and manage your list of patients and their information</p>
                    <span className="action-status available">
                      <span className="status-dot"></span>
                      {verificationStatus === 'approved' ? 'View Patients' : 'Restricted until Approval'}
                    </span>
                  </div>
                </div>

                <div className="action-card primary-action" onClick={() => {
                  if (blockIfUnverified('AI Diagnosis Review')) return;
                  navigate('/doctor-ai-diagnosis');
                }}>
                  <div className="action-icon">
                    <Brain size={48} />
                  </div>
                  <div className="action-content">
                    <h3>AI Diagnosis Review</h3>
                    <p>Review and edit AI-generated diagnoses for your patients</p>
                    <span className="action-status available">
                      <span className="status-dot"></span>
                      {verificationStatus === 'approved' ? `${stats.pendingReviews} Pending Review${stats.pendingReviews !== 1 ? 's' : ''}` : 'Restricted until Approval'}
                    </span>
                  </div>
                </div>

                <div className="action-card secondary-action" onClick={() => {
                  if (blockIfUnverified('Medical Reports')) return;
                  navigate('/doctor-medical-reports');
                }}>
                  <div className="action-icon">
                    <FileText size={48} />
                  </div>
                  <div className="action-content">
                    <h3>Medical Reports</h3>
                    <p>View and manage all your saved medical reports and patient histories</p>
                    <span className="action-status available">
                      <span className="status-dot"></span>
                      {verificationStatus === 'approved' ? 'View Reports' : 'Restricted until Approval'}
                    </span>
                  </div>
                </div>

                <div className="action-card secondary-action" onClick={handleSchedule}>
                  <div className="action-icon">
                    <Calendar size={48} />
                  </div>
                  <div className="action-content">
                    <h3>Schedule Management</h3>
                    <p>Manage appointments, consultations, and follow-up sessions</p>
                    <span className="action-status info">
                      <span className="status-dot info"></span>
                      {verificationStatus === 'approved' ? 'View Schedule' : 'Restricted until Approval'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div className="sidebar-area">
              <div className="content-card activity-card">
                <div className="card-header">
                  <h3>
                    <Activity size={24} />
                    Recent Medical Activity
                  </h3>
                  <button className="view-all-btn" onClick={() => navigate('/doctor-medical-reports')}>
                    View All
                  </button>
                </div>
                <div className="activity-list">
                  {recentActivity.length > 0 && recentActivity.map((activity) => (
                    <div key={activity.id} className="activity-item normal">
                      <div className="activity-icon">
                        <FileText size={16} />
                      </div>
                      <div className="activity-details">
                        <span className="activity-text">Medical report {activity.action} <strong>{activity.patientName}</strong></span>
                        <span className="activity-time">{activity.timeAgo}</span>
                      </div>
                      <span className="activity-status completed">✓ Saved</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="user-info-card">
                <h3 className="card-title">
                  <Stethoscope size={20} />
                  Doctor Information
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
                      const license = user.doctor_profile?.license_number || `MD-${user.uid ? String(user.uid).slice(-6).toUpperCase() : 'XXXXXX'}`;
                      return (
                        <>
                          <div className="user-detail">
                            <strong>Name:</strong> Dr. {name}
                          </div>
                          <div className="user-detail">
                            <strong>Email:</strong> {email}
                          </div>
                          <div className="user-detail">
                            <strong>Role:</strong> {roleCap}
                          </div>
                          <div className="user-detail">
                            <strong>License:</strong> {license}
                          </div>
                        </>
                      );
                    })()}
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

export default DoctorDashboard

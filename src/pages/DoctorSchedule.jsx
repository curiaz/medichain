import React, { useEffect, useState, useCallback } from "react"
import Header from "./Header"
import { Calendar, Clock, User, Video, RefreshCw } from "lucide-react"
import axios from "axios"
import { auth } from "../config/firebase"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import DoctorAvailability from "./DoctorAvailability"
import "../assets/styles/ModernDashboard.css"

const DoctorSchedule = () => {
  const navigate = useNavigate()
  const { user, getFirebaseToken } = useAuth()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [appointments, setAppointments] = useState([])

  // Helper function to extract room name from Jitsi URL
  const extractRoomName = (url) => {
    if (!url) return null
    try {
      // Extract room name from URL like: https://meet.jit.si/medichain-xxx-20240101-1200-abc123
      const match = url.match(/meet\.jit\.si\/([^#\s]+)/)
      return match ? match[1] : null
    } catch (e) {
      return null
    }
  }

  // Handle joining video call
  const handleJoinVideoCall = (meetingUrl) => {
    const roomName = extractRoomName(meetingUrl)
    if (roomName) {
      navigate(`/video/${roomName}`)
    } else {
      // Fallback: open in new tab
      window.open(meetingUrl, '_blank')
    }
  }

  const loadAppointments = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Get authentication token with multiple fallback strategies
      let token = null
      let tokenSource = 'unknown'
      
      // Strategy 1: Try to get Firebase token using AuthContext helper
      try {
        if (getFirebaseToken) {
          token = await getFirebaseToken()
          tokenSource = 'firebase_via_authcontext'
        }
      } catch (authContextError) {
        console.warn("⚠️ DoctorSchedule: Could not get token via AuthContext:", authContextError)
      }
      
      // Strategy 2: Try to get Firebase token from auth.currentUser
      if (!token) {
        try {
          let currentUser = auth.currentUser
          if (!currentUser && user?.uid) {
            await new Promise(resolve => setTimeout(resolve, 500))
            currentUser = auth.currentUser
          }
          
          if (currentUser) {
            token = await currentUser.getIdToken(true)
            tokenSource = 'firebase'
          }
        } catch (firebaseError) {
          console.warn("⚠️ DoctorSchedule: Could not get Firebase token:", firebaseError)
        }
      }
      
      // Strategy 3: Check stored Firebase token
      if (!token) {
        const storedFirebaseToken = sessionStorage.getItem('firebase_id_token') || 
                                    localStorage.getItem('firebase_id_token')
        if (storedFirebaseToken) {
          token = storedFirebaseToken
          tokenSource = 'stored_firebase'
        }
      }
      
      // Fallback to medichain_token
      if (!token) {
        token = localStorage.getItem('medichain_token')
        tokenSource = 'medichain_token'
      }
      
      if (!token) {
        setError("Please log in as a doctor")
        setLoading(false)
        return
      }
      
      console.log(`✅ DoctorSchedule: Token obtained from ${tokenSource}`)
      
      const resp = await axios.get("https://medichain.clinic/api/appointments", {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (resp.data?.success) {
        const appts = Array.isArray(resp.data.appointments) ? resp.data.appointments : []
        
        // Debug: Log patient info and AI diagnosis for each appointment
        appts.forEach((appt, index) => {
          console.log(`📋 Appointment ${index + 1} (ID: ${appt.id}):`, {
            patient_firebase_uid: appt.patient_firebase_uid,
            patient_object: appt.patient,
            has_patient_first_name: !!appt.patient?.first_name,
            has_patient_last_name: !!appt.patient?.last_name,
            has_patient_email: !!appt.patient?.email,
            has_symptoms: !!appt.symptoms,
            symptoms: appt.symptoms,
            has_documents: !!appt.documents,
            has_ai_diagnosis: !!appt.ai_diagnosis,
            ai_diagnosis_processed: appt.ai_diagnosis_processed,
            ai_diagnosis_data: appt.ai_diagnosis ? {
              primary_condition: appt.ai_diagnosis.primary_condition,
              confidence: appt.ai_diagnosis.confidence_score,
              has_detailed_results: !!appt.ai_diagnosis.detailed_results,
              results_count: appt.ai_diagnosis.detailed_results?.length || 0
            } : null
          })
        })
        
        // Sort by date/time ascending
        appts.sort((a, b) => {
          const da = new Date(`${a.appointment_date}T${(a.appointment_time || "00:00").padStart(5, "0")}:00`)
          const db = new Date(`${b.appointment_date}T${(b.appointment_time || "00:00").padStart(5, "0")}:00`)
          return da - db
        })
        setAppointments(appts)
      } else {
        setError(resp.data?.error || "Failed to load appointments")
      }
    } catch (err) {
      setError("Failed to load appointments")
    } finally {
      setLoading(false)
    }
  }, [getFirebaseToken, user?.uid])

  useEffect(() => { loadAppointments() }, [loadAppointments])

  return (
    <div className="dashboard-container fade-in">
      <div className="background-crosses">
        {[...Array(24)].map((_, i) => (
          <span key={i} className={`cross cross-${i + 1}`}>+</span>
        ))}
      </div>

      <Header />

      <main className="dashboard-main-content">
        <div className="dashboard-header-section">
          <div className="dashboard-title-section">
            <h1 className="dashboard-title">SCHEDULE MANAGEMENT</h1>
            <p className="dashboard-subtitle">Upcoming video consultations and availability</p>
          </div>
        </div>

        <div className="dashboard-grid">
          <div className="main-and-sidebar-grid">
            <div className="main-content-area">
                <div className="card-header">
                  <h3>
                    <Calendar size={24} /> Upcoming Appointments
                  </h3>
                  <button className="view-all-btn" onClick={loadAppointments}>
                    <RefreshCw size={16} /> Refresh
                  </button>
                </div>

                {loading ? (
                  <div className="loading-container"><div className="loading-spinner"></div><p>Loading appointments...</p></div>
                ) : error ? (
                  <div className="error-container"><p className="error-message">{error}</p></div>
                ) : appointments.length === 0 ? (
                  <div className="no-availability" style={{ marginTop: 16 }}>
                    <Calendar size={48} />
                    <p>No upcoming appointments</p>
                  </div>
                ) : (
                  <div className="availability-grid">
                    {appointments.map((appt) => {
                    // Parse date and time - handle both string and date formats
                    let appointmentDate = appt.appointment_date
                    let appointmentTime = appt.appointment_time || "00:00"
                    
                    // If appointment_date is a string, parse it
                    if (typeof appointmentDate === 'string') {
                      // Handle date format YYYY-MM-DD
                      appointmentDate = appointmentDate.split('T')[0] // Remove time if present
                    }
                    
                    // Ensure time is in HH:MM format
                    if (typeof appointmentTime === 'string') {
                      appointmentTime = appointmentTime.substring(0, 5) // Take only HH:MM part
                    }
                    
                    // Create date object for formatting
                    let formattedDate = null
                    let formattedTime = null
                    try {
                      const dateStr = `${appointmentDate}T${appointmentTime.padStart(5, "0")}:00`
                      const d = new Date(dateStr)
                      if (!isNaN(d.getTime())) {
                        formattedDate = d.toLocaleDateString('en-US', { 
                          weekday: 'long', 
                          year: 'numeric', 
                          month: 'long', 
                          day: 'numeric' 
                        })
                        formattedTime = d.toLocaleTimeString([], { 
                          hour: '2-digit', 
                          minute: '2-digit',
                          hour12: true 
                        })
                      }
                    } catch (e) {
                      console.error('Error parsing date:', e, appt)
                    }
                    
                    // Get patient name - prefer name over email, never show UID
                      const patient = appt.patient || {}
                    let patientName = 'Patient'
                    
                    // Try to get full name first (handle null, undefined, empty string, whitespace)
                    const firstName = (patient.first_name || "").trim()
                    const lastName = (patient.last_name || "").trim()
                    const fullName = `${firstName} ${lastName}`.trim()
                    
                    if (fullName) {
                      patientName = fullName
                    } else if (patient.email) {
                      // Use email username if name not available
                      const emailUsername = patient.email.split('@')[0]
                      patientName = emailUsername || patient.email
                      console.log(`📧 Using email username for patient: ${patientName} (full email: ${patient.email})`)
                    } else {
                      // Fallback to generic name, never show UID
                      patientName = 'Patient'
                    }
                    
                    // Log if we're missing patient info for debugging
                    if (!fullName && !patient.email) {
                      console.warn('⚠️ Missing patient info for appointment:', appt.id, 'Patient UID:', appt.patient_firebase_uid, 'Patient object:', patient)
                    } else if (!fullName && patient.email) {
                      console.log(`ℹ️ Patient ${appt.id}: Has email (${patient.email}) but no name - using email username: ${patientName}`)
                    }
                    
                      return (
                        <div key={appt.id} className="availability-card">
                          <div className="card-header">
                            <div className="date-info">
                              <Calendar size={20} />
                              <span className="date-text">
                              {formattedDate || appointmentDate || 'Date not available'}
                              </span>
                            </div>
                          </div>
                          <div className="time-slots">
                            <div className="time-slot">
                              <Clock size={16} />
                            <span>{formattedTime || appointmentTime || 'Time not available'}</span>
                            </div>
                            <div className="time-slot">
                              <User size={16} />
                            <span>{patientName}</span>
                            </div>
                          {(appt.meeting_url || appt.meeting_link) && (
                              <div className="time-slot video-consultation">
                                <Video size={16} />
                              <button
                                onClick={() => handleJoinVideoCall(appt.meeting_url || appt.meeting_link)}
                                style={{ 
                                  background: 'none', 
                                  border: 'none', 
                                  color: '#1976D2', 
                                  textDecoration: 'none', 
                                  fontWeight: '500',
                                  cursor: 'pointer',
                                  padding: 0,
                                  fontSize: 'inherit',
                                  fontFamily: 'inherit'
                                }}
                                onMouseOver={(e) => e.target.style.textDecoration = 'underline'}
                                onMouseOut={(e) => e.target.style.textDecoration = 'none'}
                              >
                                Join Video Consultation
                              </button>
                              </div>
                            )}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}
            </div>

            <div className="sidebar-area">
              <div className="content-card">
                <div className="card-header">
                  <h3>
                    <Clock size={24} /> Manage Availability
                  </h3>
                </div>
                {/* Embed the existing availability manager */}
                <div style={{ padding: 0 }}>
                  <DoctorAvailability embedded={true} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default DoctorSchedule



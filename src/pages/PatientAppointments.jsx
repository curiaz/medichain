import React, { useEffect, useState, useCallback } from "react"
import Header from "./Header"
import { Calendar, Clock, Video, User } from "lucide-react"
import axios from "axios"
import { useNavigate } from "react-router-dom"
import "../assets/styles/ModernDashboard.css"

const PatientAppointments = () => {
  const navigate = useNavigate()
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

  const fetchAppointments = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const token = localStorage.getItem('medichain_token')
      if (!token) {
        navigate('/login')
        return
      }
      const resp = await axios.get('http://localhost:5000/api/appointments', {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (resp.data?.success) {
        const appts = Array.isArray(resp.data.appointments) ? resp.data.appointments : []
        appts.sort((a, b) => {
          const da = new Date(`${a.appointment_date}T${(a.appointment_time || "00:00").padStart(5, "0")}:00`)
          const db = new Date(`${b.appointment_date}T${(b.appointment_time || "00:00").padStart(5, "0")}:00`)
          return da - db
        })
        setAppointments(appts)
      } else {
        setError(resp.data?.error || 'Failed to load appointments')
      }
    } catch (e) {
      setError('Failed to load appointments')
    } finally {
      setLoading(false)
    }
  }, [navigate])

  useEffect(() => { fetchAppointments() }, [fetchAppointments])

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
            <h1 className="dashboard-title">MY APPOINTMENTS</h1>
            <p className="dashboard-subtitle">View and join your scheduled online consultations</p>
          </div>
        </div>

        <div className="dashboard-grid">
          <div className="main-and-sidebar-grid">
            <div className="main-content-area">
              <div className="content-card">
                <div className="card-header">
                  <h3>
                    <Calendar size={24} /> Upcoming Appointments
                  </h3>
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
                      
                      // Get doctor name
                      const doctorName = appt.doctor 
                        ? `Dr. ${appt.doctor.first_name || ''} ${appt.doctor.last_name || ''}`.trim()
                        : appt.doctor_name || 'Your doctor'
                      
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
                              <span>{doctorName}</span>
                            </div>
                            {(appt.meeting_url || appt.meeting_link) && (
                              <div className="time-slot" style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                                <Video size={16} />
                                <button
                                  onClick={() => handleJoinVideoCall(appt.meeting_url || appt.meeting_link)}
                                  style={{ 
                                    background: 'none', 
                                    border: 'none', 
                                    color: '#3b82f6', 
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
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default PatientAppointments



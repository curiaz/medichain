import React, { useEffect, useState, useCallback, useMemo } from "react"
import Header from "./Header"
import { Calendar, Clock, Video, User, ArrowUpDown, Star } from "lucide-react"
import axios from "axios"
import { useNavigate } from "react-router-dom"
import RatingModal from "../components/RatingModal"
import { useAuth } from "../context/AuthContext"
import "../assets/styles/ModernDashboard.css"

const PatientAppointments = () => {
  const navigate = useNavigate()
  const { getFirebaseToken } = useAuth()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [appointments, setAppointments] = useState([])
  const [sortOrder, setSortOrder] = useState('newest') // 'newest' or 'oldest'
  const [ratings, setRatings] = useState({}) // Map of appointment_id -> rating
  const [ratingModalOpen, setRatingModalOpen] = useState(false)
  const [selectedAppointment, setSelectedAppointment] = useState(null)

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
      const token = await getFirebaseToken() || localStorage.getItem('medichain_token')
      if (!token) {
        navigate('/login')
        return
      }
      const resp = await axios.get('https://medichainn.onrender.com/api/appointments', {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (resp.data?.success) {
        const appts = Array.isArray(resp.data.appointments) ? resp.data.appointments : []
        // Store appointments without sorting - we'll sort in useMemo based on sortOrder
        setAppointments(appts)
        
        // Fetch ratings for completed appointments
        const completedAppts = appts.filter(apt => apt.status === 'completed')
        const ratingsMap = {}
        
        for (const appt of completedAppts) {
          try {
            const ratingResp = await axios.get(
              `https://medichainn.onrender.com/api/appointments/${appt.id}/rating`,
              { headers: { Authorization: `Bearer ${token}` } }
            )
            if (ratingResp.data?.success && ratingResp.data.rating) {
              ratingsMap[appt.id] = ratingResp.data.rating
            }
          } catch (err) {
            // Rating doesn't exist yet, that's okay
            console.log(`No rating found for appointment ${appt.id}`)
          }
        }
        
        setRatings(ratingsMap)
      } else {
        setError(resp.data?.error || 'Failed to load appointments')
      }
    } catch (e) {
      setError('Failed to load appointments')
    } finally {
      setLoading(false)
    }
  }, [navigate, getFirebaseToken])

  useEffect(() => { fetchAppointments() }, [fetchAppointments])

  // Sort appointments based on selected order
  const sortedAppointments = useMemo(() => {
    if (!appointments.length) {
      console.log('⚠️ No appointments to sort')
      return []
    }
    
    console.log('🔍 Sorting', appointments.length, 'appointments - Current sortOrder:', sortOrder)
    
    const sorted = [...appointments].sort((a, b) => {
      // Handle both string and date formats
      let dateAStr = a.appointment_date
      let dateBStr = b.appointment_date
      
      // If it's already a Date object, convert to string
      if (dateAStr instanceof Date) {
        dateAStr = dateAStr.toISOString().split('T')[0]
      } else if (typeof dateAStr === 'string') {
        dateAStr = dateAStr.split('T')[0] // Remove time if present
      }
      
      if (dateBStr instanceof Date) {
        dateBStr = dateBStr.toISOString().split('T')[0]
      } else if (typeof dateBStr === 'string') {
        dateBStr = dateBStr.split('T')[0] // Remove time if present
      }
      
      // Format time with proper padding
      const timeA = (a.appointment_time || "00:00").toString().padStart(5, "0").substring(0, 5)
      const timeB = (b.appointment_time || "00:00").toString().padStart(5, "0").substring(0, 5)
      
      // Create date strings for comparison
      const dateA = `${dateAStr}T${timeA}:00`
      const dateB = `${dateBStr}T${timeB}:00`
      
      const da = new Date(dateA)
      const db = new Date(dateB)
      
      // Check if dates are valid
      if (isNaN(da.getTime()) || isNaN(db.getTime())) {
        console.warn('⚠️ Invalid date in sorting:', { dateA, dateB, appointmentA: a.id, appointmentB: b.id })
        return 0 // Keep original order if invalid
      }
      
      // For newest: nearest upcoming appointments first (ascending - earliest date first)
      // For oldest: furthest/latest appointments first (descending - latest date first)
      if (sortOrder === 'newest') {
        // Newest = nearest upcoming appointments first (ascending - earliest dates first)
        return da - db
      } else {
        // Oldest = furthest/latest appointments first (descending - latest dates first)
        return db - da
      }
    })
    
    console.log('✅ Sort complete. First appointment:', sorted[0]?.appointment_date, sorted[0]?.appointment_time, 'Last:', sorted[sorted.length - 1]?.appointment_date, sorted[sorted.length - 1]?.appointment_time)
    
    return sorted
  }, [appointments, sortOrder])

  const handleSortChange = (order) => {
    console.log('🔍 Changing sort order from', sortOrder, 'to', order)
    setSortOrder(order)
  }

  const handleOpenRatingModal = (appointment) => {
    setSelectedAppointment(appointment)
    setRatingModalOpen(true)
  }

  const handleCloseRatingModal = () => {
    setRatingModalOpen(false)
    setSelectedAppointment(null)
  }

  const handleSubmitRating = async (ratingData) => {
    try {
      const token = await getFirebaseToken() || localStorage.getItem('medichain_token')
      if (!token) {
        throw new Error("Not authenticated")
      }

      const method = ratings[selectedAppointment.id] ? 'PUT' : 'POST'
      const response = await axios({
        method: method,
        url: `https://medichainn.onrender.com/api/appointments/${selectedAppointment.id}/rating`,
        data: ratingData,
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      })

      if (response.data.success) {
        // Update local ratings state
        setRatings(prev => ({
          ...prev,
          [selectedAppointment.id]: response.data.rating
        }))
        // Refresh appointments to get updated doctor ratings
        fetchAppointments()
      } else {
        throw new Error(response.data.error || "Failed to submit rating")
      }
    } catch (err) {
      throw new Error(err.response?.data?.error || err.message || "Failed to submit rating")
    }
  }

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
          <div style={{ display: 'flex', justifyContent: 'center', width: '100%', maxWidth: '1200px', margin: '0 auto' }}>
            <div style={{ width: '100%', maxWidth: '900px' }}>
              <div className="content-card">
                <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                  <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <Calendar size={24} /> Upcoming Appointments
                  </h3>
                  
                  {/* Sort Filter */}
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '12px',
                    background: '#f5f7fa',
                    padding: '4px',
                    borderRadius: '10px',
                    border: '1px solid #e1e8ed'
                  }}>
                    <ArrowUpDown size={16} color="#64748b" />
                    <button
                      onClick={() => handleSortChange('newest')}
                      style={{
                        padding: '8px 16px',
                        border: 'none',
                        borderRadius: '8px',
                        backgroundColor: sortOrder === 'newest' ? '#2196F3' : 'transparent',
                        color: sortOrder === 'newest' ? 'white' : '#64748b',
                        cursor: 'pointer',
                        fontSize: '14px',
                        fontWeight: sortOrder === 'newest' ? '600' : '500',
                        transition: 'all 0.2s ease',
                        boxShadow: sortOrder === 'newest' ? '0 2px 4px rgba(33, 150, 243, 0.2)' : 'none'
                      }}
                    >
                      Newest
                    </button>
                    <button
                      onClick={() => handleSortChange('oldest')}
                      style={{
                        padding: '8px 16px',
                        border: 'none',
                        borderRadius: '8px',
                        backgroundColor: sortOrder === 'oldest' ? '#2196F3' : 'transparent',
                        color: sortOrder === 'oldest' ? 'white' : '#64748b',
                        cursor: 'pointer',
                        fontSize: '14px',
                        fontWeight: sortOrder === 'oldest' ? '600' : '500',
                        transition: 'all 0.2s ease',
                        boxShadow: sortOrder === 'oldest' ? '0 2px 4px rgba(33, 150, 243, 0.2)' : 'none'
                      }}
                    >
                      Oldest
                    </button>
                  </div>
                </div>

                {loading ? (
                  <div className="loading-container"><div className="loading-spinner"></div><p>Loading appointments...</p></div>
                ) : error ? (
                  <div className="error-container"><p className="error-message">{error}</p></div>
                ) : sortedAppointments.length === 0 ? (
                  <div className="no-availability" style={{ marginTop: 16 }}>
                    <Calendar size={48} />
                    <p>No upcoming appointments</p>
                  </div>
                ) : (
                  <div className="availability-grid">
                    {sortedAppointments.map((appt) => {
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
                            {(appt.meeting_link || appt.meeting_url) && (
                              <div className="time-slot video-consultation">
                                <Video size={16} />
                                <button
                                  onClick={() => handleJoinVideoCall(appt.meeting_link || appt.meeting_url)}
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
                            {appt.status === 'completed' && (
                              <div className="time-slot rating-section">
                                {ratings[appt.id] ? (
                                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                                    <Star size={16} fill="#FFD700" color="#FFD700" />
                                    <span style={{ fontWeight: '500' }}>
                                      Rated {ratings[appt.id].rating}/5
                                    </span>
                                    <button
                                      onClick={() => handleOpenRatingModal(appt)}
                                      style={{
                                        background: 'none',
                                        border: '1px solid #2196F3',
                                        color: '#2196F3',
                                        padding: '4px 12px',
                                        borderRadius: '6px',
                                        cursor: 'pointer',
                                        fontSize: '0.85rem',
                                        fontWeight: '500',
                                        marginLeft: '8px'
                                      }}
                                    >
                                      Edit Rating
                                    </button>
                                  </div>
                                ) : (
                                  <button
                                    onClick={() => handleOpenRatingModal(appt)}
                                    style={{
                                      background: 'linear-gradient(135deg, #2196F3, #00BCD4)',
                                      border: 'none',
                                      color: 'white',
                                      padding: '8px 16px',
                                      borderRadius: '8px',
                                      cursor: 'pointer',
                                      fontSize: '0.9rem',
                                      fontWeight: '600',
                                      display: 'flex',
                                      alignItems: 'center',
                                      gap: '6px'
                                    }}
                                  >
                                    <Star size={16} />
                                    Rate Doctor
                                  </button>
                                )}
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

      {/* Rating Modal */}
      {selectedAppointment && (
        <RatingModal
          isOpen={ratingModalOpen}
          onClose={handleCloseRatingModal}
          appointmentId={selectedAppointment.id}
          doctorName={selectedAppointment.doctor 
            ? `${selectedAppointment.doctor.first_name || ''} ${selectedAppointment.doctor.last_name || ''}`.trim()
            : selectedAppointment.doctor_name || 'Your doctor'}
          onSubmit={handleSubmitRating}
          existingRating={ratings[selectedAppointment.id] || null}
        />
      )}
    </div>
  )
}

export default PatientAppointments



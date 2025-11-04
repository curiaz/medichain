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
                      const d = new Date(`${appt.appointment_date}T${(appt.appointment_time || "00:00").padStart(5, "0")}:00`)
                      return (
                        <div key={appt.id} className="availability-card">
                          <div className="card-header">
                            <div className="date-info">
                              <Calendar size={20} />
                              <span className="date-text">
                                {d.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                              </span>
                            </div>
                          </div>
                          <div className="time-slots">
                            <div className="time-slot">
                              <Clock size={16} />
                              <span>{`${d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`}</span>
                            </div>
                            <div className="time-slot">
                              <User size={16} />
                              <span>With your doctor</span>
                            </div>
                            {appt.meeting_url && (
                              <div className="time-slot" style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                                <Video size={16} />
                                <a href={appt.meeting_url} target="_blank" rel="noreferrer">Join Jitsi Room</a>
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



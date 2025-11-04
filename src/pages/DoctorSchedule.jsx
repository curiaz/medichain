import React, { useEffect, useState } from "react"
import Header from "./Header"
import { Calendar, Clock, User, Video, RefreshCw } from "lucide-react"
import axios from "axios"
import { auth } from "../config/firebase"
import DoctorAvailability from "./DoctorAvailability"
import "../assets/styles/ModernDashboard.css"

const DoctorSchedule = () => {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [appointments, setAppointments] = useState([])

  const loadAppointments = async () => {
    try {
      setLoading(true)
      setError(null)
      const currentUser = auth.currentUser
      if (!currentUser) {
        setError("Please log in as a doctor")
        setLoading(false)
        return
      }
      const token = await currentUser.getIdToken()
      const resp = await axios.get("http://localhost:5000/api/appointments", {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (resp.data?.success) {
        const appts = Array.isArray(resp.data.appointments) ? resp.data.appointments : []
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
  }

  useEffect(() => { loadAppointments() }, [])

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
              <div className="content-card">
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
                      const d = new Date(`${appt.appointment_date}T${(appt.appointment_time || "00:00").padStart(5, "0")}:00`)
                      const patient = appt.patient || {}
                      const pname = `${patient.first_name || ""} ${patient.last_name || ""}`.trim() || patient.email || appt.patient_firebase_uid
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
                              <span>{pname}</span>
                            </div>
                            {appt.meeting_url ? (
                              <div className="time-slot" style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                                <Video size={16} />
                                <a href={appt.meeting_url} target="_blank" rel="noreferrer">Join Jitsi Room</a>
                              </div>
                            ) : (
                              <div className="time-slot">
                                <Video size={16} />
                                <span>Video Conference</span>
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

            <div className="sidebar-area">
              <div className="content-card">
                <div className="card-header">
                  <h3>
                    <Clock size={24} /> Manage Availability
                  </h3>
                </div>
                {/* Embed the existing availability manager */}
                <div style={{ padding: 0 }}>
                  <DoctorAvailability />
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



import React, { useEffect, useState } from "react"
import Header from "./Header"
import { Plus, Users, Clock, Activity, CheckCircle, AlertCircle, UserCheck, Brain, Stethoscope } from "lucide-react"
import { useAuth } from "../context/AuthContext"
import { useNavigate } from "react-router-dom"
import "../assets/styles/ModernDashboard.css"
import "../assets/styles/DoctorDashboard.css"

// Simple toast replacement
const toast = {
  info: (message) => {
    alert(`ℹ️ ${message}`);
  }
};

const DoctorDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalPatients: 0,
    pendingReviews: 0,
    aiConsultations: 0,
    recentActivity: 0
  })

  useEffect(() => {
    // Load doctor dashboard stats
    loadDoctorStats()
  }, [])

  const loadDoctorStats = () => {
    // Placeholder stats - in real app, this would fetch from API
    setStats({
      totalPatients: 24,
      pendingReviews: 3,
      aiConsultations: 12,
      recentActivity: 8
    })
  }

  const handleNewPatient = () => {
    toast.info("New Patient feature coming soon!")
  }

  const handlePatientAIHistory = () => {
    navigate('/patient-ai-history')
  }

  const handlePatientList = () => {
    navigate('/patients')
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
            <h1 className="dashboard-title">DOCTOR DASHBOARD</h1>
            {user && (
              <div className="user-welcome">
                <span>Welcome back, <strong>Dr. {user.first_name || user.name}</strong></span>
                <span className="user-role">Medical Professional</span>
              </div>
            )}
          </div>
          <div className="dashboard-actions">
            <button className="primary-action-btn" onClick={handleNewPatient}>
              <Plus size={20} /> New Patient
            </button>
          </div>
        </div>

        <div className="dashboard-grid">
          <div className="stats-cards-row">
            <div className="stat-card doctor-stat">
              <div className="stat-icon">
                <Users size={32} />
              </div>
              <div className="stat-info">
                <span className="stat-label">Total Patients</span>
                <span className="stat-value">{stats.totalPatients}</span>
              </div>
            </div>
            
            <div className="stat-card doctor-stat">
              <div className="stat-icon">
                <AlertCircle size={32} />
              </div>
              <div className="stat-info">
                <span className="stat-label">Pending AI Reviews</span>
                <span className="stat-value">{stats.pendingReviews}</span>
              </div>
            </div>
            
            <div className="stat-card doctor-stat">
              <div className="stat-icon">
                <Brain size={32} />
              </div>
              <div className="stat-info">
                <span className="stat-label">AI Consultations</span>
                <span className="stat-value">{stats.aiConsultations}</span>
              </div>
            </div>
            
            <div className="stat-card doctor-stat">
              <div className="stat-icon">
                <Activity size={32} />
              </div>
              <div className="stat-info">
                <span className="stat-label">Recent Activity</span>
                <span className="stat-value">{stats.recentActivity}</span>
              </div>
            </div>
          </div>

          <div className="main-and-sidebar-grid">
            <div className="main-content-area">
              <div className="doctor-actions-grid">
                <div className="action-card" onClick={handlePatientList}>
                  <div className="action-icon">
                    <Users size={48} />
                  </div>
                  <div className="action-content">
                    <h3>Patient Management</h3>
                    <p>View and manage your patient list, appointments, and medical records</p>
                    <span className="action-status">Available</span>
                  </div>
                </div>

                <div className="action-card" onClick={handlePatientAIHistory}>
                  <div className="action-icon ai-icon">
                    <Brain size={48} />
                  </div>
                  <div className="action-content">
                    <h3>Patient AI Consultations</h3>
                    <p>Review AI-generated diagnoses and provide professional oversight</p>
                    <span className="action-status available">Available Now</span>
                  </div>
                </div>
              </div>

              <div className="content-card">
                <h3>
                  <Activity size={24} />
                  Recent Activity
                </h3>
                <div className="activity-list">
                  <div className="activity-item">
                    <span className="activity-time">1 hour ago</span>
                    <span className="activity-text">AI consultation reviewed for John Doe</span>
                    <span className="activity-status completed">Completed</span>
                  </div>
                  <div className="activity-item">
                    <span className="activity-time">3 hours ago</span>
                    <span className="activity-text">New AI diagnosis pending review - Jane Smith</span>
                    <span className="activity-status pending">Pending</span>
                  </div>
                  <div className="activity-item">
                    <span className="activity-time">5 hours ago</span>
                    <span className="activity-text">Patient consultation completed</span>
                    <span className="activity-status completed">Completed</span>
                  </div>
                  <div className="activity-item">
                    <span className="activity-time">1 day ago</span>
                    <span className="activity-text">Prescription modified for AI diagnosis</span>
                    <span className="activity-status modified">Modified</span>
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
                {user ? (
                  <div className="user-details">
                    <div className="user-detail">
                      <strong>Name:</strong> Dr. {user.first_name ? `${user.first_name} ${user.last_name}` : (user.name || 'N/A')}
                    </div>
                    <div className="user-detail">
                      <strong>Email:</strong> {user.email || 'N/A'}
                    </div>
                    <div className="user-detail">
                      <strong>Role:</strong> {user.role || 'N/A'}
                    </div>
                    <div className="user-detail">
                      <strong>License:</strong> MD-{user.id ? String(user.id).slice(-6).toUpperCase() : 'XXXXXX'}
                    </div>
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

export default DoctorDashboard;

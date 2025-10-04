import React, { useEffect, useState } from "react"
import Header from "./Header"
import { Users, Search, Calendar, RefreshCw, UserCheck, AlertCircle } from "lucide-react"
import { useAuth } from "../context/AuthContext"
import DatabaseService from "../services/databaseService"
import "../assets/styles/ModernDashboard.css"
import "../assets/styles/DoctorDashboard.css"
import "../assets/styles/PatientList.css"

const PatientList = () => {
  const { user } = useAuth();
  const [patients, setPatients] = useState([])
  const [filteredPatients, setFilteredPatients] = useState([])
  const [searchTerm, setSearchTerm] = useState("")
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    // Load all patients when component mounts
    if (user?.uid) {
      loadAllPatients()
    }
  }, [user])

  useEffect(() => {
    // Filter patients based on search term
    const filtered = patients.filter(patient =>
      patient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      patient.email.toLowerCase().includes(searchTerm.toLowerCase())
    )
    setFilteredPatients(filtered)
  }, [searchTerm, patients])

  const loadAllPatients = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const result = await DatabaseService.getAllPatients()
      
      if (result.success) {
        setPatients(result.data)
        setFilteredPatients(result.data)
      } else {
        console.warn('Failed to load patients:', result.error)
        setError('Failed to load patient list')
      }
    } catch (err) {
      console.error('Error loading patients:', err)
      setError('Error connecting to database')
    } finally {
      setLoading(false)
    }
  }

  const formatJoinedDate = (dateString) => {
    const date = new Date(dateString)
    const options = { 
      year: 'numeric', 
      month: 'long'
    }
    return date.toLocaleDateString('en-US', options)
  }

  const getInitials = (name) => {
    if (!name || name.trim() === '') return 'P'
    const names = name.trim().split(' ')
    if (names.length === 1) return names[0].charAt(0).toUpperCase()
    return (names[0].charAt(0) + names[names.length - 1].charAt(0)).toUpperCase()
  }

  const handleRefresh = () => {
    loadAllPatients()
  }

  const handlePatientClick = (patientId) => {
    // Navigate to patient detail page (to be implemented)
    console.log('Navigate to patient:', patientId)
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
            <h1 className="dashboard-title" style={{ marginBottom: '16px' }}>PATIENT LIST</h1>
            {user && user.profile && (
              <div className="user-welcome" style={{ textAlign: 'center' }}>
                <span>Managing <strong>{filteredPatients.length}</strong> patient{filteredPatients.length !== 1 ? 's' : ''}</span>
                <span className="user-role">PATIENT MANAGEMENT</span>
              </div>
            )}
            
            {error && (
              <div className="error-message" style={{ color: '#e74c3c', fontSize: '0.9rem', marginTop: '8px', textAlign: 'center' }}>
                <AlertCircle size={16} style={{ marginRight: '4px' }} />
                {error}
              </div>
            )}
          </div>
        </div>

        {/* Search and Controls Section */}
        <div className="controls-section" style={{ margin: '24px 0', display: 'flex', justifyContent: 'center', gap: '16px', flexWrap: 'wrap' }}>
          <div className="search-container" style={{ position: 'relative', minWidth: '300px' }}>
            <Search size={20} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} />
            <input
              type="text"
              placeholder="Search patients by name or email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                width: '100%',
                padding: '12px 12px 12px 44px',
                borderRadius: '12px',
                border: '2px solid #e2e8f0',
                fontSize: '14px',
                fontWeight: '500',
                backgroundColor: '#ffffff',
                transition: 'all 0.2s ease',
                outline: 'none'
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#3b82f6'
                e.target.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)'
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#e2e8f0'
                e.target.style.boxShadow = 'none'
              }}
            />
          </div>
          
          <button
            onClick={handleRefresh}
            disabled={loading}
            className="refresh-btn"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 20px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s ease',
              opacity: loading ? 0.7 : 1
            }}
            onMouseOver={(e) => {
              if (!loading) {
                e.target.style.backgroundColor = '#2563eb'
                e.target.style.transform = 'translateY(-1px)'
              }
            }}
            onMouseOut={(e) => {
              e.target.style.backgroundColor = '#3b82f6'
              e.target.style.transform = 'translateY(0)'
            }}
          >
            <RefreshCw size={16} className={loading ? 'spin' : ''} />
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>

        {/* Stats Cards */}
        <div className="stats-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', margin: '24px 0' }}>
          <div className="stat-card modern-card">
            <div className="stat-icon">
              <Users size={32} />
            </div>
            <div className="stat-content">
              <div className="stat-number">{patients.length}</div>
              <div className="stat-label">Total Patients</div>
            </div>
          </div>
          
          <div className="stat-card modern-card">
            <div className="stat-icon" style={{ backgroundColor: '#e0f2fe', color: '#0277bd' }}>
              <UserCheck size={32} />
            </div>
            <div className="stat-content">
              <div className="stat-number">{filteredPatients.length}</div>
              <div className="stat-label">Filtered Results</div>
            </div>
          </div>
          
          <div className="stat-card modern-card">
            <div className="stat-icon" style={{ backgroundColor: '#f3e5f5', color: '#7b1fa2' }}>
              <Calendar size={32} />
            </div>
            <div className="stat-content">
              <div className="stat-number">{patients.filter(p => new Date(p.joined) > new Date(Date.now() - 30*24*60*60*1000)).length}</div>
              <div className="stat-label">New This Month</div>
            </div>
          </div>
        </div>

        {/* Patient List */}
        <div className="patient-list-container" style={{ marginTop: '32px' }}>
          {loading ? (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '60px', flexDirection: 'column', gap: '16px' }}>
              <RefreshCw size={32} className="spin" style={{ color: '#3b82f6' }} />
              <span style={{ color: '#64748b', fontSize: '16px', fontWeight: '500' }}>Loading patients...</span>
            </div>
          ) : filteredPatients.length === 0 ? (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '60px', flexDirection: 'column', gap: '16px' }}>
              <Users size={48} style={{ color: '#cbd5e1' }} />
              <span style={{ color: '#64748b', fontSize: '18px', fontWeight: '500' }}>
                {searchTerm ? `No patients found matching "${searchTerm}"` : 'No patients found'}
              </span>
              {searchTerm && (
                <button
                  onClick={() => setSearchTerm('')}
                  style={{
                    padding: '8px 16px',
                    backgroundColor: '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '14px',
                    cursor: 'pointer'
                  }}
                >
                  Clear Search
                </button>
              )}
            </div>
          ) : (
            <div className="patient-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
              {filteredPatients.map((patient) => (
                <div
                  key={patient.id}
                  className="patient-card modern-card"
                  onClick={() => handlePatientClick(patient.id)}
                  style={{
                    padding: '20px',
                    borderRadius: '16px',
                    backgroundColor: '#ffffff',
                    border: '2px solid #f1f5f9',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    position: 'relative'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.borderColor = '#3b82f6'
                    e.currentTarget.style.transform = 'translateY(-2px)'
                    e.currentTarget.style.boxShadow = '0 8px 25px rgba(0,0,0,0.1)'
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.borderColor = '#f1f5f9'
                    e.currentTarget.style.transform = 'translateY(0)'
                    e.currentTarget.style.boxShadow = '0 2px 10px rgba(0,0,0,0.05)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <div
                      className="patient-avatar"
                      style={{
                        width: '50px',
                        height: '50px',
                        borderRadius: '50%',
                        backgroundColor: '#3b82f6',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'white',
                        fontSize: '18px',
                        fontWeight: '600',
                        flexShrink: 0
                      }}
                    >
                      {patient.avatar_url ? (
                        <img
                          src={patient.avatar_url}
                          alt={patient.name}
                          style={{
                            width: '100%',
                            height: '100%',
                            borderRadius: '50%',
                            objectFit: 'cover'
                          }}
                        />
                      ) : (
                        getInitials(patient.name)
                      )}
                    </div>
                    
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: '16px', fontWeight: '600', color: '#1e293b', marginBottom: '4px' }}>
                        {patient.name || 'Unknown Patient'}
                      </div>
                      <div style={{ fontSize: '14px', color: '#64748b', marginBottom: '8px' }}>
                        {patient.email}
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: '#64748b' }}>
                        <Calendar size={14} />
                        <span>Joined {formatJoinedDate(patient.joined)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default PatientList
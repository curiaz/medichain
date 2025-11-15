import React, { useState, useEffect } from 'react';
import Header from './Header';
import { FileText, Calendar, User, Search, Eye, Download, ArrowLeft } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { auth } from '../config/firebase';
import '../assets/styles/ModernDashboard.css';
import '../assets/styles/DoctorMedicalReports.css';

const DoctorMedicalReports = () => {
  const { user, getFirebaseToken } = useAuth();
  const navigate = useNavigate();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (user?.uid) {
      loadMedicalReports();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  const loadMedicalReports = async () => {
    try {
      setLoading(true);
      setError(null);

      let token = null;
      if (getFirebaseToken) {
        token = await getFirebaseToken();
      } else if (auth.currentUser) {
        token = await auth.currentUser.getIdToken(true);
      } else {
        token = localStorage.getItem('medichain_token');
      }

      if (!token) {
        setError('Authentication required');
        setLoading(false);
        return;
      }

      const response = await axios.get('http://localhost:5000/api/medical-reports/doctor', {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data?.success) {
        const reportsData = response.data.medical_reports || [];
        
        // Fetch patient names for each report
        const reportsWithPatients = await Promise.all(
          reportsData.map(async (report) => {
            try {
              // Get patient info from appointments or user_profiles
              const appointmentsResponse = await axios.get('http://localhost:5000/api/appointments', {
                headers: { Authorization: `Bearer ${token}` }
              });
              
              if (appointmentsResponse.data?.success) {
                const appointments = appointmentsResponse.data.appointments || [];
                const appointment = appointments.find(apt => apt.id === report.appointment_id);
                
                if (appointment?.patient) {
                  return {
                    ...report,
                    patientName: `${appointment.patient.first_name || ''} ${appointment.patient.last_name || ''}`.trim() || 'Unknown Patient',
                    appointmentDate: appointment.appointment_date,
                    appointmentTime: appointment.appointment_time
                  };
                }
              }
              
              return {
                ...report,
                patientName: 'Unknown Patient',
                appointmentDate: report.created_at?.split('T')[0] || '',
                appointmentTime: ''
              };
            } catch (err) {
              console.warn('Error fetching patient info:', err);
              return {
                ...report,
                patientName: 'Unknown Patient',
                appointmentDate: report.created_at?.split('T')[0] || '',
                appointmentTime: ''
              };
            }
          })
        );

        // Sort by date (newest first)
        reportsWithPatients.sort((a, b) => {
          const dateA = new Date(a.created_at || a.appointmentDate);
          const dateB = new Date(b.created_at || b.appointmentDate);
          return dateB - dateA;
        });

        setReports(reportsWithPatients);
        console.log(`✅ Loaded ${reportsWithPatients.length} medical reports`);
      } else {
        setError(response.data?.error || 'Failed to load medical reports');
      }
    } catch (err) {
      console.error('Error loading medical reports:', err);
      setError('Failed to load medical reports. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } catch (e) {
      return dateStr;
    }
  };

  const formatDateTime = (dateStr) => {
    if (!dateStr) return 'N/A';
    try {
      const date = new Date(dateStr);
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (e) {
      return dateStr;
    }
  };

  const filteredReports = reports.filter(report => {
    if (!searchTerm) return true;
    const search = searchTerm.toLowerCase();
    return (
      report.patientName.toLowerCase().includes(search) ||
      report.title?.toLowerCase().includes(search) ||
      report.diagnosis?.toLowerCase().includes(search) ||
      report.record_type?.toLowerCase().includes(search)
    );
  });

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
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <button
                className="back-button"
                onClick={() => navigate('/dashboard')}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  color: '#2196F3',
                  fontSize: '16px'
                }}
              >
                <ArrowLeft size={20} />
                Back
              </button>
              <h1 className="dashboard-title">MEDICAL REPORTS</h1>
            </div>
            <div className="user-welcome">
              <span>View and manage all your saved medical reports</span>
            </div>
          </div>
        </div>

        <div className="medical-reports-container">
          <div className="reports-header">
            <div className="search-section">
              <div className="search-box">
                <Search size={20} />
                <input
                  type="text"
                  placeholder="Search by patient name, diagnosis, or report type..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="search-input"
                />
              </div>
            </div>
            <div className="reports-count">
              {filteredReports.length} report{filteredReports.length !== 1 ? 's' : ''} found
            </div>
          </div>

          {loading ? (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <p>Loading medical reports...</p>
            </div>
          ) : error ? (
            <div className="error-container">
              <p className="error-message">{error}</p>
              <button className="retry-button" onClick={loadMedicalReports}>
                Retry
              </button>
            </div>
          ) : filteredReports.length === 0 ? (
            <div className="no-reports-container">
              <FileText size={64} />
              <h2>No Medical Reports Found</h2>
              <p>
                {searchTerm 
                  ? 'No reports match your search criteria.'
                  : 'You haven\'t created any medical reports yet. Reports will appear here after you review and save AI diagnoses.'}
              </p>
            </div>
          ) : (
            <div className="reports-list">
              {filteredReports.map((report) => (
                <div key={report.id} className="report-card">
                  <div className="report-header">
                    <div className="report-title-section">
                      <FileText size={24} />
                      <div>
                        <h3 className="report-title">{report.title || 'Medical Report'}</h3>
                        <div className="report-meta">
                          <span className="report-patient">
                            <User size={16} />
                            {report.patientName}
                          </span>
                          <span className="report-type">{report.record_type || 'consultation'}</span>
                        </div>
                      </div>
                    </div>
                    <div className="report-date">
                      <Calendar size={16} />
                      <span>{formatDate(report.created_at || report.appointmentDate)}</span>
                    </div>
                  </div>

                  {report.diagnosis && (
                    <div className="report-section">
                      <h4>Diagnosis</h4>
                      <p className="report-diagnosis">{report.diagnosis}</p>
                    </div>
                  )}

                  {report.medications && Array.isArray(report.medications) && report.medications.length > 0 && (
                    <div className="report-section">
                      <h4>Medications</h4>
                      <ul className="medications-list">
                        {report.medications.map((med, idx) => (
                          <li key={idx}>
                            <strong>{med.name || 'Medication'}</strong>
                            {med.dosage && ` - ${med.dosage}`}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {report.treatment_plan && (
                    <div className="report-section">
                      <h4>Treatment Plan</h4>
                      <p className="report-treatment">{report.treatment_plan}</p>
                    </div>
                  )}

                  <div className="report-footer">
                    <div className="report-timestamp">
                      Created: {formatDateTime(report.created_at)}
                    </div>
                    <div className="report-actions">
                      <button
                        className="view-report-btn"
                        onClick={() => {
                          // Navigate to appointment or show full report
                          if (report.appointment_id) {
                            navigate(`/doctor-ai-diagnosis/${report.appointment_id}`);
                          }
                        }}
                      >
                        <Eye size={16} />
                        View Details
                      </button>
                      <button
                        className="download-report-btn"
                        onClick={() => alert('Download functionality coming soon!')}
                      >
                        <Download size={16} />
                        Download
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default DoctorMedicalReports;


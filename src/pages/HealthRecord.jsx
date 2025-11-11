import React, { useState, useEffect } from 'react';
import Header from './Header';
import { FileText, Calendar, Pill, Activity, Download, Stethoscope, File, Brain, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { auth } from '../config/firebase';
import '../assets/styles/ModernDashboard.css';
import '../assets/styles/HealthRecord.css';

const HealthRecord = () => {
  const { user, isAuthenticated, getFirebaseToken } = useAuth();
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [showPrescription, setShowPrescription] = useState(false);

  useEffect(() => {
    if (user?.uid) {
      loadHealthRecords();
    }
  }, [user]);

  const loadHealthRecords = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get authentication token
      let token = null;
      try {
        if (getFirebaseToken) {
          token = await getFirebaseToken();
        } else if (auth.currentUser) {
          token = await auth.currentUser.getIdToken(true);
        } else {
          token = localStorage.getItem('medichain_token');
        }
      } catch (err) {
        console.warn('Token fetch error:', err);
        token = localStorage.getItem('medichain_token');
      }

      if (!token) {
        setError('Please log in to view your health records');
        setLoading(false);
        return;
      }

      // Fetch appointments with symptoms and documents
      const appointmentsResponse = await axios.get('http://localhost:5000/api/appointments', {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (appointmentsResponse.data?.success) {
        const appointments = appointmentsResponse.data.appointments || [];
        
        // Fetch medical reports for all appointments
        const appointmentIds = appointments
          .filter(appt => appt.symptoms && appt.symptoms.length > 0)
          .map(appt => appt.id);

        // Fetch medical reports
        const medicalReportsMap = new Map();
        if (appointmentIds.length > 0) {
          try {
            const reportsResponse = await axios.get('http://localhost:5000/api/medical-reports/patient', {
              headers: { Authorization: `Bearer ${token}` }
            });
            
            if (reportsResponse.data?.success && reportsResponse.data.medical_reports) {
              reportsResponse.data.medical_reports.forEach(report => {
                if (report.appointment_id) {
                  medicalReportsMap.set(report.appointment_id, report);
                }
              });
            }
          } catch (err) {
            console.warn('Error fetching medical reports:', err);
            // Continue without medical reports
          }
        }
        
        // Transform appointments into health records
        const healthRecords = appointments
          .filter(appt => appt.symptoms && appt.symptoms.length > 0) // Only show appointments with symptoms
          .map(appt => {
            const medicalReport = medicalReportsMap.get(appt.id);
            
            return {
              id: appt.id,
              date: appt.appointment_date,
              time: appt.appointment_time,
              doctor: appt.doctor ? {
                name: `Dr. ${appt.doctor.first_name || ''} ${appt.doctor.last_name || ''}`.trim() || 'Doctor',
                specialization: appt.doctor.specialization || 'General Practitioner'
              } : null,
              symptoms: appt.symptoms || [],
              documents: appt.documents || [],
              finalDiagnosis: medicalReport?.diagnosis || null, // Only show if doctor has edited
              prescription: medicalReport ? {
                medications: medicalReport.medications || [],
                instructions: medicalReport.treatment_plan || '',
                duration_days: medicalReport.duration_days || null
              } : null, // Only show if doctor has edited
              notes: appt.notes || '',
              status: appt.status || 'scheduled',
              hasMedicalReport: !!medicalReport // Flag to show if doctor has reviewed
            };
          })
          .sort((a, b) => {
            // Sort by date (newest first)
            const dateA = new Date(`${a.date}T${a.time || '00:00'}`);
            const dateB = new Date(`${b.date}T${b.time || '00:00'}`);
            return dateB - dateA;
          });

        setRecords(healthRecords);
        console.log(`✅ Loaded ${healthRecords.length} health records`);
      } else {
        setError(appointmentsResponse.data?.error || 'Failed to load health records');
      }
    } catch (err) {
      console.error('Error loading health records:', err);
      setError('Failed to load health records. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr, timeStr) => {
    try {
      const date = new Date(`${dateStr}T${timeStr || '00:00'}`);
      return date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (e) {
      return `${dateStr} ${timeStr || ''}`;
    }
  };

  const handleViewPrescription = (record) => {
    setSelectedRecord(record);
    setShowPrescription(true);
  };

  const handleDownloadDocument = (document) => {
    // Placeholder for document download
    alert(`Download functionality will be implemented soon.\n\nDocument: ${document.name}\nSize: ${(document.size / 1024).toFixed(2)} KB`);
  };

  if (!isAuthenticated || !user) {
    return (
      <div className="dashboard-container">
        <Header />
        <div className="error-container">
          <p>Please log in to view your health records</p>
        </div>
      </div>
    );
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
            <h1 className="dashboard-title">MY HEALTH RECORD</h1>
            {user && (
              <div className="user-welcome">
                <span>
                  Health record for <strong>
                    {user.profile?.first_name 
                      ? `${user.profile.first_name} ${user.profile.last_name || ''}`.trim()
                      : user.profile?.name || user.displayName || 'User'}
                  </strong>
                </span>
                <span className="user-role">Medical Records Portal</span>
              </div>
            )}
          </div>
        </div>

        {loading ? (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading your health records...</p>
          </div>
        ) : error ? (
          <div className="error-container">
            <AlertCircle size={48} />
            <p className="error-message">{error}</p>
            <button className="retry-button" onClick={loadHealthRecords}>
              Retry
            </button>
          </div>
        ) : records.length === 0 ? (
          <div className="no-records-container">
            <FileText size={64} />
            <h2>No Health Records Yet</h2>
            <p>Your health records will appear here after you book appointments with symptoms.</p>
            <button 
              className="book-appointment-btn"
              onClick={() => window.location.href = '/book-appointment'}
            >
              Book Your First Appointment
            </button>
          </div>
        ) : (
          <div className="health-records-container">
            <div className="records-header">
              <h2>Your Medical History</h2>
              <p className="records-count">{records.length} record{records.length !== 1 ? 's' : ''} found</p>
            </div>

            <div className="records-list">
              {records.map((record) => (
                <div key={record.id} className="health-record-card">
                  <div className="record-header">
                    <div className="record-date-info">
                      <Calendar size={20} />
                      <div>
                        <div className="record-date">{formatDate(record.date, record.time)}</div>
                        {record.doctor && (
                          <div className="record-doctor">
                            <Stethoscope size={16} />
                            <span>{record.doctor.name} - {record.doctor.specialization}</span>
                          </div>
                        )}
                      </div>
                    </div>
                    <div className={`record-status ${record.status}`}>
                      {record.status.charAt(0).toUpperCase() + record.status.slice(1)}
                    </div>
                  </div>

                  {/* Symptoms Section */}
                  <div className="record-section">
                    <h3 className="section-title">
                      <Activity size={18} />
                      Symptoms Reported
                    </h3>
                    <div className="symptoms-list">
                      {record.symptoms.map((symptom, idx) => (
                        <span key={idx} className="symptom-badge">
                          {symptom}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Final Diagnosis Section - Only show if doctor has reviewed */}
                  {record.finalDiagnosis && (
                    <div className="record-section final-diagnosis-section">
                      <h3 className="section-title">
                        <Brain size={18} />
                        Final Diagnosis
                      </h3>
                      <div className="final-diagnosis-content">
                        <p className="diagnosis-text">{record.finalDiagnosis}</p>
                      </div>
                    </div>
                  )}

                  {/* Documents Section */}
                  {record.documents && record.documents.length > 0 && (
                    <div className="record-section">
                      <h3 className="section-title">
                        <File size={18} />
                        Lab Test Results & Documents ({record.documents.length})
                      </h3>
                      <div className="documents-list">
                        {record.documents.map((doc, idx) => (
                          <div key={idx} className="document-item">
                            <FileText size={16} />
                            <div className="document-info">
                              <span className="document-name">{doc.name}</span>
                              <span className="document-size">
                                {doc.size ? `${(doc.size / 1024).toFixed(2)} KB` : 'Unknown size'}
                              </span>
                            </div>
                            <button
                              className="download-doc-btn"
                              onClick={() => handleDownloadDocument(doc)}
                              title="Download document"
                            >
                              <Download size={16} />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Notes Section */}
                  {record.notes && (
                    <div className="record-section">
                      <h3 className="section-title">
                        <FileText size={18} />
                        Notes
                      </h3>
                      <p className="record-notes">{record.notes}</p>
                    </div>
                  )}

                  {/* Prescription Section - Only show if doctor has reviewed */}
                  {record.prescription && record.prescription.medications?.length > 0 && (
                    <div className="record-actions">
                      <button
                        className="view-prescription-btn"
                        onClick={() => handleViewPrescription(record)}
                      >
                        <Pill size={18} />
                        View Prescription
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Prescription Modal */}
      {showPrescription && selectedRecord && (
        <div className="prescription-modal-overlay" onClick={() => setShowPrescription(false)}>
          <div className="prescription-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>
                <Pill size={24} />
                Prescription
              </h2>
              <button
                className="close-modal-btn"
                onClick={() => setShowPrescription(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-content">
              <div className="prescription-info">
                <div className="prescription-date">
                  <Calendar size={18} />
                  <span>{formatDate(selectedRecord.date, selectedRecord.time)}</span>
                </div>
                {selectedRecord.doctor && (
                  <div className="prescription-doctor">
                    <Stethoscope size={18} />
                    <span>{selectedRecord.doctor.name}</span>
                  </div>
                )}
              </div>

              {/* Prescription Content - From medical report */}
              {selectedRecord.prescription && selectedRecord.prescription.medications?.length > 0 ? (
                <div className="prescription-details">
                  <h3>Medication</h3>
                  {selectedRecord.prescription.medications.map((med, idx) => (
                    <div key={idx} className="medication-item">
                      <strong>{med.name || 'Medication'}</strong>
                      {med.dosage && (
                        <p className="dosage">Dosage: {med.dosage}</p>
                      )}
                      {med.duration && (
                        <p className="duration">Duration: {med.duration}</p>
                      )}
                    </div>
                  ))}
                  {selectedRecord.prescription.instructions && (
                    <div className="prescription-instructions">
                      <h3>Instructions</h3>
                      <p>{selectedRecord.prescription.instructions}</p>
                    </div>
                  )}
                  {selectedRecord.prescription.duration_days && (
                    <div className="prescription-duration">
                      <strong>Treatment Duration:</strong> {selectedRecord.prescription.duration_days} days
                    </div>
                  )}
                </div>
              ) : (
                <div className="no-prescription">
                  <Pill size={48} />
                  <p>No prescription available for this record.</p>
                  <p className="prescription-note">
                    Prescription will be added by your doctor after consultation.
                  </p>
                </div>
              )}

              <div className="prescription-disclaimer">
                <AlertCircle size={16} />
                <p>This is a preliminary prescription based on AI diagnosis. Please consult with your doctor before taking any medication.</p>
              </div>
            </div>
            <div className="modal-footer">
              <button
                className="close-btn"
                onClick={() => setShowPrescription(false)}
              >
                Close
              </button>
              <button
                className="download-prescription-btn"
                onClick={() => alert('Download prescription functionality coming soon!')}
              >
                <Download size={18} />
                Download Prescription
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HealthRecord;

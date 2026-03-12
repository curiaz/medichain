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
  const [userProfile, setUserProfile] = useState(null);

  // Load user profile from database if not already loaded
  useEffect(() => {
    const loadUserProfile = async () => {
      if (!user?.uid) return;

      // Check if profile data is already available
      const hasProfileData = user.profile?.first_name || user.first_name;
      
      if (!hasProfileData) {
        try {
          // Get token for authentication
          let token = null;
          try {
            if (getFirebaseToken) {
              token = await getFirebaseToken();
            }
          } catch (authError) {
            console.warn("Could not get Firebase token:", authError);
          }

          if (!token) {
            token = sessionStorage.getItem('firebase_id_token') || 
                    localStorage.getItem('firebase_id_token') ||
                    localStorage.getItem('medichain_token');
          }

          if (token) {
            // Fetch user profile from backend
            const response = await axios.get('https://medichainn.onrender.com/api/profile', {
              headers: { Authorization: `Bearer ${token}` }
            });

            if (response.data?.success && response.data?.user) {
              setUserProfile(response.data.user);
              console.log('✅ Loaded user profile from database:', response.data.user);
            }
          }
        } catch (err) {
          console.warn('Could not load user profile:', err);
          // Continue without profile - will use fallback names
        }
      } else {
        // Profile data already available in user object
        setUserProfile(user);
      }
    };

    loadUserProfile();
  }, [user, getFirebaseToken]);

  useEffect(() => {
    const userUid = user?.uid || user?.firebase_uid || user?.profile?.firebase_uid || user?.id;
    if (userUid) {
      loadHealthRecords();
    } else {
      // If user exists but no UID found, still try to load (might work with token)
      if (user) {
        console.log('⚠️ HealthRecord: User exists but no UID found, attempting to load anyway');
        loadHealthRecords();
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  const loadHealthRecords = async () => {
    try {
      setLoading(true);
      setError(null);

      console.log('🔍 HealthRecord: Loading health records, user:', user);

      // Get authentication token
      let token = null;
      try {
        // Try Firebase token first
        if (getFirebaseToken) {
          try {
            token = await getFirebaseToken();
            console.log('✅ HealthRecord: Got Firebase token');
          } catch (firebaseErr) {
            console.warn('⚠️ HealthRecord: Could not get Firebase token:', firebaseErr);
          }
        }
        
        // Fallback to auth.currentUser
        if (!token && auth.currentUser) {
          try {
            token = await auth.currentUser.getIdToken(true);
            console.log('✅ HealthRecord: Got token from auth.currentUser');
          } catch (authErr) {
            console.warn('⚠️ HealthRecord: Could not get token from auth.currentUser:', authErr);
          }
        }
        
        // Final fallback to medichain_token
        if (!token) {
          token = localStorage.getItem('medichain_token');
          if (token) {
            console.log('✅ HealthRecord: Using medichain_token');
          }
        }
      } catch (err) {
        console.warn('⚠️ HealthRecord: Token fetch error:', err);
        token = localStorage.getItem('medichain_token');
      }

      if (!token) {
        console.error('❌ HealthRecord: No authentication token available');
        setError('Please log in to view your health records');
        setLoading(false);
        return;
      }

      console.log('🔍 HealthRecord: Fetching appointments...');

      // Fetch appointments with symptoms and documents
      let appointmentsResponse;
      try {
        appointmentsResponse = await axios.get('https://medichainn.onrender.com/api/appointments', {
          headers: { Authorization: `Bearer ${token}` },
          timeout: 10000 // 10 second timeout
        });
        console.log('✅ HealthRecord: Appointments response:', appointmentsResponse.data);
      } catch (apptErr) {
        console.error('❌ HealthRecord: Error fetching appointments:', apptErr);
        if (apptErr.response) {
          console.error('   Response status:', apptErr.response.status);
          console.error('   Response data:', apptErr.response.data);
        }
        setError(`Failed to load appointments: ${apptErr.response?.data?.error || apptErr.message}`);
        setLoading(false);
        return;
      }

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
            const reportsResponse = await axios.get('https://medichainn.onrender.com/api/medical-reports/patient', {
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
        console.log(`✅ HealthRecord: Loaded ${healthRecords.length} health records`);
      } else {
        const errorMsg = appointmentsResponse.data?.error || 'Failed to load health records';
        console.error('❌ HealthRecord: Appointments response was not successful:', errorMsg);
        setError(errorMsg);
      }
    } catch (err) {
      console.error('❌ HealthRecord: Error loading health records:', err);
      if (err.response) {
        console.error('   Response status:', err.response.status);
        console.error('   Response data:', err.response.data);
      }
      setError(`Failed to load health records: ${err.response?.data?.error || err.message}`);
    } finally {
      console.log('🏁 HealthRecord: Loading complete, setting loading to false');
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

  const handleDownloadPrescription = async (record) => {
    try {
      // Dynamically import jsPDF and qrcode
      const { default: jsPDF } = await import('jspdf');
      const QRCode = await import('qrcode');
      
      const doc = new jsPDF();
      const pageWidth = doc.internal.pageSize.getWidth();
      const pageHeight = doc.internal.pageSize.getHeight();
      const margin = 20;
      // Space reserved for footer (QR, signature, ID)
      let yPos = margin;

      // Header - MediChain branding (compact)
      doc.setFillColor(33, 150, 243);
      doc.rect(0, 0, pageWidth, 28, 'F');
      
      doc.setTextColor(255, 255, 255);
      doc.setFontSize(20);
      doc.setFont('helvetica', 'bold');
      doc.text('MEDICHAIN', pageWidth / 2, 14, { align: 'center' });
      
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      doc.text('E-Prescription System', pageWidth / 2, 22, { align: 'center' });

      yPos = 40;

      // Prescribing Physician Section (stacked layout)
      doc.setTextColor(0, 0, 0);
      doc.setFontSize(12);
      doc.setFont('helvetica', 'bold');
      doc.text('Prescribing Physician:', margin, yPos);
      
      yPos += 7;
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      if (record.doctor) {
        doc.text(`Dr. ${record.doctor.name}`, margin, yPos);
        yPos += 6;
        doc.text(`Specialization: ${record.doctor.specialization}`, margin, yPos);
      }

      yPos += 12;

      // Patient Information Section (stacked layout)
      // Use userProfile if loaded, otherwise fall back to user object
      const profileData = userProfile || user;
      
      // Try multiple locations for patient name
      const firstName = profileData?.profile?.first_name || profileData?.first_name || profileData?.profile?.firstName || '';
      const lastName = profileData?.profile?.last_name || profileData?.last_name || profileData?.profile?.lastName || '';
      const patientName = firstName && lastName 
        ? `${firstName} ${lastName}`.trim()
        : profileData?.profile?.name || profileData?.name || profileData?.displayName || profileData?.email?.split('@')[0] || 'Patient';

      // Get patient date of birth
      let patientDOB = 'N/A';
      if (record.appointment_id) {
        try {
          let token = null;
          if (getFirebaseToken) {
            token = await getFirebaseToken();
          } else if (auth.currentUser) {
            token = await auth.currentUser.getIdToken(true);
          } else {
            token = localStorage.getItem('medichain_token');
          }

          if (token) {
            const appointmentResponse = await axios.get(
              `https://medichainn.onrender.com/api/appointments/${record.appointment_id}`,
              { headers: { Authorization: `Bearer ${token}` } }
            );
            
            if (appointmentResponse.data?.success && appointmentResponse.data.appointment?.patient) {
              const patient = appointmentResponse.data.appointment.patient;
              if (patient.date_of_birth) {
                patientDOB = new Date(patient.date_of_birth).toLocaleDateString('en-US', {
                  month: '2-digit',
                  day: '2-digit',
                  year: 'numeric'
                });
              }
            }
          }
        } catch (err) {
          console.warn('Could not fetch patient DOB:', err);
        }
      }

      doc.setFontSize(12);
      doc.setFont('helvetica', 'bold');
      doc.text('Patient Information:', margin, yPos);
      
      yPos += 7;
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      doc.text(`Name: ${patientName}`, margin, yPos);
      yPos += 6;
      doc.text(`Date of Birth: ${patientDOB}`, margin, yPos);
      yPos += 6;
      doc.text(`Date: ${formatDate(record.date, record.time)}`, margin, yPos);

      yPos += 12;

      // Diagnosis Section
      if (record.finalDiagnosis) {
        doc.setFontSize(12);
        doc.setFont('helvetica', 'bold');
        doc.text('Diagnosis:', margin, yPos);
        yPos += 7;
        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        const diagnosisLines = doc.splitTextToSize(record.finalDiagnosis, pageWidth - 2 * margin);
        doc.text(diagnosisLines, margin, yPos);
        yPos += diagnosisLines.length * 5 + 10;
      }

      // Prescription Section
      doc.setFontSize(12);
      doc.setFont('helvetica', 'bold');
      doc.text('Prescription:', margin, yPos);
      yPos += 8;

      // Draw table header
      doc.setFillColor(233, 242, 253);
      doc.rect(margin, yPos - 6, pageWidth - 2 * margin, 8, 'F');
      
      doc.setFontSize(10);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(0, 0, 0);
      doc.text('Medication', margin + 2, yPos);
      doc.text('Dosage', margin + 80, yPos);
      doc.text('Duration', margin + 130, yPos);
      
      yPos += 10;

      // Medication rows
      if (record.prescription && record.prescription.medications) {
        record.prescription.medications.forEach((med, idx) => {
          doc.setFontSize(10);
          doc.setFont('helvetica', 'normal');
          doc.setTextColor(0, 0, 0);
          
          // Medication name
          const medName = med.name || 'Medication';
          const nameLines = doc.splitTextToSize(medName, 70);
          doc.text(nameLines, margin + 2, yPos);
          
          // Dosage
          if (med.dosage) {
            const dosageLines = doc.splitTextToSize(med.dosage, 40);
            doc.text(dosageLines, margin + 80, yPos);
          }
          
          // Duration
          if (med.duration) {
            doc.text(med.duration, margin + 130, yPos);
          }

          yPos += Math.max(nameLines.length * 5, 8);
          
          // Draw separator line
          doc.setDrawColor(200, 200, 200);
          doc.line(margin, yPos - 2, pageWidth - margin, yPos - 2);
          yPos += 4;
        });
      }

      // Instructions Section
      if (record.prescription && record.prescription.instructions) {
        yPos += 8;
        doc.setFontSize(12);
        doc.setFont('helvetica', 'bold');
        doc.text('Instructions:', margin, yPos);
        yPos += 7;
        
        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        const instructionLines = doc.splitTextToSize(record.prescription.instructions, pageWidth - 2 * margin);
        doc.text(instructionLines, margin, yPos);
        yPos += instructionLines.length * 5 + 4;
      }

      // Generate QR Code with secure URL pointing to verification page
      // The URL contains the appointment ID which is used to verify the prescription
      const baseUrl = window.location.origin;
      const verificationUrl = `${baseUrl}/verify-prescription/${record.id}`;
      
      const qrCodeDataUrl = await QRCode.toDataURL(verificationUrl, {
        width: 50,
        margin: 1,
        color: {
          dark: '#000000',
          light: '#FFFFFF'
        }
      });

      // Footer area - Add QR code, signature, ID, and time at the bottom
      // This is added after all content, so it won't affect the main layout
      const footerY = pageHeight - 45;
      
      // QR Code on bottom left (without label)
      doc.addImage(qrCodeDataUrl, 'PNG', margin, footerY, 35, 35);

      // Doctor signature on bottom right (centered)
      const signatureX = pageWidth - margin - 60;
      const signatureText = 'Doctor\'s Signature';
      const signatureTextWidth = doc.getTextWidth(signatureText);
      const signatureLineX = signatureX + (55 - signatureTextWidth) / 2;
      
      doc.setFontSize(9);
      doc.setFont('helvetica', 'normal');
      doc.line(signatureLineX, footerY + 25, signatureLineX + signatureTextWidth, footerY + 25);
      doc.text(signatureText, signatureX + (55 - signatureTextWidth) / 2, footerY + 32);

      // Prescription ID and timestamp at the very bottom (centered)
      const bottomY = pageHeight - 8;
      doc.setFontSize(8);
      doc.setTextColor(128, 128, 128);
      const prescriptionId = `Prescription ID: ${record.id.substring(0, 8)}`;
      const generatedTime = `Generated: ${new Date().toLocaleString()}`;
      const idWidth = doc.getTextWidth(prescriptionId);
      const timeWidth = doc.getTextWidth(generatedTime);
      
      // Center the text at bottom
      doc.text(prescriptionId, (pageWidth - idWidth) / 2, bottomY);
      doc.text(generatedTime, (pageWidth - timeWidth) / 2, bottomY + 4);

      // Save PDF
      const fileName = `prescription_${record.id.substring(0, 8)}_${new Date().toISOString().split('T')[0]}.pdf`;
      doc.save(fileName);
    } catch (error) {
      console.error('Error generating prescription PDF:', error);
      alert('Error generating prescription. Please install required packages: npm install jspdf qrcode');
    }
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
            {user && (() => {
              // Use userProfile if loaded, otherwise fall back to user object
              const profileData = userProfile || user;
              
              // Try multiple locations for user name
              const firstName = profileData.profile?.first_name || profileData.first_name || profileData.profile?.firstName || '';
              const lastName = profileData.profile?.last_name || profileData.last_name || profileData.profile?.lastName || '';
              const fullName = firstName && lastName 
                ? `${firstName} ${lastName}`.trim()
                : profileData.profile?.name || profileData.name || profileData.displayName || profileData.email?.split('@')[0] || 'User';
              
              return (
                <div className="user-welcome">
                  <span>
                    Health record for <strong>{fullName}</strong>
                  </span>
                  <span className="user-role">Medical Records Portal</span>
                </div>
              );
            })()}
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
                  <div className="prescription-section-header">
                    <Pill size={20} />
                    <h3>Medication</h3>
                  </div>
                  <div className="medications-list">
                    {selectedRecord.prescription.medications.map((med, idx) => (
                      <div key={idx} className="medication-item">
                        <div className="medication-content">
                          <div className="medication-name-section">
                            <strong className="medication-name">{med.name || 'Medication'}</strong>
                          </div>
                          <div className="medication-info-section">
                            {med.dosage && (
                              <div className="medication-info-item">
                                <span className="info-label">DOSAGE:</span>
                                <span className="info-value">{med.dosage}</span>
                              </div>
                            )}
                            {med.duration && (
                              <div className="medication-info-item">
                                <span className="info-label">DURATION:</span>
                                <span className="info-value">{med.duration}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  {selectedRecord.prescription.instructions && (
                    <div className="prescription-instructions">
                      <div className="instructions-header">
                        <Activity size={18} />
                        <h3>Instructions</h3>
                      </div>
                      <div className="instructions-content">
                        <p>{selectedRecord.prescription.instructions}</p>
                      </div>
                    </div>
                  )}
                  
                  {selectedRecord.prescription.duration_days && (
                    <div className="prescription-duration-info">
                      <Calendar size={16} />
                      <span><strong>Treatment Duration:</strong> {selectedRecord.prescription.duration_days} days</span>
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
            </div>
            <div className="modal-footer">
              <button
                className="download-prescription-btn"
                onClick={() => handleDownloadPrescription(selectedRecord)}
              >
                <Download size={18} />
                Download Prescription
              </button>
              <button
                className="close-btn"
                onClick={() => setShowPrescription(false)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HealthRecord;

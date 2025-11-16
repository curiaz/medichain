import React, { useState, useEffect } from 'react';
import Header from './Header';
import { FileText, Calendar, User, Search, Eye, Download, ArrowLeft } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { auth } from '../config/firebase';
import { API_CONFIG } from '../config/api';
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

      const response = await axios.get(`${API_CONFIG.API_URL}/medical-reports/doctor`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data?.success) {
        const reportsData = response.data.medical_reports || [];
        
        // Fetch patient names for each report
        const reportsWithPatients = await Promise.all(
          reportsData.map(async (report) => {
            try {
              // Get patient info from appointments or user_profiles
              const appointmentsResponse = await axios.get(`${API_CONFIG.API_URL}/appointments`, {
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

  const handleDownloadMedicalReport = async (report) => {
    try {
      // Dynamically import jsPDF
      const { default: jsPDF } = await import('jspdf');
      
      const doc = new jsPDF();
      const pageWidth = doc.internal.pageSize.getWidth();
      const pageHeight = doc.internal.pageSize.getHeight();
      const margin = 20;
      let yPos = margin;

      // Header - Title
      doc.setFillColor(33, 150, 243);
      doc.rect(0, 0, pageWidth, 35, 'F');
      
      doc.setTextColor(255, 255, 255);
      doc.setFontSize(24);
      doc.setFont('helvetica', 'bold');
      doc.text('Medical Reports of Patients', pageWidth / 2, 20, { align: 'center' });
      
      // Orange underline
      doc.setDrawColor(255, 152, 0);
      doc.setLineWidth(2);
      doc.line(margin, 25, pageWidth - margin, 25);

      yPos = 45;

      // Patient Information Section
      doc.setTextColor(0, 0, 0);
      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      doc.text('Patient Information:', margin, yPos);
      
      yPos += 8;
      doc.setFontSize(11);
      doc.setFont('helvetica', 'normal');
      
      // Get patient info
      const patientName = report.patientName || 
        (report.patient_info?.first_name && report.patient_info?.last_name
          ? `${report.patient_info.first_name} ${report.patient_info.last_name}`
          : 'Unknown Patient');
      
      // Try to get patient details from appointment
      let patientDOB = 'N/A';
      let patientID = report.patient_firebase_uid?.substring(0, 9) || 'N/A';
      
      if (report.appointment_id) {
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
              `${API_CONFIG.API_URL}/appointments/${report.appointment_id}`,
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
              patientID = patient.firebase_uid?.substring(0, 9) || patientID;
            }
          }
        } catch (err) {
          console.warn('Could not fetch patient details:', err);
        }
      }

      doc.text(`Name: ${patientName}`, margin, yPos);
      yPos += 7;
      doc.text(`Date of Birth: ${patientDOB}`, margin, yPos);
      yPos += 7;
      doc.text(`Patient ID: ${patientID}`, margin, yPos);
      yPos += 7;
      
      const reportDate = report.created_at || report.appointmentDate || new Date().toISOString();
      const formattedReportDate = new Date(reportDate).toLocaleDateString('en-US', {
        month: '2-digit',
        day: '2-digit',
        year: 'numeric'
      });
      doc.text(`Date of Report: ${formattedReportDate}`, margin, yPos);
      yPos += 7;

      // Get doctor info from user context
      let doctorName = 'Dr. Unknown, MD';
      let doctorSpecialty = 'General Practitioner';
      
      if (user) {
        const firstName = user.profile?.first_name || user.first_name || '';
        const lastName = user.profile?.last_name || user.last_name || '';
        if (firstName || lastName) {
          doctorName = `Dr. ${firstName} ${lastName}`.trim() + ', MD';
        } else if (user.displayName) {
          doctorName = `Dr. ${user.displayName}, MD`;
        }
        
        doctorSpecialty = user.profile?.specialization || user.specialization || 'General Practitioner';
      }
      
      doc.text(`Referring Physician: ${doctorName}`, margin, yPos);
      yPos += 7;
      doc.text(`Specialty: ${doctorSpecialty}`, margin, yPos);

      yPos += 15;

      // Introduction Section
      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      doc.text('Introduction:', margin, yPos);
      yPos += 8;
      doc.setFontSize(11);
      doc.setFont('helvetica', 'normal');
      
      const appointmentDate = report.appointmentDate || report.created_at?.split('T')[0] || formattedReportDate;
      const introText = `This report is for ${patientName}, following a consultation and evaluation in the ${doctorSpecialty.toLowerCase()} department on ${appointmentDate}. The purpose of this report is to document ${patientName.split(' ')[0]}'s current health status and outline the recommended management plan.`;
      const introLines = doc.splitTextToSize(introText, pageWidth - 2 * margin);
      doc.text(introLines, margin, yPos);
      yPos += introLines.length * 5 + 10;

      // Medical History Section
      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      doc.text('Medical History:', margin, yPos);
      yPos += 8;
      doc.setFontSize(11);
      doc.setFont('helvetica', 'normal');
      
      // Get symptoms from appointment if available
      let symptomsText = 'No significant medical history documented.';
      if (report.symptoms && Array.isArray(report.symptoms) && report.symptoms.length > 0) {
        symptomsText = `Patient reported the following symptoms: ${report.symptoms.join(', ')}.`;
      } else if (report.appointment_id) {
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
              `${API_CONFIG.API_URL}/appointments/${report.appointment_id}`,
              { headers: { Authorization: `Bearer ${token}` } }
            );
            
            if (appointmentResponse.data?.success && appointmentResponse.data.appointment?.symptoms) {
              const symptoms = appointmentResponse.data.appointment.symptoms;
              if (Array.isArray(symptoms) && symptoms.length > 0) {
                symptomsText = `Patient reported the following symptoms: ${symptoms.join(', ')}.`;
              }
            }
          }
        } catch (err) {
          console.warn('Could not fetch symptoms:', err);
        }
      }
      
      const historyText = `${symptomsText} Patient has no known drug allergies documented.`;
      const historyLines = doc.splitTextToSize(historyText, pageWidth - 2 * margin);
      doc.text(historyLines, margin, yPos);
      yPos += historyLines.length * 5 + 10;

      // Presenting Complaints Section
      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      doc.text('Presenting Complaints:', margin, yPos);
      yPos += 8;
      doc.setFontSize(11);
      doc.setFont('helvetica', 'normal');
      
      const complaintsText = symptomsText !== 'No significant medical history documented.' 
        ? symptomsText
        : 'Patient presented for routine consultation and evaluation.';
      const complaintsLines = doc.splitTextToSize(complaintsText, pageWidth - 2 * margin);
      doc.text(complaintsLines, margin, yPos);
      yPos += complaintsLines.length * 5 + 10;

      // Diagnostic Tests Conducted Section
      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      doc.text('Diagnostic Tests Conducted:', margin, yPos);
      yPos += 8;
      doc.setFontSize(11);
      doc.setFont('helvetica', 'normal');
      doc.text('Clinical examination and patient history review were conducted.', margin, yPos);
      yPos += 10;

      // Diagnosis Section
      if (report.diagnosis) {
        doc.setFontSize(14);
        doc.setFont('helvetica', 'bold');
        doc.text('Diagnosis:', margin, yPos);
        yPos += 8;
        doc.setFontSize(11);
        doc.setFont('helvetica', 'normal');
        const diagnosisLines = doc.splitTextToSize(report.diagnosis, pageWidth - 2 * margin);
        doc.text(diagnosisLines, margin, yPos);
        yPos += diagnosisLines.length * 5 + 10;
      }

      // Medications/Prescription Section
      if (report.medications && Array.isArray(report.medications) && report.medications.length > 0) {
        doc.setFontSize(14);
        doc.setFont('helvetica', 'bold');
        doc.text('Prescribed Medications:', margin, yPos);
        yPos += 8;
        doc.setFontSize(11);
        doc.setFont('helvetica', 'normal');
        
        report.medications.forEach((med, idx) => {
          const medName = med.name || med.medicine || 'Medication';
          const dosage = med.dosage || med.adult_dose || 'As directed';
          const duration = med.duration ? ` for ${med.duration}` : '';
          const medText = `${idx + 1}. ${medName} - ${dosage}${duration}`;
          const medLines = doc.splitTextToSize(medText, pageWidth - 2 * margin);
          doc.text(medLines, margin, yPos);
          yPos += medLines.length * 5 + 3;
        });
        yPos += 5;
      }

      // Treatment Plan Section
      if (report.treatment_plan) {
        doc.setFontSize(14);
        doc.setFont('helvetica', 'bold');
        doc.text('Treatment Plan:', margin, yPos);
        yPos += 8;
        doc.setFontSize(11);
        doc.setFont('helvetica', 'normal');
        const treatmentLines = doc.splitTextToSize(report.treatment_plan, pageWidth - 2 * margin);
        doc.text(treatmentLines, margin, yPos);
        yPos += treatmentLines.length * 5 + 10;
      }

      // Footer
      const footerY = pageHeight - 15;
      doc.setFontSize(8);
      doc.setTextColor(128, 128, 128);
      doc.text('Copyright @ MediChain E-Health System', pageWidth / 2, footerY, { align: 'center' });

      // Save PDF
      const fileName = `medical_report_${patientName.replace(/\s+/g, '_')}_${formattedReportDate.replace(/\//g, '-')}.pdf`;
      doc.save(fileName);
    } catch (error) {
      console.error('Error generating medical report PDF:', error);
      alert('Error generating medical report. Please install required packages: npm install jspdf');
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
                        onClick={() => handleDownloadMedicalReport(report)}
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


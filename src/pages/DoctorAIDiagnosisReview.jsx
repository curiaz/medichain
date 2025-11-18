import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import Header from './Header';
import { Brain, ChevronLeft, ChevronRight, Save, X, Edit2, Check, Search, User, Clock, AlertCircle, FileText, Image, Download, Eye, AlertTriangle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { auth } from '../config/firebase';
import { onAuthStateChanged } from 'firebase/auth';
import { API_CONFIG } from '../config/api';
import '../assets/styles/ModernDashboard.css';
import '../assets/styles/DoctorAIDiagnosisReview.css';

const DoctorAIDiagnosisReview = () => {
  const { appointmentId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { getFirebaseToken } = useAuth();
  
  const [currentSlide, setCurrentSlide] = useState(0);
  const [appointment, setAppointment] = useState(location.state?.appointment || null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [editing, setEditing] = useState({
    recommendedAction: false,
    diagnosis: false,
    prescription: false
  });
  
  // Patient search state
  const [showPatientSearch, setShowPatientSearch] = useState(!appointmentId);
  const [patients, setPatients] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  // eslint-disable-next-line no-unused-vars
  const [reviewStatus, setReviewStatus] = useState('pending'); // pending or reviewed
  
  // Edited values
  const [finalRecommendedAction, setFinalRecommendedAction] = useState('');
  const [finalDiagnosis, setFinalDiagnosis] = useState('');
  const [finalPrescription, setFinalPrescription] = useState({
    medications: [],
    instructions: '',
    duration_days: null
  });

  // Patient files state
  const [patientFiles, setPatientFiles] = useState([]);
  const [viewingFile, setViewingFile] = useState(null);

  // Component for appointment item with status check
  const AppointmentItem = ({ appointment, aptDate, onSelect }) => {
    const [isReviewed, setIsReviewed] = useState(false);
    const [checkingStatus, setCheckingStatus] = useState(true);

    useEffect(() => {
      const checkStatus = async () => {
        try {
          let token = null;
          if (getFirebaseToken) {
            token = await getFirebaseToken();
          } else if (auth.currentUser) {
            token = await auth.currentUser.getIdToken(true);
          } else {
            token = localStorage.getItem('medichain_token');
          }

          if (!token) {
            setCheckingStatus(false);
            return;
          }

          const response = await axios.get(`${API_CONFIG.API_URL}/medical-reports/appointment/${appointment.id}`, {
            headers: { Authorization: `Bearer ${token}` }
          });

          // Check if medical report exists and has review_status = 'reviewed'
          if (response.data?.success && response.data.medical_report) {
            const report = response.data.medical_report;
            // Check review_status column if it exists, otherwise assume reviewed if diagnosis exists
            setIsReviewed(report.review_status === 'reviewed' || (!report.review_status && report.diagnosis));
          } else {
            setIsReviewed(false);
          }
        } catch (err) {
          // 404 means not reviewed
          setIsReviewed(false);
        } finally {
          setCheckingStatus(false);
        }
      };

      checkStatus();
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [appointment.id]);

    return (
      <div
        className="appointment-item"
        onClick={() => onSelect(appointment)}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
          <div className="appointment-date">
            <Clock size={16} />
            {aptDate.toLocaleDateString('en-US', { 
              month: 'short', 
              day: 'numeric',
              year: 'numeric'
            })} at {aptDate.toLocaleTimeString('en-US', {
              hour: '2-digit',
              minute: '2-digit'
            })}
          </div>
          {!checkingStatus && (
            <span className="appointment-status-badge" style={{
              padding: '4px 10px',
              borderRadius: '12px',
              fontSize: '11px',
              fontWeight: '600',
              background: isReviewed ? '#4CAF50' : '#FF9800',
              color: 'white'
            }}>
              {isReviewed ? 'Reviewed' : 'Pending'}
            </span>
          )}
        </div>
        {appointment.ai_diagnosis?.detailed_results?.[0] && (
          <div className="appointment-diagnosis">
            {appointment.ai_diagnosis.detailed_results[0].condition}
          </div>
        )}
        <button className="review-appointment-btn" onClick={(e) => {
          e.stopPropagation();
          onSelect(appointment);
        }}>
          {isReviewed ? 'View Review' : 'Review AI Diagnosis'}
        </button>
      </div>
    );
  };

  // Monitor auth state changes in real-time
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
      if (!firebaseUser) {
        setError('You are not authenticated. Please log in to continue.');
        setLoading(false);
        // Redirect to login after showing notification
        setTimeout(() => {
          navigate('/login');
        }, 2000);
      }
    });

    return () => unsubscribe();
  }, [navigate]);

  useEffect(() => {
    // Check if auth.currentUser is null
    if (!auth.currentUser) {
      setError('You are not authenticated. Please log in to continue.');
      setLoading(false);
      // Redirect to login after showing notification
      setTimeout(() => {
        navigate('/login');
      }, 2000);
      return;
    }

    // If appointment is passed via state, use it immediately
    if (appointment && appointment.id) {
      console.log('Appointment from state:', {
        id: appointment.id,
        has_ai_diagnosis: !!appointment.ai_diagnosis,
        ai_diagnosis_processed: appointment.ai_diagnosis_processed
      });
      setLoading(false);
      loadAppointmentData(appointment);
      checkReviewStatus(appointment.id);
    } else if (appointmentId) {
      // Otherwise, fetch from API
      loadAppointmentFromId();
    } else {
      // No appointment ID - show patient search
      setLoading(false);
      loadPatients();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [appointmentId, appointment]);

  const checkReviewStatus = async (aptId) => {
    try {
      let token = null;
      if (getFirebaseToken) {
        token = await getFirebaseToken();
      } else if (auth.currentUser) {
        token = await auth.currentUser.getIdToken(true);
      } else {
        token = localStorage.getItem('medichain_token');
      }

      if (!token) return;

      const response = await axios.get(`${API_CONFIG.API_URL}/medical-reports/appointment/${aptId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      // Check if medical report exists and has review_status = 'reviewed'
      if (response.data?.success && response.data.medical_report) {
        const report = response.data.medical_report;
        // Check review_status column if it exists, otherwise assume reviewed if diagnosis exists
        if (report.review_status === 'reviewed' || (!report.review_status && report.diagnosis)) {
          setReviewStatus('reviewed');
        } else {
          setReviewStatus('pending');
        }
      } else {
        setReviewStatus('pending');
      }
    } catch (err) {
      // Error fetching report - treat as not reviewed
        setReviewStatus('pending');
    }
  };

  const loadPatients = async () => {
    try {
      setLoading(true);
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

      // Get all appointments for this doctor
      const response = await axios.get(`${API_CONFIG.API_URL}/appointments`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data?.success) {
        const appointments = response.data.appointments || [];
        console.log(`🔍 [AI Diagnosis Review] Total appointments fetched: ${appointments.length}`);
        
        // Filter appointments with AI diagnosis
        const appointmentsWithAI = appointments.filter(apt => 
          apt.ai_diagnosis && apt.ai_diagnosis_processed
        );
        console.log(`🔍 [AI Diagnosis Review] Appointments with AI diagnosis: ${appointmentsWithAI.length}`);

        // Group by patient
        const patientMap = new Map();
        appointmentsWithAI.forEach(apt => {
          if (apt.patient && apt.patient_firebase_uid) {
            const patientId = apt.patient_firebase_uid;
            if (!patientMap.has(patientId)) {
              patientMap.set(patientId, {
                id: patientId,
                name: `${apt.patient.first_name || ''} ${apt.patient.last_name || ''}`.trim() || 'Unknown Patient',
                email: apt.patient.email || '',
                appointments: []
              });
            }
            patientMap.get(patientId).appointments.push(apt);
          } else {
            console.warn(`⚠️  [AI Diagnosis Review] Appointment ${apt.id} missing patient info`);
          }
        });

        const patientsList = Array.from(patientMap.values());
        console.log(`✅ [AI Diagnosis Review] Grouped into ${patientsList.length} patients`);
        patientsList.forEach(patient => {
          console.log(`  - ${patient.name}: ${patient.appointments.length} appointment(s)`);
        });

        setPatients(patientsList);
        setLoading(false);
      }
    } catch (err) {
      console.error('Error loading patients:', err);
      setError('Failed to load patients');
      setLoading(false);
    }
  };


  const handleAppointmentSelect = async (apt) => {
    setAppointment(apt);
    setShowPatientSearch(false);
    loadAppointmentData(apt);
    checkReviewStatus(apt.id);
  };

  const loadAppointmentFromId = async () => {
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

      // Try to get appointment from appointments list first
      const appointmentsResponse = await axios.get('http://localhost:5000/api/appointments', {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (appointmentsResponse.data?.success) {
        const appointments = appointmentsResponse.data.appointments || [];
        console.log(`Found ${appointments.length} appointments, looking for ID: ${appointmentId}`);
        const foundAppointment = appointments.find(apt => {
          const aptId = apt.id?.toString() || apt.id;
          const searchId = appointmentId?.toString() || appointmentId;
          return aptId === searchId;
        });
        
        if (foundAppointment) {
          console.log('Appointment found:', {
            id: foundAppointment.id,
            has_ai_diagnosis: !!foundAppointment.ai_diagnosis,
            ai_diagnosis_processed: foundAppointment.ai_diagnosis_processed
          });
          setAppointment(foundAppointment);
          loadAppointmentData(foundAppointment);
          checkReviewStatus(foundAppointment.id);
          setLoading(false);
          return;
        } else {
          console.error('Appointment not found. Available IDs:', appointments.map(a => a.id));
        }
      }
      
      // If not found, show error
      setError('Appointment not found');
    } catch (err) {
      console.error('Error loading appointment:', err);
      setError(err.response?.data?.error || 'Failed to load appointment');
    } finally {
      setLoading(false);
    }
  };

  const loadAppointmentData = (appt = null) => {
    const apptData = appt || appointment;
    if (!apptData) {
      console.error('No appointment data available');
      return;
    }

    console.log('Loading appointment data:', {
      id: apptData.id,
      has_ai_diagnosis: !!apptData.ai_diagnosis,
      ai_diagnosis_processed: apptData.ai_diagnosis_processed,
      detailed_results_count: apptData.ai_diagnosis?.detailed_results?.length || 0,
      documents: apptData.documents,
      medicine_allergies: apptData.medicine_allergies,
      medicine_allergies_type: typeof apptData.medicine_allergies,
      medicine_allergies_value: JSON.stringify(apptData.medicine_allergies),
      patient_allergies: apptData.patient?.allergies,
      patient_allergies_type: typeof apptData.patient?.allergies,
      patient_allergies_value: JSON.stringify(apptData.patient?.allergies),
      full_patient_object: apptData.patient
    });

    // Load patient uploaded files
    if (apptData.documents && Array.isArray(apptData.documents) && apptData.documents.length > 0) {
      setPatientFiles(apptData.documents);
      console.log('📄 Loaded patient files:', apptData.documents);
    } else {
      setPatientFiles([]);
    }

    // Initialize from AI diagnosis
    if (apptData.ai_diagnosis?.detailed_results?.[0]) {
      const aiResult = apptData.ai_diagnosis.detailed_results[0];
      setFinalDiagnosis(aiResult.condition || '');
      setFinalRecommendedAction(aiResult.recommended_action || '');
      
      if (aiResult.medication) {
        setFinalPrescription({
          medications: [{
            name: aiResult.medication,
            dosage: aiResult.dosage || '',
            frequency: 'As prescribed',
            duration: aiResult.dosage ? '7 days' : ''
          }],
          instructions: aiResult.recommended_action || '',
          duration_days: 7
        });
      }
    } else {
      console.warn('No AI diagnosis data found in appointment:', apptData);
    }

    // Check if medical report already exists (doctor has already edited)
    // This is async but we don't need to wait for it - it's optional
    loadMedicalReport(apptData.id).catch(err => {
      // Silently handle errors - no medical report is expected for new appointments
      console.log('No existing medical report (this is normal)');
    });
  };

  const loadMedicalReport = async (apptId) => {
    try {
      let token = null;
      if (getFirebaseToken) {
        token = await getFirebaseToken();
      } else if (auth.currentUser) {
        token = await auth.currentUser.getIdToken(true);
      } else {
        token = localStorage.getItem('medichain_token');
      }

      const response = await axios.get(`${API_CONFIG.API_URL}/medical-reports/appointment/${apptId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data?.success && response.data.medical_report) {
        const report = response.data.medical_report;
        // Load existing medical report data
        if (report.diagnosis) {
          setFinalDiagnosis(report.diagnosis);
        }
        if (report.treatment_plan) {
          setFinalRecommendedAction(report.treatment_plan);
        }
        if (report.medications) {
          setFinalPrescription({
            medications: Array.isArray(report.medications) ? report.medications : [],
            instructions: report.treatment_plan || '',
            duration_days: report.duration_days || null
          });
        }
      }
    } catch (err) {
      // Medical report doesn't exist yet, that's okay - this is expected for new appointments
      // Backend now returns 200 with success: false instead of 404, so this catch is for other errors
        console.log('No existing medical report found - this is normal for new appointments');
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      
      let token = null;
      if (getFirebaseToken) {
        token = await getFirebaseToken();
      } else if (auth.currentUser) {
        token = await auth.currentUser.getIdToken(true);
      } else {
        token = localStorage.getItem('medichain_token');
      }

      const medicalReportData = {
        appointment_id: appointment.id,
        patient_firebase_uid: appointment.patient_firebase_uid,
        record_type: 'consultation',
        title: `Medical Report - ${appointment.appointment_date}`,
        symptoms: appointment.symptoms || [],
        diagnosis: finalDiagnosis,
        treatment_plan: finalRecommendedAction || finalPrescription.instructions,
        medications: finalPrescription.medications,
        status: 'active'
      };

      const response = await axios.post(`${API_CONFIG.API_URL}/medical-reports`, medicalReportData, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.data?.success) {
        setReviewStatus('reviewed');
        alert('Medical report saved successfully!');
        
        // Trigger dashboard statistics refresh by dispatching a custom event
        // This will notify the dashboard to refresh its statistics
        window.dispatchEvent(new CustomEvent('medicalReportSaved', {
          detail: { appointmentId: appointment.id }
        }));
        
        // Optionally navigate back or stay on page
        // navigate('/doctor-schedule');
      } else {
        alert('Failed to save medical report: ' + (response.data?.error || 'Unknown error'));
      }
    } catch (err) {
      console.error('Error saving medical report:', err);
      alert('Error saving medical report. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  // Helper function to get file URL
  const getFileUrl = (file) => {
    // First, check if file has base64 data (for inline display)
    if (file.data || file.base64) {
      const base64Data = file.data || file.base64;
      // If it already has data URL prefix, return as is
      if (base64Data.startsWith('data:')) {
        return base64Data;
      }
      // Otherwise, construct data URL
      const mimeType = file.type || 'application/octet-stream';
      // Determine MIME type from filename if not provided
      let finalMimeType = mimeType;
      if (mimeType === 'application/octet-stream' && file.name) {
        const ext = file.name.split('.').pop()?.toLowerCase();
        if (ext === 'pdf') finalMimeType = 'application/pdf';
        else if (['jpg', 'jpeg'].includes(ext)) finalMimeType = 'image/jpeg';
        else if (ext === 'png') finalMimeType = 'image/png';
      }
      return `data:${finalMimeType};base64,${base64Data}`;
    }
    
    // Handle different file storage formats
    if (file.url) return file.url;
    if (file.file_url) return file.file_url;
    if (file.file_path) {
      // If it's already a full URL, return as is
      if (file.file_path.startsWith('http')) return file.file_path;
      // Try Supabase Storage URL format
      if (file.file_path.startsWith('documents/')) {
        // Construct file URL (API_URL already includes /api)
        return `${API_CONFIG.API_URL}/files/${file.file_path}`;
      }
      return `${API_CONFIG.API_URL}/files/${file.file_path}`;
    }
    // If file has a name but no URL, try to construct from appointment
    if (file.name && appointment?.id) {
      // Try to fetch file from appointment documents endpoint
      // API_URL already includes /api, so use /files/ not /api/files/
      return `${API_CONFIG.API_URL}/files/appointments/${appointment.id}/documents/${encodeURIComponent(file.name)}`;
    }
    return null;
  };

  // Helper function to determine file type
  const getFileType = (filename) => {
    if (!filename) return 'unknown';
    const ext = filename.split('.').pop()?.toLowerCase();
    if (['pdf'].includes(ext)) return 'pdf';
    if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext)) return 'image';
    if (['doc', 'docx'].includes(ext)) return 'document';
    return 'other';
  };

  // File Viewer Component
  const FileViewer = ({ file, onClose }) => {
    const [fileUrl, setFileUrl] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const fileType = getFileType(file.name || file.filename);

    useEffect(() => {
      const loadFile = async () => {
        try {
          setLoading(true);
          setError(null);
          
          // Check if file has base64 data (no need to fetch)
          if (file.data || file.base64) {
            const url = getFileUrl(file);
            setFileUrl(url);
            setLoading(false);
            return;
          }
          
          // Otherwise, get URL (might need authentication)
          const url = getFileUrl(file);
          
          // If URL requires authentication, fetch with token
          if (url && url.startsWith(API_CONFIG.API_URL)) {
            try {
              let token = null;
              if (getFirebaseToken) {
                token = await getFirebaseToken();
              } else if (auth.currentUser) {
                token = await auth.currentUser.getIdToken(true);
              }
              
              if (token) {
                // Test if file is accessible
                const response = await fetch(url, {
                  headers: {
                    'Authorization': `Bearer ${token}`
                  }
                });
                
                if (response.ok) {
                  // If response is JSON with a URL, use that
                  const contentType = response.headers.get('content-type');
                  if (contentType && contentType.includes('application/json')) {
                    const data = await response.json();
                    if (data.url) {
                      setFileUrl(data.url);
                    } else if (data.error) {
                      throw new Error(data.message || data.error);
                    } else {
                      setFileUrl(url);
                    }
                  } else {
                    // Convert blob to data URL for images/PDFs
                    const blob = await response.blob();
                    const reader = new FileReader();
                    reader.onloadend = () => {
                      setFileUrl(reader.result);
                    };
                    reader.onerror = () => {
                      setError('Failed to read file data');
                      setLoading(false);
                    };
                    reader.readAsDataURL(blob);
                    return; // Don't set loading to false yet, wait for reader
                  }
                } else {
                  // Try to get error message from response
                  const contentType = response.headers.get('content-type');
                  if (contentType && contentType.includes('application/json')) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || errorData.error || `Failed to load file: ${response.statusText}`);
                  } else {
                    throw new Error(`Failed to load file: ${response.status} ${response.statusText}`);
                  }
                }
              } else {
                setFileUrl(url);
              }
            } catch (err) {
              console.error('Error loading file:', err);
              setError('Failed to load file. Please try again.');
            }
          } else {
            setFileUrl(url);
          }
          
          setLoading(false);
        } catch (err) {
          console.error('Error in loadFile:', err);
          setError('Failed to load file');
          setLoading(false);
        }
      };
      
      loadFile();
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [file, appointment?.id]);

    if (loading) {
      return (
        <div className="file-viewer-overlay" onClick={onClose}>
          <div className="file-viewer-content" onClick={(e) => e.stopPropagation()}>
            <div className="file-viewer-error">
              <div className="loading-spinner" style={{ margin: '20px auto' }}></div>
              <p>Loading file...</p>
              <button onClick={onClose}>Close</button>
            </div>
          </div>
        </div>
      );
    }

    if (error || !fileUrl) {
      return (
        <div className="file-viewer-overlay" onClick={onClose}>
          <div className="file-viewer-content" onClick={(e) => e.stopPropagation()}>
            <div className="file-viewer-error">
              <AlertCircle size={48} />
              <p>{error || 'File URL not available'}</p>
              <button onClick={onClose}>Close</button>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="file-viewer-overlay" onClick={onClose}>
        <div className="file-viewer-content" onClick={(e) => e.stopPropagation()}>
          <div className="file-viewer-header">
            <h3>{file.name || file.filename || 'Patient File'}</h3>
            <button className="file-viewer-close" onClick={onClose}>
              <X size={24} />
            </button>
          </div>
          <div className="file-viewer-body">
            {fileType === 'pdf' ? (
              <iframe
                src={fileUrl}
                title={file.name || file.filename}
                style={{ width: '100%', height: '100%', border: 'none' }}
              />
            ) : fileType === 'image' ? (
              <img
                src={fileUrl}
                alt={file.name || file.filename}
                style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }}
                onError={(e) => {
                  console.error('Image load error:', e);
                  setError('Failed to load image');
                }}
              />
            ) : (
              <div className="file-viewer-unsupported">
                <FileText size={48} />
                <p>Preview not available for this file type</p>
                <a href={fileUrl} download target="_blank" rel="noopener noreferrer">
                  <Download size={20} />
                  Download File
                </a>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const slides = [
    {
      title: 'Possible Conditions',
      content: (
        <div className="slide-content">
          {/* Patient Uploaded Files Section */}
          {patientFiles && patientFiles.length > 0 && (
            <div className="slide-content-card patient-files-section">
              <h4 className="files-section-title">
                <FileText size={20} />
                Patient Uploaded Files
              </h4>
              <div className="patient-files-grid">
                {patientFiles.map((file, idx) => {
                  const fileType = getFileType(file.name || file.filename);
                  return (
                    <div key={idx} className="patient-file-card" onClick={() => setViewingFile(file)}>
                      <div className="file-icon">
                        {fileType === 'pdf' ? (
                          <FileText size={32} />
                        ) : fileType === 'image' ? (
                          <Image size={32} />
                        ) : (
                          <FileText size={32} />
                        )}
                      </div>
                      <div className="file-info">
                        <p className="file-name">{file.name || file.filename || 'Unknown File'}</p>
                        {file.size && (
                          <p className="file-size">{(file.size / 1024).toFixed(2)} KB</p>
                        )}
                      </div>
                      <div className="file-action">
                        <Eye size={18} />
                        <span>View</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* AI Diagnosis Results */}
          {appointment?.ai_diagnosis?.detailed_results && appointment.ai_diagnosis.detailed_results.length > 0 ? (
            <>
              <p className="slide-intro">Based on the patient's symptoms, the AI has identified the following possible conditions:</p>
              <div className="slide-content-grid">
                {appointment.ai_diagnosis.detailed_results.map((result, idx) => (
                  <div key={idx} className="slide-content-card ai-result-card">
                    <div className="result-header">
                      <h3>{result.condition || 'Unknown Condition'}</h3>
                      <span className="confidence-badge">
                        {result.confidence_percent || `${Math.round((result.confidence || 0) * 100)}%`}
                      </span>
                    </div>
                    {result.reason && (
                      <p className="result-reason">{result.reason}</p>
                    )}
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="slide-content-card no-ai-results">
              <p>No AI diagnosis results available.</p>
              <p className="sub-text">AI diagnosis may not have been processed yet for this appointment.</p>
            </div>
          )}
        </div>
      )
    },
    {
      title: 'Recommended Action',
      content: (
        <div className="slide-content">
          <div className="slide-content-card editable-section">
            <div className="section-header">
              <h3>Recommended Action</h3>
              <button
                className="edit-button"
                onClick={() => setEditing({ ...editing, recommendedAction: !editing.recommendedAction })}
              >
                {editing.recommendedAction ? <Check size={18} /> : <Edit2 size={18} />}
              </button>
            </div>
            {editing.recommendedAction ? (
              <textarea
                className="action-input"
                value={finalRecommendedAction}
                onChange={(e) => setFinalRecommendedAction(e.target.value)}
                placeholder="Enter recommended action..."
                rows={6}
              />
            ) : (
              <div className="recommended-action-display">
                {finalRecommendedAction || appointment?.ai_diagnosis?.detailed_results?.[0]?.recommended_action ? (
                  <div className="action-card">
                    <h3>Recommended Action</h3>
                    <p className="action-text">
                      {finalRecommendedAction || appointment.ai_diagnosis.detailed_results[0].recommended_action}
                    </p>
                    {appointment?.ai_diagnosis?.detailed_results?.[0]?.reason && (
                      <div className="action-reason">
                        <strong>AI Reasoning:</strong>
                        <p>{appointment.ai_diagnosis.detailed_results[0].reason}</p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="no-ai-results">
                    <p>No recommended action available. Click edit to add.</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )
    },
    {
      title: 'Medication',
      content: (
        <div className="slide-content">
          {/* Patient Medicine Allergies Section */}
          {(() => {
            // Get allergies from appointment first, then fallback to patient profile
            let allergies = [];
            
            console.log('🔍 Checking allergies:', {
              'appointment.medicine_allergies': appointment?.medicine_allergies,
              'appointment.medicine_allergies type': typeof appointment?.medicine_allergies,
              'appointment.patient?.allergies': appointment?.patient?.allergies,
              'appointment.patient?.allergies type': typeof appointment?.patient?.allergies,
              'full appointment object keys': appointment ? Object.keys(appointment) : 'no appointment'
            });
            
            // Check appointment.medicine_allergies first
            if (appointment?.medicine_allergies) {
              if (typeof appointment.medicine_allergies === 'string' && appointment.medicine_allergies.trim()) {
                allergies = appointment.medicine_allergies
                  .split(/[,;\n]/)
                  .map(a => a.trim())
                  .filter(a => a.length > 0);
                console.log('✅ Parsed medicine_allergies from string:', allergies);
              } else if (Array.isArray(appointment.medicine_allergies)) {
                allergies = appointment.medicine_allergies.filter(a => a && (typeof a === 'string' ? a.trim().length > 0 : true));
                console.log('✅ Parsed medicine_allergies from array:', allergies);
              } else {
                console.warn('⚠️ medicine_allergies is neither string nor array:', appointment.medicine_allergies);
              }
            } else {
              console.log('ℹ️ No appointment.medicine_allergies found');
            }
            
            // Fallback to patient profile allergies if appointment doesn't have them
            if (allergies.length === 0 && appointment?.patient?.allergies) {
              if (Array.isArray(appointment.patient.allergies)) {
                allergies = appointment.patient.allergies.filter(a => a && (typeof a === 'string' ? a.trim().length > 0 : true));
                console.log('✅ Parsed patient.allergies from array:', allergies);
              } else if (typeof appointment.patient.allergies === 'string' && appointment.patient.allergies.trim()) {
                allergies = appointment.patient.allergies
                  .split(/[,;\n]/)
                  .map(a => a.trim())
                  .filter(a => a.length > 0);
                console.log('✅ Parsed patient.allergies from string:', allergies);
              } else {
                console.warn('⚠️ patient.allergies is neither string nor array:', appointment.patient.allergies);
              }
            } else if (allergies.length === 0) {
              console.log('ℹ️ No patient.allergies found or already have allergies from appointment');
            }
            
            console.log('📋 Final allergies array:', allergies);
            
            return allergies.length > 0 ? (
              <div className="slide-content-card medicine-allergies-section" style={{
                background: '#FFF3CD',
                border: '2px solid #FFC107',
                borderRadius: '8px',
                padding: '16px',
                marginBottom: '20px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                  <AlertTriangle size={24} color="#FF9800" />
                  <h4 style={{ margin: 0, color: '#856404', fontSize: '18px', fontWeight: '600' }}>
                    Patient Medicine Allergies
                  </h4>
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {allergies.map((allergy, idx) => (
                    <span
                      key={idx}
                      style={{
                        background: '#FFE082',
                        color: '#856404',
                        padding: '6px 12px',
                        borderRadius: '16px',
                        fontSize: '14px',
                        fontWeight: '500',
                        border: '1px solid #FFC107'
                      }}
                    >
                      {allergy}
                    </span>
                  ))}
                </div>
                <p style={{ 
                  marginTop: '12px', 
                  marginBottom: 0, 
                  fontSize: '13px', 
                  color: '#856404',
                  fontStyle: 'italic'
                }}>
                  ⚠️ Please review medication recommendations carefully to avoid allergic reactions.
                </p>
              </div>
            ) : null;
          })()}

          {/* AI Recommended Medication */}
          {appointment?.ai_diagnosis?.detailed_results?.[0]?.medication ? (
            <div className="slide-content-card medication-display">
              <div className="medication-card">
                <h3>AI Recommended Medication</h3>
                <div className="medication-details">
                  <div className="medication-name">
                    <strong>Medication:</strong>
                    <span>{appointment.ai_diagnosis.detailed_results[0].medication}</span>
                  </div>
                  {appointment.ai_diagnosis.detailed_results[0].dosage && (
                    <div className="medication-dosage">
                      <strong>Dosage:</strong>
                      <span>{appointment.ai_diagnosis.detailed_results[0].dosage}</span>
                    </div>
                  )}
                  {appointment.ai_diagnosis.detailed_results[0].recommended_action && (
                    <div className="medication-instructions">
                      <strong>Instructions:</strong>
                      <p>{appointment.ai_diagnosis.detailed_results[0].recommended_action}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="slide-content-card no-ai-results">
              <p>No medication recommendation available from AI diagnosis.</p>
            </div>
          )}
        </div>
      )
    },
    {
      title: 'Final Diagnosis',
      content: (
        <div className="slide-content">
          {/* Patient Symptoms Section */}
          {appointment?.symptoms && appointment.symptoms.length > 0 && (
            <div className="slide-content-card symptoms-section">
              <h4 className="symptoms-title">Patient's Reported Symptoms</h4>
              <div className="symptoms-list">
                {appointment.symptoms.map((symptom, idx) => (
                  <span key={idx} className="symptom-tag">
                    {symptom.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {/* Final Diagnosis Section */}
          <div className="slide-content-card editable-section">
            <div className="section-header">
              <h3>Final Diagnosis</h3>
              <button
                className="edit-button"
                onClick={() => setEditing({ ...editing, diagnosis: !editing.diagnosis })}
              >
                {editing.diagnosis ? <Check size={18} /> : <Edit2 size={18} />}
              </button>
            </div>
            {editing.diagnosis ? (
              <textarea
                className="diagnosis-input"
                value={finalDiagnosis}
                onChange={(e) => setFinalDiagnosis(e.target.value)}
                placeholder="Enter final diagnosis..."
                rows={6}
              />
            ) : (
              <div className="diagnosis-display">
                {finalDiagnosis || <em>No diagnosis entered yet. Click edit to add.</em>}
              </div>
            )}
          </div>
        </div>
      )
    },
    {
      title: 'Prescription',
      content: (
        <div className="slide-content">
          <div className="editable-section">
            <div className="section-header" style={{ justifyContent: 'flex-end', marginBottom: '16px' }}>
              <button
                className="edit-button"
                onClick={() => setEditing({ ...editing, prescription: !editing.prescription })}
              >
                {editing.prescription ? <Check size={18} /> : <Edit2 size={18} />}
              </button>
            </div>
            {editing.prescription ? (
              <div className="prescription-editor">
                <div className="medications-section">
                  <label className="section-label">Medications</label>
                  <div className="medications-list">
                    {finalPrescription.medications.map((med, idx) => (
                      <div key={idx} className="medication-item">
                        <div className="medication-input-group">
                          <label className="field-label">Medication Name</label>
                          <input
                            type="text"
                            placeholder="e.g., St. John's Wort / Omega-3 supplements"
                            value={med.name}
                            onChange={(e) => {
                              const newMeds = [...finalPrescription.medications];
                              newMeds[idx].name = e.target.value;
                              setFinalPrescription({ ...finalPrescription, medications: newMeds });
                            }}
                          />
                        </div>
                        <div className="medication-input-group">
                          <label className="field-label">Dosage</label>
                          <input
                            type="text"
                            placeholder="e.g., 300 mg 2x/day"
                            value={med.dosage}
                            onChange={(e) => {
                              const newMeds = [...finalPrescription.medications];
                              newMeds[idx].dosage = e.target.value;
                              setFinalPrescription({ ...finalPrescription, medications: newMeds });
                            }}
                          />
                        </div>
                        <button
                          className="remove-med-button"
                          onClick={() => {
                            const newMeds = finalPrescription.medications.filter((_, i) => i !== idx);
                            setFinalPrescription({ ...finalPrescription, medications: newMeds });
                          }}
                          title="Remove medication"
                        >
                          <X size={16} />
                        </button>
                      </div>
                    ))}
                    <button
                      className="add-med-button"
                      onClick={() => {
                        setFinalPrescription({
                          ...finalPrescription,
                          medications: [...finalPrescription.medications, { name: '', dosage: '', frequency: '', duration: '' }]
                        });
                      }}
                    >
                      + Add Medication
                    </button>
                  </div>
                </div>
                <div className="instructions-section">
                  <label className="section-label">Instructions for Patient</label>
                  <textarea
                    className="instructions-input"
                    value={finalPrescription.instructions}
                    onChange={(e) => setFinalPrescription({ ...finalPrescription, instructions: e.target.value })}
                    placeholder="e.g., Seek counseling, maintain routine, use calming supplements."
                    rows={2}
                  />
                </div>
                <div className="duration-section">
                  <label className="section-label">Treatment Duration (Days)</label>
                  <input
                    type="number"
                    className="duration-input"
                    placeholder="Enter number of days"
                    value={finalPrescription.duration_days || ''}
                    onChange={(e) => setFinalPrescription({ ...finalPrescription, duration_days: parseInt(e.target.value) || null })}
                    min="1"
                  />
                </div>
              </div>
            ) : (
              <div className="prescription-display">
                {finalPrescription.medications.length > 0 ? (
                  <div>
                    <h4>Medications:</h4>
                    <ul>
                      {finalPrescription.medications.map((med, idx) => (
                        <li key={idx}>
                          <strong>{med.name}</strong> - {med.dosage}
                          {med.duration && ` (${med.duration})`}
                        </li>
                      ))}
                    </ul>
                    {finalPrescription.instructions && (
                      <div>
                        <h4>Instructions:</h4>
                        <p>{finalPrescription.instructions}</p>
                      </div>
                    )}
                  </div>
                ) : (
                  <em>No prescription entered yet. Click edit to add.</em>
                )}
              </div>
            )}
          </div>
        </div>
      )
    }
  ];

  if (loading) {
    return (
      <div className="dashboard-container">
        <Header />
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading AI diagnosis...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <Header />
        <div className="error-container">
          <p>{error}</p>
          <button onClick={() => navigate('/doctor-schedule')}>Back to Schedule</button>
        </div>
      </div>
    );
  }

  // Show patient search if no appointment selected
  if (showPatientSearch || (!appointment && !loading && !error)) {
    const filteredPatients = patients.filter(patient => {
      if (!searchTerm) return true;
      const search = searchTerm.toLowerCase();
      return (
        patient.name.toLowerCase().includes(search) ||
        patient.email.toLowerCase().includes(search)
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
              <h1 className="dashboard-title">AI DIAGNOSIS REVIEW</h1>
              <div className="user-welcome">
                <span>Search for a patient to review their AI diagnosis</span>
              </div>
            </div>
          </div>

          <div className="patient-search-container">
            <div className="search-section">
              <div className="search-box">
                <Search size={20} />
                <input
                  type="text"
                  placeholder="Search by patient name or email..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="search-input"
                />
              </div>
            </div>

            {loading ? (
              <div className="loading-container">
                <div className="loading-spinner"></div>
                <p>Loading patients...</p>
              </div>
            ) : filteredPatients.length === 0 ? (
              <div className="no-patients">
                <User size={48} />
                <p>No patients with AI diagnoses found.</p>
                <p className="sub-text">Patients will appear here after they book appointments with symptoms.</p>
              </div>
            ) : (
              <div className="patients-list">
                {filteredPatients.map((patient) => (
                  <div key={patient.id} className="patient-card">
                    <div className="patient-info">
                      <User size={24} />
                      <div>
                        <h3>{patient.name}</h3>
                        <p className="patient-email">{patient.email}</p>
                        <p className="patient-appointments-count">
                          {patient.appointments.length} appointment{patient.appointments.length !== 1 ? 's' : ''} with AI diagnosis
                        </p>
                      </div>
                    </div>
                    <div className="patient-appointments">
                      {patient.appointments.map((apt) => {
                        const aptDate = new Date(`${apt.appointment_date}T${apt.appointment_time || '00:00'}`);
                        return (
                          <AppointmentItem
                            key={apt.id}
                            appointment={apt}
                            aptDate={aptDate}
                            onSelect={handleAppointmentSelect}
                          />
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </main>
      </div>
    );
  }

  if (!appointment) {
    return (
      <div className="dashboard-container">
        <Header />
        <div className="error-container">
          <p>Appointment not found</p>
          <button onClick={() => navigate('/doctor-schedule')}>Back to Schedule</button>
        </div>
      </div>
    );
  }

  // Check if AI diagnosis exists
  const hasAIDiagnosis = appointment.ai_diagnosis && appointment.ai_diagnosis_processed && 
                         appointment.ai_diagnosis.detailed_results && 
                         appointment.ai_diagnosis.detailed_results.length > 0;

  if (!hasAIDiagnosis) {
    return (
      <div className="dashboard-container">
        <Header />
        <div className="error-container">
          <p>AI diagnosis not available for this appointment.</p>
          <p style={{ fontSize: '14px', color: '#666', marginTop: '8px' }}>
            The AI diagnosis may not have been processed yet. Please check back later.
          </p>
          <button onClick={() => navigate('/doctor-schedule')}>Back to Schedule</button>
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
            <div>
              <h1 className="dashboard-title">AI DIAGNOSIS REVIEW</h1>
              <div className="appointment-info">
                <span>Appointment: {appointment.appointment_date} at {appointment.appointment_time}</span>
                {appointment.patient && (
                  <span>Patient: {appointment.patient.first_name} {appointment.patient.last_name}</span>
                )}
              </div>
            </div>
            {showPatientSearch && (
              <button
                className="back-to-search-btn"
                onClick={() => {
                  setAppointment(null);
                  setShowPatientSearch(true);
                  loadPatients();
                }}
                style={{
                  marginTop: '12px',
                  padding: '8px 16px',
                  background: '#f5f5f5',
                  border: '1px solid #e0e0e0',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                ← Back to Patient Search
              </button>
            )}
          </div>
        </div>

        <div className="ai-review-container">
          <div className="slide-navigation">
            <button
              className="nav-button"
              onClick={() => setCurrentSlide(Math.max(0, currentSlide - 1))}
              disabled={currentSlide === 0}
            >
              <ChevronLeft size={20} />
              Previous
            </button>
            <div className="slide-indicator">
              <span>Slide {currentSlide + 1} of {slides.length}</span>
              <div className="slide-dots">
                {slides.map((_, idx) => (
                  <span
                    key={idx}
                    className={`dot ${idx === currentSlide ? 'active' : ''}`}
                    onClick={() => setCurrentSlide(idx)}
                  />
                ))}
              </div>
            </div>
            <button
              className="nav-button"
              onClick={() => setCurrentSlide(Math.min(slides.length - 1, currentSlide + 1))}
              disabled={currentSlide === slides.length - 1}
            >
              Next
              <ChevronRight size={20} />
            </button>
          </div>

          <div className="slide-container">
            <div className="slide-header">
              <Brain size={24} />
              <h2>{slides[currentSlide].title}</h2>
            </div>
            <div className="slide-body">
              {slides[currentSlide].content}
            </div>
          </div>

          <div className="review-actions">
            <button className="cancel-button" onClick={() => navigate('/doctor-schedule')}>
              Cancel
            </button>
            <button
              className="save-button"
              onClick={handleSave}
              disabled={saving}
            >
              <Save size={18} />
              {saving ? 'Saving...' : 'Save Medical Report'}
            </button>
          </div>
        </div>
      </main>

      {/* File Viewer Modal */}
      {viewingFile && (
        <FileViewer
          file={viewingFile}
          onClose={() => setViewingFile(null)}
        />
      )}
    </div>
  );
};

export default DoctorAIDiagnosisReview;


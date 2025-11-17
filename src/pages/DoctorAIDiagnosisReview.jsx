import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import Header from './Header';
import { Brain, ChevronLeft, ChevronRight, Save, X, Edit2, Check, Search, User, Clock } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { auth } from '../config/firebase';
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

          const response = await axios.get(`https://medichain.clinic/api/medical-reports/appointment/${appointment.id}`, {
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

  useEffect(() => {
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

      const response = await axios.get(`https://medichain.clinic/api/medical-reports/appointment/${aptId}`, {
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
      // 404 means not reviewed yet
      if (err.response?.status === 404) {
        setReviewStatus('pending');
      }
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
      const response = await axios.get('https://medichain.clinic/api/appointments', {
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
      const appointmentsResponse = await axios.get('https://medichain.clinic/api/appointments', {
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
      detailed_results_count: apptData.ai_diagnosis?.detailed_results?.length || 0
    });

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

      const response = await axios.get(`https://medichain.clinic/api/medical-reports/appointment/${apptId}`, {
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
      if (err.response?.status === 404) {
        console.log('No existing medical report found - this is normal for new appointments');
      } else {
        console.warn('Error loading medical report:', err.response?.data?.error || err.message);
      }
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

      const response = await axios.post('https://medichain.clinic/api/medical-reports', medicalReportData, {
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

  const slides = [
    {
      title: 'Possible Conditions',
      content: (
        <div className="slide-content">
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
    </div>
  );
};

export default DoctorAIDiagnosisReview;


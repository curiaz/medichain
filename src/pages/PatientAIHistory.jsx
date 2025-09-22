import React, { useState, useEffect } from 'react';
import { Calendar, Brain, User, Clock, FileText, AlertCircle, Search, Eye, Activity } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { showToast } from '../components/CustomToast';
import LoadingSpinner from '../components/LoadingSpinner';

const PatientAIHistory = () => {
  const [selectedPatient, setSelectedPatient] = useState('');
  const [patientList, setPatientList] = useState([]);
  const [aiHistory, setAiHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedConsultation, setSelectedConsultation] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const { user } = useAuth();

  useEffect(() => {
    loadPatientList();
  }, []);

  const loadPatientList = async () => {
    try {
      // This would typically fetch from your backend API
      // For now, using mock data
      const mockPatients = [
        { id: '1', name: 'John Doe', email: 'john@example.com', last_consultation: '2024-01-15' },
        { id: '2', name: 'Jane Smith', email: 'jane@example.com', last_consultation: '2024-01-14' },
        { id: '3', name: 'Mike Johnson', email: 'mike@example.com', last_consultation: '2024-01-13' },
      ];
      setPatientList(mockPatients);
    } catch (error) {
      console.error('Error loading patient list:', error);
      showToast.error('Failed to load patient list');
    }
  };

  const loadPatientAIHistory = async (patientId) => {
    if (!patientId) return;
    
    setLoading(true);
    try {
      // This would typically fetch from your backend API
      // For now, using mock data
      const mockHistory = [
        {
          id: '1',
          patient_id: patientId,
          timestamp: '2024-01-15T10:30:00Z',
          symptoms: 'Persistent headache, fatigue, difficulty concentrating',
          age: 35,
          gender: 'female',
          diagnosis: 'Tension-type headache possibly related to stress',
          confidence: 85,
          prescription: 'Ibuprofen 400mg every 6-8 hours, stress management techniques',
          recommendations: 'Ensure adequate sleep, stay hydrated, consider stress reduction activities',
          doctor_review: null,
          doctor_notes: '',
          modified_prescription: null,
          session_type: 'authenticated'
        },
        {
          id: '2',
          patient_id: patientId,
          timestamp: '2024-01-10T14:15:00Z',
          symptoms: 'Sore throat, mild fever, body aches',
          age: 35,
          gender: 'female',
          diagnosis: 'Viral upper respiratory infection',
          confidence: 92,
          prescription: 'Rest, increased fluid intake, throat lozenges',
          recommendations: 'Monitor temperature, return if symptoms worsen or persist beyond 7 days',
          doctor_review: 'Reviewed',
          doctor_notes: 'Patient recovered well. Advised to continue current treatment.',
          modified_prescription: null,
          session_type: 'authenticated'
        },
        {
          id: '3',
          patient_id: patientId,
          timestamp: '2024-01-05T09:45:00Z',
          symptoms: 'Intermittent chest pain, shortness of breath during exercise',
          age: 35,
          gender: 'female',
          diagnosis: 'Exercise-induced chest discomfort, likely musculoskeletal',
          confidence: 78,
          prescription: 'Gradual increase in exercise intensity, proper warm-up routine',
          recommendations: 'Schedule cardiac evaluation if symptoms persist or worsen',
          doctor_review: 'Reviewed',
          doctor_notes: 'Recommended ECG and stress test. Results normal. Cleared for exercise.',
          modified_prescription: 'Cleared for normal activities. Continue gradual exercise progression.',
          session_type: 'authenticated'
        }
      ];
      
      setAiHistory(mockHistory);
    } catch (error) {
      console.error('Error loading AI history:', error);
      showToast.error('Failed to load patient AI history');
    } finally {
      setLoading(false);
    }
  };

  const handlePatientSelect = (patientId) => {
    setSelectedPatient(patientId);
    setSelectedConsultation(null);
    loadPatientAIHistory(patientId);
  };

  const handleConsultationSelect = (consultation) => {
    setSelectedConsultation(consultation);
  };

  const submitDoctorReview = async (consultationId, notes, modifiedPrescription) => {
    try {
      // This would typically send to your backend API
      const updatedHistory = aiHistory.map(consultation => {
        if (consultation.id === consultationId) {
          return {
            ...consultation,
            doctor_review: 'Reviewed',
            doctor_notes: notes,
            modified_prescription: modifiedPrescription,
            reviewed_by: user.id,
            reviewed_at: new Date().toISOString()
          };
        }
        return consultation;
      });
      
      setAiHistory(updatedHistory);
      showToast.success('Doctor review submitted successfully');
      
      // Update selected consultation
      const updatedConsultation = updatedHistory.find(c => c.id === consultationId);
      setSelectedConsultation(updatedConsultation);
      
    } catch (error) {
      console.error('Error submitting review:', error);
      showToast.error('Failed to submit doctor review');
    }
  };

  const filteredPatients = patientList.filter(patient =>
    patient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const selectedPatientInfo = patientList.find(p => p.id === selectedPatient);

  return (
    <div className="patient-ai-history-container">
      <div className="history-header">
        <h2>
          <Brain size={24} />
          Patient AI Consultation History
        </h2>
        <p>Review and manage AI-generated diagnoses for your patients</p>
      </div>

      <div className="history-content">
        <div className="patient-selection-panel">
          <div className="search-section">
            <h3>
              <User size={20} />
              Select Patient
            </h3>
            <div className="search-input-group">
              <Search size={16} />
              <input
                type="text"
                placeholder="Search patients..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
            </div>
          </div>

          <div className="patient-list">
            {filteredPatients.map(patient => (
              <div
                key={patient.id}
                className={`patient-item ${selectedPatient === patient.id ? 'selected' : ''}`}
                onClick={() => handlePatientSelect(patient.id)}
              >
                <div className="patient-info">
                  <div className="patient-name">{patient.name}</div>
                  <div className="patient-email">{patient.email}</div>
                  <div className="last-consultation">
                    <Clock size={12} />
                    Last consultation: {new Date(patient.last_consultation).toLocaleDateString()}
                  </div>
                </div>
                {selectedPatient === patient.id && (
                  <div className="selected-indicator">
                    <Eye size={16} />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="consultation-history-panel">
          {selectedPatientInfo && (
            <div className="selected-patient-header">
              <h3>AI Consultations for {selectedPatientInfo.name}</h3>
              <div className="consultation-stats">
                <span className="stat">
                  <Activity size={16} />
                  {aiHistory.length} consultations
                </span>
                <span className="stat">
                  <FileText size={16} />
                  {aiHistory.filter(c => c.doctor_review).length} reviewed
                </span>
              </div>
            </div>
          )}

          {loading && (
            <div className="loading-section">
              <LoadingSpinner />
              <span>Loading consultation history...</span>
            </div>
          )}

          {!selectedPatient && !loading && (
            <div className="no-selection">
              <Brain size={48} />
              <h3>Select a Patient</h3>
              <p>Choose a patient from the list to view their AI consultation history</p>
            </div>
          )}

          {selectedPatient && !loading && aiHistory.length === 0 && (
            <div className="no-history">
              <FileText size={48} />
              <h3>No AI Consultations</h3>
              <p>This patient hasn't used the AI health assistant yet</p>
            </div>
          )}

          {aiHistory.length > 0 && (
            <div className="consultation-list">
              {aiHistory.map(consultation => (
                <div
                  key={consultation.id}
                  className={`consultation-item ${selectedConsultation?.id === consultation.id ? 'selected' : ''}`}
                  onClick={() => handleConsultationSelect(consultation)}
                >
                  <div className="consultation-header">
                    <div className="consultation-date">
                      <Calendar size={16} />
                      {new Date(consultation.timestamp).toLocaleDateString()} at {' '}
                      {new Date(consultation.timestamp).toLocaleTimeString()}
                    </div>
                    <div className={`review-status ${consultation.doctor_review ? 'reviewed' : 'pending'}`}>
                      {consultation.doctor_review ? 'Reviewed' : 'Pending Review'}
                    </div>
                  </div>
                  <div className="consultation-preview">
                    <div className="symptoms-preview">
                      <strong>Symptoms:</strong> {consultation.symptoms.substring(0, 100)}
                      {consultation.symptoms.length > 100 && '...'}
                    </div>
                    <div className="diagnosis-preview">
                      <strong>AI Diagnosis:</strong> {consultation.diagnosis}
                      <span className="confidence">({consultation.confidence}% confidence)</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {selectedConsultation && (
          <div className="consultation-detail-panel">
            <ConsultationDetail
              consultation={selectedConsultation}
              onSubmitReview={submitDoctorReview}
              doctorId={user.id}
            />
          </div>
        )}
      </div>

      <style jsx>{`
        .patient-ai-history-container {
          padding: 2rem;
          max-width: 1400px;
          margin: 0 auto;
        }

        .history-header {
          margin-bottom: 2rem;
          text-align: center;
        }

        .history-header h2 {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
          color: #333;
          margin-bottom: 0.5rem;
        }

        .history-header p {
          color: #666;
          font-size: 1.1rem;
        }

        .history-content {
          display: grid;
          grid-template-columns: 300px 1fr 400px;
          gap: 2rem;
          min-height: 600px;
        }

        .patient-selection-panel {
          background: white;
          border-radius: 12px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
          overflow: hidden;
        }

        .search-section {
          padding: 1.5rem;
          border-bottom: 1px solid #e0e0e0;
        }

        .search-section h3 {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 1rem;
          color: #333;
        }

        .search-input-group {
          position: relative;
          display: flex;
          align-items: center;
        }

        .search-input-group svg {
          position: absolute;
          left: 12px;
          color: #666;
          z-index: 1;
        }

        .search-input {
          width: 100%;
          padding: 0.75rem 0.75rem 0.75rem 2.5rem;
          border: 1px solid #ddd;
          border-radius: 8px;
          font-size: 0.9rem;
        }

        .patient-list {
          max-height: 500px;
          overflow-y: auto;
        }

        .patient-item {
          padding: 1rem 1.5rem;
          border-bottom: 1px solid #f0f0f0;
          cursor: pointer;
          transition: all 0.3s ease;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .patient-item:hover {
          background: #f8f9fa;
        }

        .patient-item.selected {
          background: #e8f5ff;
          border-left: 4px solid #00d4aa;
        }

        .patient-name {
          font-weight: 600;
          color: #333;
          margin-bottom: 0.25rem;
        }

        .patient-email {
          color: #666;
          font-size: 0.9rem;
          margin-bottom: 0.25rem;
        }

        .last-consultation {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          color: #888;
          font-size: 0.8rem;
        }

        .selected-indicator {
          color: #00d4aa;
        }

        .consultation-history-panel {
          background: white;
          border-radius: 12px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
          overflow: hidden;
        }

        .selected-patient-header {
          padding: 1.5rem;
          border-bottom: 1px solid #e0e0e0;
          background: #f8f9fa;
        }

        .selected-patient-header h3 {
          color: #333;
          margin-bottom: 1rem;
        }

        .consultation-stats {
          display: flex;
          gap: 1rem;
        }

        .stat {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: #666;
          font-size: 0.9rem;
        }

        .loading-section {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 3rem;
          color: #666;
        }

        .no-selection, .no-history {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 3rem;
          text-align: center;
          color: #666;
        }

        .no-selection svg, .no-history svg {
          color: #ddd;
          margin-bottom: 1rem;
        }

        .consultation-list {
          max-height: 500px;
          overflow-y: auto;
        }

        .consultation-item {
          padding: 1.5rem;
          border-bottom: 1px solid #f0f0f0;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .consultation-item:hover {
          background: #f8f9fa;
        }

        .consultation-item.selected {
          background: #e8f5ff;
          border-left: 4px solid #00d4aa;
        }

        .consultation-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .consultation-date {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: #666;
          font-size: 0.9rem;
        }

        .review-status {
          padding: 0.25rem 0.75rem;
          border-radius: 12px;
          font-size: 0.8rem;
          font-weight: 500;
        }

        .review-status.reviewed {
          background: #d4edda;
          color: #155724;
        }

        .review-status.pending {
          background: #fff3cd;
          color: #856404;
        }

        .consultation-preview {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .symptoms-preview, .diagnosis-preview {
          font-size: 0.9rem;
          line-height: 1.4;
        }

        .confidence {
          color: #666;
          font-weight: normal;
          margin-left: 0.5rem;
        }

        .consultation-detail-panel {
          background: white;
          border-radius: 12px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
          overflow: hidden;
          max-height: 600px;
          overflow-y: auto;
        }

        @media (max-width: 1200px) {
          .history-content {
            grid-template-columns: 1fr;
            gap: 1rem;
          }
          
          .consultation-detail-panel {
            max-height: none;
          }
        }
      `}</style>
    </div>
  );
};

// Consultation Detail Component
const ConsultationDetail = ({ consultation, onSubmitReview, doctorId }) => {
  const [doctorNotes, setDoctorNotes] = useState(consultation.doctor_notes || '');
  const [modifiedPrescription, setModifiedPrescription] = useState(consultation.modified_prescription || '');
  const [isEditing, setIsEditing] = useState(!consultation.doctor_review);

  const handleSubmitReview = () => {
    if (!doctorNotes.trim()) {
      showToast.error('Please add doctor notes');
      return;
    }
    
    onSubmitReview(consultation.id, doctorNotes, modifiedPrescription);
    setIsEditing(false);
  };

  return (
    <div className="consultation-detail">
      <div className="detail-header">
        <h3>
          <FileText size={20} />
          Consultation Details
        </h3>
        <div className="consultation-meta">
          <span>{new Date(consultation.timestamp).toLocaleString()}</span>
          <span className={`status ${consultation.doctor_review ? 'reviewed' : 'pending'}`}>
            {consultation.doctor_review ? 'Reviewed' : 'Pending Review'}
          </span>
        </div>
      </div>

      <div className="detail-content">
        <div className="detail-section">
          <h4>Patient Information</h4>
          <div className="patient-data">
            <span><strong>Age:</strong> {consultation.age}</span>
            <span><strong>Gender:</strong> {consultation.gender}</span>
          </div>
        </div>

        <div className="detail-section">
          <h4>Symptoms Reported</h4>
          <p className="symptoms-text">{consultation.symptoms}</p>
        </div>

        <div className="detail-section">
          <h4>AI Diagnosis</h4>
          <div className="ai-diagnosis">
            <p><strong>Diagnosis:</strong> {consultation.diagnosis}</p>
            <div className="confidence-indicator">
              <span>Confidence Level: {consultation.confidence}%</span>
              <div className="confidence-bar">
                <div 
                  className="confidence-fill" 
                  style={{ width: `${consultation.confidence}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        <div className="detail-section">
          <h4>AI Prescription</h4>
          <p className="prescription-text">{consultation.prescription}</p>
        </div>

        <div className="detail-section">
          <h4>AI Recommendations</h4>
          <p className="recommendations-text">{consultation.recommendations}</p>
        </div>

        <div className="detail-section doctor-review-section">
          <h4>Doctor Review</h4>
          
          {isEditing ? (
            <div className="review-form">
              <div className="form-group">
                <label>Doctor Notes *</label>
                <textarea
                  value={doctorNotes}
                  onChange={(e) => setDoctorNotes(e.target.value)}
                  placeholder="Add your professional assessment and notes..."
                  rows={4}
                  className="form-textarea"
                />
              </div>
              
              <div className="form-group">
                <label>Modified Prescription (if needed)</label>
                <textarea
                  value={modifiedPrescription}
                  onChange={(e) => setModifiedPrescription(e.target.value)}
                  placeholder="Enter modified prescription or leave blank if AI prescription is appropriate..."
                  rows={3}
                  className="form-textarea"
                />
              </div>
              
              <div className="review-actions">
                <button onClick={handleSubmitReview} className="submit-review-btn">
                  Submit Review
                </button>
                {consultation.doctor_review && (
                  <button onClick={() => setIsEditing(false)} className="cancel-edit-btn">
                    Cancel
                  </button>
                )}
              </div>
            </div>
          ) : (
            <div className="review-display">
              <div className="doctor-notes">
                <strong>Doctor Notes:</strong>
                <p>{consultation.doctor_notes}</p>
              </div>
              
              {consultation.modified_prescription && (
                <div className="modified-prescription">
                  <strong>Modified Prescription:</strong>
                  <p>{consultation.modified_prescription}</p>
                </div>
              )}
              
              <div className="review-meta">
                <span>Reviewed on: {new Date(consultation.reviewed_at || consultation.timestamp).toLocaleString()}</span>
              </div>
              
              <button onClick={() => setIsEditing(true)} className="edit-review-btn">
                Edit Review
              </button>
            </div>
          )}
        </div>
      </div>

      <style jsx>{`
        .consultation-detail {
          height: 100%;
          display: flex;
          flex-direction: column;
        }

        .detail-header {
          padding: 1.5rem;
          border-bottom: 1px solid #e0e0e0;
          background: #f8f9fa;
        }

        .detail-header h3 {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: #333;
          margin-bottom: 0.5rem;
        }

        .consultation-meta {
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-size: 0.9rem;
          color: #666;
        }

        .status {
          padding: 0.25rem 0.75rem;
          border-radius: 12px;
          font-size: 0.8rem;
          font-weight: 500;
        }

        .status.reviewed {
          background: #d4edda;
          color: #155724;
        }

        .status.pending {
          background: #fff3cd;
          color: #856404;
        }

        .detail-content {
          flex: 1;
          padding: 1.5rem;
          overflow-y: auto;
        }

        .detail-section {
          margin-bottom: 2rem;
        }

        .detail-section h4 {
          color: #333;
          margin-bottom: 0.75rem;
          font-size: 1rem;
          border-bottom: 1px solid #e0e0e0;
          padding-bottom: 0.5rem;
        }

        .patient-data {
          display: flex;
          gap: 2rem;
          font-size: 0.9rem;
        }

        .symptoms-text, .prescription-text, .recommendations-text {
          line-height: 1.6;
          color: #333;
          background: #f8f9fa;
          padding: 1rem;
          border-radius: 8px;
          border-left: 4px solid #00d4aa;
        }

        .ai-diagnosis {
          background: #f8f9fa;
          padding: 1rem;
          border-radius: 8px;
          border-left: 4px solid #007bff;
        }

        .confidence-indicator {
          margin-top: 1rem;
        }

        .confidence-bar {
          width: 100%;
          height: 8px;
          background: #e0e0e0;
          border-radius: 4px;
          overflow: hidden;
          margin-top: 0.5rem;
        }

        .confidence-fill {
          height: 100%;
          background: linear-gradient(90deg, #ff6b6b 0%, #feca57 50%, #48cab2 100%);
          transition: width 0.3s ease;
        }

        .doctor-review-section {
          background: #fff8f0;
          padding: 1.5rem;
          border-radius: 8px;
          border: 1px solid #ffe4b5;
        }

        .form-group {
          margin-bottom: 1rem;
        }

        .form-group label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 500;
          color: #333;
        }

        .form-textarea {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid #ddd;
          border-radius: 6px;
          font-family: inherit;
          font-size: 0.9rem;
          line-height: 1.5;
          resize: vertical;
        }

        .review-actions {
          display: flex;
          gap: 1rem;
          margin-top: 1rem;
        }

        .submit-review-btn, .edit-review-btn {
          padding: 0.75rem 1.5rem;
          background: #00d4aa;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-weight: 500;
          transition: background 0.3s ease;
        }

        .submit-review-btn:hover, .edit-review-btn:hover {
          background: #00b899;
        }

        .cancel-edit-btn {
          padding: 0.75rem 1.5rem;
          background: #6c757d;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-weight: 500;
        }

        .cancel-edit-btn:hover {
          background: #5a6268;
        }

        .review-display {
          background: white;
          padding: 1rem;
          border-radius: 6px;
        }

        .doctor-notes, .modified-prescription {
          margin-bottom: 1rem;
        }

        .doctor-notes p, .modified-prescription p {
          margin-top: 0.5rem;
          line-height: 1.6;
          color: #333;
        }

        .review-meta {
          font-size: 0.9rem;
          color: #666;
          margin-bottom: 1rem;
        }
      `}</style>
    </div>
  );
};

export default PatientAIHistory;

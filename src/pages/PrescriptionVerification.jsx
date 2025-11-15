import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../assets/styles/PrescriptionVerification.css';

const PrescriptionVerification = () => {
  const { appointmentId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [verificationResult, setVerificationResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (appointmentId) {
      verifyPrescription(appointmentId);
    } else {
      setError('Invalid prescription link');
      setLoading(false);
    }
  }, [appointmentId]);

  const verifyPrescription = async (id) => {
    try {
      setLoading(true);
      setError(null);

      const response = await axios.get(
        `http://localhost:5000/api/prescription/verify/${id}`
      );

      if (response.data.success) {
        setVerificationResult(response.data);
      } else {
        setError(response.data.error || 'Verification failed');
      }
    } catch (err) {
      console.error('Verification error:', err);
      setError(err.response?.data?.error || 'Failed to verify prescription');
    } finally {
      setLoading(false);
    }
  };

  const handleMarkDispensed = async () => {
    if (!window.confirm('Mark this prescription as dispensed? This action cannot be undone.')) {
      return;
    }

    try {
      const response = await axios.post(
        `http://localhost:5000/api/prescription/mark-dispensed/${appointmentId}`
      );

      if (response.data.success) {
        // Refresh verification to show updated status
        await verifyPrescription(appointmentId);
        alert('Prescription marked as dispensed successfully');
      }
    } catch (err) {
      console.error('Error marking as dispensed:', err);
      alert('Failed to mark prescription as dispensed');
    }
  };

  if (loading) {
    return (
      <div className="verification-container">
        <div className="verification-loading">
          <div className="spinner"></div>
          <p>Verifying prescription...</p>
        </div>
      </div>
    );
  }

  if (error && !verificationResult) {
    return (
      <div className="verification-container">
        <div className="verification-error">
          <div className="error-icon">❌</div>
          <h1>Verification Error</h1>
          <p>{error}</p>
          <button onClick={() => navigate('/')} className="btn-primary">
            Go to Home
          </button>
        </div>
      </div>
    );
  }

  const isValid = verificationResult?.valid;
  const prescription = verificationResult?.prescription;
  const errorType = verificationResult?.error;

  return (
    <div className="verification-container">
      <div className="verification-card">
        {isValid ? (
          <>
            {/* Valid Prescription */}
            <div className="verification-header valid">
              <div className="status-icon">✅</div>
              <h1>VALID PRESCRIPTION</h1>
              <p className="status-subtitle">This prescription has been verified</p>
            </div>

            <div className="prescription-details">
              <div className="detail-section">
                <h2>Patient Information</h2>
                <div className="detail-item">
                  <span className="detail-label">Patient Name:</span>
                  <span className="detail-value">{prescription.patient_name}</span>
                </div>
              </div>

              <div className="detail-section">
                <h2>Doctor Information</h2>
                <div className="detail-item">
                  <span className="detail-label">Doctor Name:</span>
                  <span className="detail-value">{prescription.doctor_name}</span>
                </div>
              </div>

              {prescription.diagnosis && (
                <div className="detail-section">
                  <h2>Diagnosis</h2>
                  <p className="diagnosis-text">{prescription.diagnosis}</p>
                </div>
              )}

              {prescription.medications && prescription.medications.length > 0 && (
                <div className="detail-section">
                  <h2>Medications</h2>
                  <div className="medications-list">
                    {prescription.medications.map((med, idx) => (
                      <div key={idx} className="medication-item">
                        <div className="medication-name">
                          <strong>{med.name || med.medicine || 'Medication'}</strong>
                        </div>
                        {med.dosage && (
                          <div className="medication-detail">
                            <span className="med-label">Dosage:</span>
                            <span>{med.dosage || med.adult_dose || 'As directed'}</span>
                          </div>
                        )}
                        {med.duration && (
                          <div className="medication-detail">
                            <span className="med-label">Duration:</span>
                            <span>{med.duration}</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {prescription.instructions && (
                <div className="detail-section">
                  <h2>Instructions</h2>
                  <p className="instructions-text">{prescription.instructions}</p>
                </div>
              )}

              <div className="detail-section">
                <h2>Prescription Details</h2>
                <div className="detail-item">
                  <span className="detail-label">Date:</span>
                  <span className="detail-value">{prescription.date || 'N/A'}</span>
                </div>
                {prescription.expiry_date && (
                  <div className="detail-item">
                    <span className="detail-label">Expiry Date:</span>
                    <span className="detail-value">{prescription.expiry_date}</span>
                  </div>
                )}
                <div className="detail-item">
                  <span className="detail-label">Status:</span>
                  <span className="detail-value status-badge active">{prescription.status}</span>
                </div>
              </div>

              <div className="verification-actions">
                <button
                  onClick={handleMarkDispensed}
                  className="btn-dispense"
                >
                  Mark as Dispensed
                </button>
              </div>
            </div>
          </>
        ) : (
          <>
            {/* Invalid Prescription */}
            <div className="verification-header invalid">
              <div className="status-icon">❌</div>
              <h1>INVALID PRESCRIPTION</h1>
              <p className="status-subtitle">{verificationResult?.message || 'This prescription cannot be verified'}</p>
            </div>

            <div className="error-details">
              <div className="error-type">
                <strong>Error Type:</strong> {errorType || 'UNKNOWN_ERROR'}
              </div>
              <div className="error-message">
                <p>{verificationResult?.details || 'This prescription link is invalid or has been tampered with.'}</p>
              </div>

              {errorType === 'ALREADY_DISPENSED' && verificationResult?.dispensed_at && (
                <div className="error-info">
                  <p>This prescription was dispensed on: {verificationResult.dispensed_at}</p>
                </div>
              )}

              {errorType === 'EXPIRED' && verificationResult?.expiry_date && (
                <div className="error-info">
                  <p>This prescription expired on: {verificationResult.expiry_date}</p>
                </div>
              )}
            </div>
          </>
        )}

        <div className="verification-footer">
          <button onClick={() => navigate('/')} className="btn-secondary">
            Go to Home
          </button>
        </div>
      </div>
    </div>
  );
};

export default PrescriptionVerification;


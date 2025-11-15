import React, { useState, useEffect } from 'react';
import { X, FileText, Download, Mail, Phone, Calendar, Stethoscope, CheckCircle, XCircle } from 'lucide-react';
import adminService from '../services/adminService';
import './DoctorDetailsModal.css';

const DoctorDetailsModal = ({ doctor, onClose, onApprove, onDecline }) => {
  const [documentUrl, setDocumentUrl] = useState(null);
  const [loadingDoc, setLoadingDoc] = useState(false);

  const userInfo = doctor.user_info || {};
  const fullName = `${userInfo.first_name || ''} ${userInfo.last_name || ''}`.trim();

  const handleDownloadDocument = async () => {
    try {
      setLoadingDoc(true);
      const blob = await adminService.getDoctorDocument(doctor.id);
      
      // Create a URL for the blob
      const url = window.URL.createObjectURL(blob);
      setDocumentUrl(url);
      
      // Create a temporary link and trigger download
      const link = document.createElement('a');
      link.href = url;
      link.download = `doctor_verification_${doctor.id}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Clean up the URL after a delay
      setTimeout(() => window.URL.revokeObjectURL(url), 100);
    } catch (error) {
      alert('Failed to download document. Please try again.');
      console.error('Error downloading document:', error);
    } finally {
      setLoadingDoc(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  useEffect(() => {
    // Clean up URL on unmount
    return () => {
      if (documentUrl) {
        window.URL.revokeObjectURL(documentUrl);
      }
    };
  }, [documentUrl]);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content doctor-details-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title-section">
            <div className="doctor-avatar-large">
              <Stethoscope size={32} />
            </div>
            <div>
              <h2>Dr. {fullName || 'N/A'}</h2>
              <p className="doctor-email">{userInfo.email || 'N/A'}</p>
            </div>
          </div>
          <button className="close-button" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <div className="modal-body">
          <div className="details-section">
            <h3>Personal Information</h3>
            <div className="details-grid">
              <div className="detail-item">
                <div className="detail-label">
                  <Mail size={16} />
                  Email
                </div>
                <div className="detail-value">{userInfo.email || 'N/A'}</div>
              </div>
              {userInfo.phone && (
                <div className="detail-item">
                  <div className="detail-label">
                    <Phone size={16} />
                    Phone
                  </div>
                  <div className="detail-value">{userInfo.phone}</div>
                </div>
              )}
              <div className="detail-item">
                <div className="detail-label">
                  <Calendar size={16} />
                  Registration Date
                </div>
                <div className="detail-value">{formatDate(doctor.created_at)}</div>
              </div>
            </div>
          </div>

          <div className="details-section">
            <h3>Professional Information</h3>
            <div className="details-grid">
              <div className="detail-item">
                <div className="detail-label">
                  <Stethoscope size={16} />
                  Specialization
                </div>
                <div className="detail-value">
                  <span className="specialization-badge">{doctor.specialization || 'General Practitioner'}</span>
                </div>
              </div>
              <div className="detail-item">
                <div className="detail-label">
                  Status
                </div>
                <div className="detail-value">
                  <span className="status-badge status-pending">Pending Verification</span>
                </div>
              </div>
            </div>
          </div>

          <div className="details-section">
            <h3>Verification Document</h3>
            <div className="document-section">
              <div className="document-info">
                <FileText size={20} />
                <div>
                  <p className="document-name">Verification Document</p>
                  <p className="document-hint">Review the uploaded document before approving</p>
                </div>
              </div>
              <button
                className="download-button"
                onClick={handleDownloadDocument}
                disabled={loadingDoc}
              >
                {loadingDoc ? (
                  <>
                    <div className="spinner-small"></div>
                    Downloading...
                  </>
                ) : (
                  <>
                    <Download size={16} />
                    Download Document
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>
            Cancel
          </button>
          <button className="btn-decline" onClick={onDecline}>
            <XCircle size={16} />
            Decline
          </button>
          <button className="btn-approve" onClick={onApprove}>
            <CheckCircle size={16} />
            Approve Doctor
          </button>
        </div>
      </div>
    </div>
  );
};

export default DoctorDetailsModal;


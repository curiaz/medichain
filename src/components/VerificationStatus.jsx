import React from 'react';
import { Clock, Mail, FileText, AlertCircle } from 'lucide-react';
import './VerificationStatus.css';

const VerificationStatus = ({ status, userType, doctorProfile }) => {
  if (userType !== 'doctor' || !doctorProfile) {
    return null;
  }

  const getStatusConfig = (verificationStatus) => {
    switch (verificationStatus) {
      case 'pending':
        return {
          icon: <Clock size={24} />,
          title: 'Verification Pending',
          message: 'Your doctor account is under review. You\'ll receive an email once verification is complete.',
          className: 'verification-pending',
          bgColor: '#fff3cd',
          borderColor: '#ffc107',
          textColor: '#856404'
        };
      case 'approved':
        return {
          icon: <FileText size={24} />,
          title: 'Verified Doctor',
          message: 'Your medical credentials have been verified. You have full access to all doctor features.',
          className: 'verification-approved',
          bgColor: '#d4edda',
          borderColor: '#28a745',
          textColor: '#155724'
        };
      case 'declined':
        return {
          icon: <AlertCircle size={24} />,
          title: 'Verification Declined',
          message: 'Your verification was not approved. Please contact support for more information.',
          className: 'verification-declined',
          bgColor: '#f8d7da',
          borderColor: '#dc3545',
          textColor: '#721c24'
        };
      default:
        return null;
    }
  };

  const config = getStatusConfig(status);
  
  if (!config) return null;

  return (
    <div 
      className={`verification-status ${config.className}`}
      style={{
        backgroundColor: config.bgColor,
        borderColor: config.borderColor,
        color: config.textColor
      }}
    >
      <div className="verification-status-header">
        <div className="verification-icon" style={{ color: config.textColor }}>
          {config.icon}
        </div>
        <div className="verification-content">
          <h3 className="verification-title">{config.title}</h3>
          <p className="verification-message">{config.message}</p>
        </div>
      </div>
      
      {status === 'pending' && (
        <div className="verification-details">
          <div className="verification-detail-item">
            <Mail size={16} />
            <span>Check your email for updates</span>
          </div>
          <div className="verification-detail-item">
            <FileText size={16} />
            <span>Specialization: {doctorProfile.specialization}</span>
          </div>
        </div>
      )}
      
      {status === 'declined' && (
        <div className="verification-actions">
          <button className="reapply-btn">
            Contact Support
          </button>
        </div>
      )}
    </div>
  );
};

export default VerificationStatus;
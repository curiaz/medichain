import React from 'react';
import { Clock, Mail, FileText, AlertCircle, ShieldCheck } from 'lucide-react';
import './VerificationStatus.css';

const VerificationStatus = ({ status, userType, doctorProfile }) => {
  if (userType !== 'doctor' || !doctorProfile) {
    return null;
  }

  const getStatusConfig = (verificationStatus) => {
    switch (verificationStatus) {
      case 'pending':
        return {
          icon: <Clock size={20} />,
          title: 'Verification Pending',
          message: "Your credentials are under review. You'll receive an email once verification is complete.",
          className: 'verification-pending',
          badgeClass: 'status-badge pending',
          badgeText: 'Pending'
        };
      case 'approved':
        return {
          icon: <ShieldCheck size={20} />,
          title: 'Verified Doctor',
          message: 'Your medical credentials have been verified. You now have full access to all doctor features.',
          className: 'verification-approved',
          badgeClass: 'status-badge approved',
          badgeText: 'Verified'
        };
      case 'declined':
        return {
          icon: <AlertCircle size={20} />,
          title: 'Verification Declined',
          message: 'Your verification was not approved. Please contact support for next steps.',
          className: 'verification-declined',
          badgeClass: 'status-badge declined',
          badgeText: 'Declined'
        };
      default:
        return null;
    }
  };

  const config = getStatusConfig(status);
  if (!config) return null;

  return (
    <div className={`verification-status ${config.className}`}>
      <div className="verification-status-header">
        <div className="verification-icon" aria-hidden>
          {config.icon}
        </div>
        <div className="verification-content">
          <div className={config.badgeClass} style={{ marginBottom: 6 }}>
            {config.icon}
            <span>{config.badgeText}</span>
          </div>
          <h3 className="verification-title">{config.title}</h3>
          <p className="verification-message">{config.message}</p>
          {doctorProfile?.specialization && (
            <div className="verification-meta">
              <FileText size={14} />
              <span>Specialization: {doctorProfile.specialization}</span>
            </div>
          )}
        </div>
      </div>

      {status === 'pending' && (
        <div className="verification-details">
          <div className="verification-detail-item">
            <Mail size={16} />
            <span>We will notify you by email when the review is complete</span>
          </div>
          <div className="verification-detail-item">
            <Clock size={16} />
            <span>Typical review time: within 24 hours</span>
          </div>
        </div>
      )}

      {status === 'declined' && (
        <div className="verification-actions">
          <button className="reapply-btn" onClick={() => window.open('mailto:medichain173@gmail.com?subject=Doctor Verification Support') }>
            Contact Support
          </button>
        </div>
      )}
    </div>
  );
};

export default VerificationStatus;
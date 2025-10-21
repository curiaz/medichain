import React, { useState, useEffect } from 'react';
import { Clock, Mail, FileText, AlertCircle, ShieldCheck, RefreshCw } from 'lucide-react';
import axios from 'axios';
import { auth } from '../config/firebase';
import './VerificationStatus.css';

const VerificationStatus = ({ status, userType, doctorProfile }) => {
  const [canResend, setCanResend] = useState(false);
  const [hoursRemaining, setHoursRemaining] = useState(0);
  const [resending, setResending] = useState(false);
  const [message, setMessage] = useState(null);
  const [lastRequestSent, setLastRequestSent] = useState(null);
  const [showApprovedCard, setShowApprovedCard] = useState(true);
  const [isHiding, setIsHiding] = useState(false);

  // Auto-hide approved verification status after 4 seconds, with fade animation
  useEffect(() => {
    if (status === 'approved' && userType === 'doctor') {
      // Start hiding animation at 4 seconds
      const hideTimer = setTimeout(() => {
        setIsHiding(true);
      }, 4000);

      // Actually remove component at 5 seconds (after animation completes)
      const removeTimer = setTimeout(() => {
        setShowApprovedCard(false);
      }, 5000);

      return () => {
        clearTimeout(hideTimer);
        clearTimeout(removeTimer);
      };
    }
  }, [status, userType]);

  // Fetch verification status on mount
  useEffect(() => {
    if (status === 'pending' && userType === 'doctor') {
      fetchVerificationStatus();
    }
  }, [status, userType]);

  // Update timer every minute
  useEffect(() => {
    if (!canResend && hoursRemaining > 0) {
      const interval = setInterval(() => {
        fetchVerificationStatus();
      }, 60000); // Update every minute

      return () => clearInterval(interval);
    }
  }, [canResend, hoursRemaining]);

  const fetchVerificationStatus = async () => {
    try {
      const currentUser = auth.currentUser;
      if (!currentUser) return;

      const token = await currentUser.getIdToken();
      const response = await axios.get(
        `http://localhost:5000/api/auth/verification-status?firebase_uid=${currentUser.uid}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.data.success) {
        setCanResend(response.data.can_resend);
        setHoursRemaining(response.data.hours_remaining || 0);
        setLastRequestSent(response.data.last_request_sent);
      }
    } catch (error) {
      console.error('Error fetching verification status:', error);
    }
  };

  const handleResendRequest = async () => {
    try {
      setResending(true);
      setMessage(null);

      const currentUser = auth.currentUser;
      if (!currentUser) {
        setMessage({ type: 'error', text: 'Please log in to continue' });
        return;
      }

      const token = await currentUser.getIdToken();
      const response = await axios.post(
        'http://localhost:5000/api/auth/resend-verification-request',
        { firebase_uid: currentUser.uid },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.data.success) {
        setMessage({ 
          type: 'success', 
          text: 'Verification request resent successfully! Admin will review within 24 hours.' 
        });
        setCanResend(false);
        setHoursRemaining(24);
        fetchVerificationStatus();
      }
    } catch (error) {
      console.error('Error resending verification:', error);
      if (error.response?.status === 429) {
        setMessage({ 
          type: 'error', 
          text: error.response.data.message || 'Please wait before requesting again' 
        });
      } else {
        setMessage({ 
          type: 'error', 
          text: error.response?.data?.error || 'Failed to resend verification request' 
        });
      }
    } finally {
      setResending(false);
    }
  };

  const formatTimeRemaining = (hours) => {
    if (hours < 1) {
      const minutes = Math.ceil(hours * 60);
      return `${minutes} minute${minutes !== 1 ? 's' : ''}`;
    }
    const roundedHours = Math.ceil(hours);
    return `${roundedHours} hour${roundedHours !== 1 ? 's' : ''}`;
  };

  if (userType !== 'doctor' || !doctorProfile) {
    return null;
  }

  // Hide approved status after timer expires
  if (status === 'approved' && !showApprovedCard) {
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
    <div className={`verification-status ${config.className} ${isHiding ? 'hiding' : ''}`}>
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
          {message && (
            <div className={`verification-message-alert ${message.type}`}>
              {message.type === 'success' ? '✓' : '⚠'} {message.text}
            </div>
          )}
          
          <div className="verification-detail-item">
            <Mail size={16} />
            <span>We will notify you by email when the review is complete</span>
          </div>
          <div className="verification-detail-item">
            <Clock size={16} />
            <span>Typical review time: within 24 hours</span>
          </div>
          
          {lastRequestSent && (
            <div className="verification-detail-item">
              <FileText size={16} />
              <span>
                Last request sent: {new Date(lastRequestSent).toLocaleString()}
              </span>
            </div>
          )}

          <div className="verification-actions">
            <button 
              className={`resend-verification-btn ${!canResend || resending ? 'disabled' : ''}`}
              onClick={handleResendRequest}
              disabled={!canResend || resending}
            >
              <RefreshCw size={16} className={resending ? 'spinning' : ''} />
              {resending ? 'Sending...' : canResend ? 'Request Verification Review' : `Available in ${formatTimeRemaining(hoursRemaining)}`}
            </button>
            {!canResend && hoursRemaining > 0 && (
              <p className="cooldown-note">
                To prevent spam, you can request a review once every 24 hours
              </p>
            )}
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
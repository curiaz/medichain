import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { sendPasswordResetEmail } from 'firebase/auth';
import { auth } from '../config/firebase';
import MedichainLogo from '../components/MedichainLogo';
import './ResetPassword.css';

const ResetPassword = () => {
  const navigate = useNavigate();
  
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [emailSent, setEmailSent] = useState(false);

  // Handle email submission for Firebase password reset
  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      await sendPasswordResetEmail(auth, email);
      setSuccess('Password reset email has been sent! Please check your inbox and follow the instructions.');
      setEmailSent(true);
    } catch (error) {
      console.error('Password reset error:', error);
      switch (error.code) {
        case 'auth/user-not-found':
          setError('No account found with this email address');
          break;
        case 'auth/invalid-email':
          setError('Please enter a valid email address');
          break;
        case 'auth/too-many-requests':
          setError('Too many attempts. Please try again later');
          break;
        default:
          setError('Failed to send password reset email. Please try again');
      }
    } finally {
      setLoading(false);
    }
  };

  // Handle resending the reset email
  const handleResendEmail = async () => {
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      await sendPasswordResetEmail(auth, email);
      setSuccess('Password reset email has been sent again!');
    } catch (error) {
      setError('Failed to resend email. Please try again');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="reset-password-container">
      <div className="reset-password-card">
        <div className="reset-password-header">
          <MedichainLogo size={60} />
          <h2>Reset Password</h2>
          <p>{emailSent ? 'Check your email' : 'Enter your email to reset your password'}</p>
        </div>

        <div className="reset-password-form">
          {!emailSent ? (
            <form onSubmit={handleEmailSubmit}>
              <div className="form-group">
                <label htmlFor="email">Email Address</label>
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email address"
                  required
                  disabled={loading}
                />
                <small>We'll send you a secure link to reset your password</small>
              </div>

              <button 
                type="submit" 
                className="reset-btn primary"
                disabled={loading || !email}
              >
                {loading ? 'Sending...' : 'Send Reset Link'}
              </button>
            </form>
          ) : (
            <div className="email-sent-state">
              <div className="email-icon">📧</div>
              <h3>Reset Link Sent!</h3>
              <p>We've sent a password reset link to <strong>{email}</strong></p>
              <p>Please check your email and click the link to reset your password.</p>
              
              <div className="email-actions">
                <button
                  type="button"
                  className="reset-btn secondary"
                  onClick={handleResendEmail}
                  disabled={loading}
                >
                  {loading ? 'Resending...' : 'Resend Email'}
                </button>
                
                <button
                  type="button"
                  className="reset-btn tertiary"
                  onClick={() => {
                    setEmailSent(false);
                    setEmail('');
                    setError('');
                    setSuccess('');
                  }}
                >
                  Use Different Email
                </button>
              </div>
            </div>
          )}

          {/* Error and Success Messages */}
          {error && <div className="message error">{error}</div>}
          {success && <div className="message success">{success}</div>}

          {/* Back to Login Link */}
          <div className="reset-password-footer">
            <Link to="/login" className="back-link">
              ← Back to Login
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResetPassword;
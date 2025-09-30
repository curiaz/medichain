import { useState } from "react"
import "./ResetPassword.css"
import { useNavigate } from "react-router-dom"
import { Mail, ChevronLeft, Lock, Shield, Key } from "lucide-react"
import MedichainLogo from "../components/MedichainLogo"
import LoadingSpinner from "../components/LoadingSpinner"
import { showToast } from "../components/CustomToast"
import axios from 'axios'

const API_URL = 'http://localhost:5000/api'

const ResetPassword = () => {
  const navigate = useNavigate()
  const [step, setStep] = useState(1) // 1: Email, 2: OTP, 3: New Password
  const [email, setEmail] = useState("")
  const [otp, setOtp] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [resetToken, setResetToken] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [otpExpiry, setOtpExpiry] = useState(null)

  const handleEmailSubmit = async (e) => {
    e.preventDefault()
    
    if (isSubmitting) return
    
    if (!email.trim()) {
      showToast.error("Please enter your email address")
      return
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email.trim())) {
      showToast.error("Please enter a valid email address")
      return
    }

    setIsSubmitting(true)
    
    try {
      const response = await axios.post(`${API_URL}/auth/password-reset-request`, {
        email: email.trim()
      })
      
      if (response.data.success) {
        showToast.success("Reset OTP has been sent to your email!")
        setStep(2)
        // Set expiry time for OTP (10 minutes)
        setOtpExpiry(new Date(Date.now() + 10 * 60 * 1000))
      } else {
        showToast.error(response.data.error || "Failed to send reset email")
      }
    } catch (error) {
      console.error('Password reset request error:', error)
      if (error.response?.data?.error) {
        showToast.error(error.response.data.error)
      } else {
        showToast.error("Failed to send reset email. Please try again.")
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleOtpSubmit = async (e) => {
    e.preventDefault()
    
    if (isSubmitting) return
    
    if (!otp.trim()) {
      showToast.error("Please enter the OTP code")
      return
    }

    if (otp.trim().length !== 6) {
      showToast.error("Please enter a valid 6-digit OTP code")
      return
    }

    setIsSubmitting(true)
    
    try {
      const response = await axios.post(`${API_URL}/auth/verify-otp`, {
        email: email.trim(),
        otp: otp.trim()
      })
      
      if (response.data.success) {
        showToast.success("OTP verified successfully!")
        setResetToken(response.data.reset_token)
        setStep(3)
      } else {
        showToast.error(response.data.error || "Invalid OTP code")
      }
    } catch (error) {
      console.error('OTP verification error:', error)
      if (error.response?.data?.error) {
        showToast.error(error.response.data.error)
      } else {
        showToast.error("Failed to verify OTP. Please try again.")
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  const handlePasswordSubmit = async (e) => {
    e.preventDefault()
    
    if (isSubmitting) return
    
    if (!newPassword.trim()) {
      showToast.error("Please enter a new password")
      return
    }

    if (!confirmPassword.trim()) {
      showToast.error("Please confirm your password")
      return
    }

    if (newPassword !== confirmPassword) {
      showToast.error("Passwords do not match")
      return
    }

    if (newPassword.length < 6) {
      showToast.error("Password must be at least 6 characters long")
      return
    }

    setIsSubmitting(true)
    
    try {
      const response = await axios.post(`${API_URL}/auth/password-reset`, {
        email: email.trim(),
        reset_token: resetToken,
        new_password: newPassword
      })
      
      if (response.data.success) {
        showToast.success("Password reset successful! You can now login with your new password.")
        setTimeout(() => {
          navigate("/login")
        }, 2000)
      } else {
        showToast.error(response.data.error || "Failed to reset password")
      }
    } catch (error) {
      console.error('Password reset error:', error)
      if (error.response?.data?.error) {
        showToast.error(error.response.data.error)
      } else {
        showToast.error("Failed to reset password. Please try again.")
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  const resendOtp = async () => {
    if (isSubmitting) return
    
    setIsSubmitting(true)
    
    try {
      const response = await axios.post(`${API_URL}/auth/password-reset-request`, {
        email: email.trim()
      })
      
      if (response.data.success) {
        showToast.success("New OTP has been sent to your email!")
        setOtp("")
        setOtpExpiry(new Date(Date.now() + 10 * 60 * 1000))
      } else {
        showToast.error(response.data.error || "Failed to resend OTP")
      }
    } catch (error) {
      console.error('Resend OTP error:', error)
      showToast.error("Failed to resend OTP. Please try again.")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="reset-password-container">
      {/* Background Animation */}
      <div className="background-crosses">
        {[...Array(20)].map((_, i) => (
          <span key={i} className={`cross cross-${i + 1}`}>
            <div className="cross-symbol">+</div>
          </span>
        ))}
      </div>

      {/* Header */}
      <div className="header">
        <div className="logo-container">
          <MedichainLogo size={36} />
          <h1>MEDICHAIN</h1>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        <div className="reset-form-container">
          <div className="reset-form">
            {/* Step Indicator */}
            <div className="step-indicator">
              <div className={`step ${step >= 1 ? 'active' : ''} ${step > 1 ? 'completed' : ''}`}>
                <Mail size={16} />
                <span>Email</span>
              </div>
              <div className={`step ${step >= 2 ? 'active' : ''} ${step > 2 ? 'completed' : ''}`}>
                <Shield size={16} />
                <span>Verify</span>
              </div>
              <div className={`step ${step >= 3 ? 'active' : ''}`}>
                <Lock size={16} />
                <span>Reset</span>
              </div>
            </div>

            {/* Step 1: Email Input */}
            {step === 1 && (
              <>
                <div className="form-header">
                  <h2>Reset Password</h2>
                  <p>Enter your email address and we'll send you a verification code</p>
                </div>

                <form onSubmit={handleEmailSubmit} className="reset-form-wrapper">
                  <div className="input-group">
                    <label htmlFor="email">Email Address</label>
                    <div className="input-wrapper">
                      <Mail className="input-icon" size={18} />
                      <input
                        id="email"
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="Enter your email address"
                        disabled={isSubmitting}
                        autoFocus
                      />
                    </div>
                  </div>

                  <button 
                    type="submit" 
                    className="reset-btn"
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? (
                      <LoadingSpinner 
                        size="small" 
                        text="Sending OTP..." 
                      />
                    ) : (
                      "Send Verification Code"
                    )}
                  </button>

                  <button
                    type="button"
                    className="back-btn"
                    onClick={() => navigate("/login")}
                    disabled={isSubmitting}
                  >
                    <ChevronLeft size={18} />
                    Back to Login
                  </button>
                </form>
              </>
            )}

            {/* Step 2: OTP Verification */}
            {step === 2 && (
              <>
                <div className="form-header">
                  <h2>Verify Code</h2>
                  <p>Enter the 6-digit verification code sent to <strong>{email}</strong></p>
                </div>

                <form onSubmit={handleOtpSubmit} className="reset-form-wrapper">
                  <div className="input-group">
                    <label htmlFor="otp">Verification Code</label>
                    <div className="input-wrapper">
                      <Key className="input-icon" size={18} />
                      <input
                        id="otp"
                        type="text"
                        value={otp}
                        onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                        placeholder="Enter 6-digit code"
                        disabled={isSubmitting}
                        autoFocus
                        maxLength={6}
                        className="otp-input"
                      />
                    </div>
                  </div>

                  <button 
                    type="submit" 
                    className="reset-btn"
                    disabled={isSubmitting || otp.length !== 6}
                  >
                    {isSubmitting ? (
                      <LoadingSpinner 
                        size="small" 
                        text="Verifying..." 
                      />
                    ) : (
                      "Verify Code"
                    )}
                  </button>

                  <div className="resend-section">
                    <button
                      type="button"
                      className="resend-btn"
                      onClick={resendOtp}
                      disabled={isSubmitting}
                    >
                      Resend Code
                    </button>
                    <span className="resend-text">Didn't receive the code?</span>
                  </div>

                  <button
                    type="button"
                    className="back-btn"
                    onClick={() => setStep(1)}
                    disabled={isSubmitting}
                  >
                    <ChevronLeft size={18} />
                    Change Email
                  </button>
                </form>
              </>
            )}

            {/* Step 3: New Password */}
            {step === 3 && (
              <>
                <div className="form-header">
                  <h2>Create New Password</h2>
                  <p>Enter your new password below</p>
                </div>

                <form onSubmit={handlePasswordSubmit} className="reset-form-wrapper">
                  <div className="input-group">
                    <label htmlFor="newPassword">New Password</label>
                    <div className="input-wrapper">
                      <Lock className="input-icon" size={18} />
                      <input
                        id="newPassword"
                        type="password"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        placeholder="Enter new password"
                        disabled={isSubmitting}
                        autoFocus
                      />
                    </div>
                  </div>

                  <div className="input-group">
                    <label htmlFor="confirmPassword">Confirm Password</label>
                    <div className="input-wrapper">
                      <Lock className="input-icon" size={18} />
                      <input
                        id="confirmPassword"
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        placeholder="Confirm new password"
                        disabled={isSubmitting}
                      />
                    </div>
                  </div>

                  <div className="password-requirements">
                    <p>Password must contain:</p>
                    <ul>
                      <li className={newPassword.length >= 6 ? 'met' : ''}>At least 6 characters</li>
                      <li className={/[A-Z]/.test(newPassword) ? 'met' : ''}>One uppercase letter</li>
                      <li className={/[a-z]/.test(newPassword) ? 'met' : ''}>One lowercase letter</li>
                      <li className={/\d/.test(newPassword) ? 'met' : ''}>One number</li>
                    </ul>
                  </div>

                  <button 
                    type="submit" 
                    className="reset-btn"
                    disabled={isSubmitting || newPassword !== confirmPassword || newPassword.length < 6}
                  >
                    {isSubmitting ? (
                      <LoadingSpinner 
                        size="small" 
                        text="Updating..." 
                      />
                    ) : (
                      "Reset Password"
                    )}
                  </button>

                  <button
                    type="button"
                    className="back-btn"
                    onClick={() => navigate("/login")}
                    disabled={isSubmitting}
                  >
                    <ChevronLeft size={18} />
                    Back to Login
                  </button>
                </form>
              </>
            )}
          </div>

          {/* Info Section */}
          <div className="info-section">
            <div className="info-content">
              {step === 1 && (
                <>
                  <h3>Password Reset Process</h3>
                  <p>
                    We'll send you a 6-digit verification code to your email address. 
                    Make sure to check your spam folder if you don't see it in your inbox.
                  </p>
                  <div className="info-list">
                    <div className="info-item">
                      <span>1</span>
                      <span>Enter your email address</span>
                    </div>
                    <div className="info-item">
                      <span>2</span>
                      <span>Check your email for OTP</span>
                    </div>
                    <div className="info-item">
                      <span>3</span>
                      <span>Create new password</span>
                    </div>
                  </div>
                </>
              )}
              
              {step === 2 && (
                <>
                  <h3>Email Verification</h3>
                  <p>
                    We've sent a 6-digit verification code to your email. 
                    The code will expire in 10 minutes.
                  </p>
                  <div className="info-list">
                    <div className="info-item">
                      <span>✓</span>
                      <span>Check your email inbox</span>
                    </div>
                    <div className="info-item">
                      <span>✓</span>
                      <span>Look for "MediChain Password Reset"</span>
                    </div>
                    <div className="info-item">
                      <span>✓</span>
                      <span>Enter the 6-digit code</span>
                    </div>
                  </div>
                </>
              )}
              
              {step === 3 && (
                <>
                  <h3>Security Guidelines</h3>
                  <p>
                    Create a strong password to keep your account secure.
                  </p>
                  <div className="info-list">
                    <div className="info-item">
                      <span>🔒</span>
                      <span>Use a unique password</span>
                    </div>
                    <div className="info-item">
                      <span>🔑</span>
                      <span>Include mixed characters</span>
                    </div>
                    <div className="info-item">
                      <span>🛡️</span>
                      <span>Avoid personal information</span>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="footer">
        <div className="footer-content">
          <div className="footer-main">
            <strong>© 2025 MediChain</strong> — <em>AI-Driven Diagnosis & Blockchain Health Records System</em>
          </div>
          <div className="footer-sub">
            Powered by Artificial Intelligence, AES & SHA-256 Encryption, and Blockchain Technology
          </div>
          <div className="footer-academic">
            For academic use – Taguig City University | BSCS Thesis Project
          </div>
        </div>
      </div>
    </div>
  )
}

export default ResetPassword

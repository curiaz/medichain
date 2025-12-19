import { useState } from "react"
import "./ResetPassword.css"
import { useNavigate } from "react-router-dom"
import { Eye, EyeOff, Lock, Mail, Plus, ChevronRight, Key } from "lucide-react"
import LoadingSpinner from "../components/LoadingSpinner"
import { showToast } from "../components/CustomToast"
import medichainLogo from "../assets/medichain_logo.png"
import axios from 'axios'
import { API_CONFIG } from '../config/api'

const API_URL = API_CONFIG.API_URL

const ResetPassword = () => {
  const navigate = useNavigate()
  const [step, setStep] = useState(1) // 1: Email, 2: OTP, 3: New Password
  const [email, setEmail] = useState("")
  const [otp, setOtp] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [resetToken, setResetToken] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isRedirecting, setIsRedirecting] = useState(false)

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
        if (response.data.ui_message) {
          showToast.success(response.data.ui_message)
        } else {
          showToast.success("Reset code sent to your email!")
        }
        // Set a dummy OTP for UI continuity with Firebase flow
        if (response.data.session_token) {
          setResetToken(response.data.session_token)
        }
        setStep(2)
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
      showToast.error("Please enter the verification code")
      return
    }

    // For Firebase mode, accept any 6-digit code as verification
    if (otp.trim().length !== 6) {
      showToast.error("Please enter a valid 6-digit code")
      return
    }

    setIsSubmitting(true)
    
    try {
      const response = await axios.post(`${API_URL}/auth/verify-otp`, {
        email: email.trim(),
        otp: otp.trim()
      })
      
      if (response.data.success) {
        if (response.data.firebase_mode && response.data.instructions) {
          showToast.success("Verification successful! " + response.data.instructions)
        } else {
          showToast.success("Code verified successfully!")
        }
        setResetToken(response.data.reset_token)
        setStep(3)
      } else {
        showToast.error(response.data.error || "Invalid verification code")
      }
    } catch (error) {
      console.error('OTP verification error:', error)
      if (error.response?.data?.error) {
        showToast.error(error.response.data.error)
      } else {
        showToast.error("Failed to verify code. Please try again.")
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

    if (newPassword.length < 60) {
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
        setIsRedirecting(true)
        
        if (response.data.instructions) {
          showToast.success("Please complete the reset using the email link!")
          // Show detailed instructions
          console.log("Firebase Reset Instructions:", response.data.instructions)
          setTimeout(() => {
            showToast.success("Redirecting to login page...")
            setTimeout(() => navigate("/login"), 1000)
          }, 2000)
        } else {
          showToast.success("Password updated successfully! Redirecting to login...")
          setTimeout(() => navigate("/login"), 2000)
        }
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
        showToast.success("New code sent to your email!")
        setOtp("")
      } else {
        showToast.error(response.data.error || "Failed to resend code")
      }
    } catch (error) {
      console.error('Resend OTP error:', error)
      showToast.error("Failed to resend code. Please try again.")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="reset-password-container">
      {/* Background crosses */}
      <div className="background-crosses">
        {[...Array(24)].map((_, i) => (
          <span key={i} className={`cross cross-${i + 1}`}>
            <Plus size={24} />
          </span>
        ))}
      </div>

      {/* Header */}
      <div className="header">
        <div className="logo-container" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
          <div className="logo-icon">
            <img src={medichainLogo} alt="MediChain Logo" width={40} height={40} />
          </div>
          <h1>MEDICHAIN</h1>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        <div className="reset-form-container">
          {/* Reset Form */}
          <div className="reset-form">
            <div className="form-content">
              {/* Step 1: Email Input */}
              {step === 1 && (
                <>
                  <div className="form-header">
                    <h2>Reset Password</h2>
                    <p>Enter your email to reset your password</p>
                  </div>

                  {isRedirecting && (
                    <div className="success-message">
                      <div className="success-content">
                        <div className="success-icon">✅</div>
                        <h3>Password Reset Complete!</h3>
                        <p>You will be redirected to the login page shortly...</p>
                      </div>
                    </div>
                  )}

                  <form onSubmit={handleEmailSubmit} className="reset-form-wrapper">
                    <div className="input-group">
                      <label htmlFor="email">Email Address</label>
                      <div className="input-wrapper">
                        <Mail className="input-icon" size={20} />
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
                          text="Sending..." 
                        />
                      ) : (
                        <>
                          Send Reset Code
                          <ChevronRight size={20} />
                        </>
                      )}
                    </button>

                    <div className="divider">
                      <span>or</span>
                    </div>

                    <button 
                      type="button" 
                      className="back-btn" 
                      onClick={() => navigate("/login")}
                      disabled={isSubmitting}
                    >
                      <div className="back-icon">←</div>
                      Back to Login
                    </button>

                    <p className="signup-link">
                      Don't have an account? <span 
                        onClick={() => navigate("/signup")} 
                        className="signup-link-text"
                      >
                        Sign Up
                      </span>
                    </p>
                  </form>
                </>
              )}

              {/* Step 2: OTP Verification */}
              {step === 2 && (
                <>
                  <div className="form-header">
                    <h2>Check Your Email</h2>
                    <p>We sent a password reset email to {email} with two options:</p>
                    <ul style={{textAlign: 'left', marginTop: '10px', color: '#666'}}>
                      <li><strong>Option 1:</strong> Enter the 6-digit verification code below</li>
                      <li><strong>Option 2:</strong> Click the "Reset Password" button in your email</li>
                    </ul>
                  </div>

                  {isRedirecting && (
                    <div className="success-message">
                      <div className="success-content">
                        <div className="success-icon">✅</div>
                        <h3>Password Reset Complete!</h3>
                        <p>You will be redirected to the login page shortly...</p>
                      </div>
                    </div>
                  )}

                  <form onSubmit={handleOtpSubmit} className="reset-form-wrapper">
                    <div className="input-group">
                      <label htmlFor="otp">Verification Code</label>
                      <div className="input-wrapper">
                        <Key className="input-icon" size={20} />
                        <input
                          id="otp"
                          type="tel"
                          inputMode="numeric"
                          pattern="[0-9]*"
                          value={otp}
                          onChange={(e) => {
                            const numericValue = e.target.value.replace(/\D/g, '').slice(0, 6);
                            setOtp(numericValue);
                          }}
                          placeholder="Enter verification code from email"
                          disabled={isSubmitting}
                          autoFocus
                          autoComplete="one-time-code"
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
                        <>
                          Verify & Continue
                          <ChevronRight size={20} />
                        </>
                      )}
                    </button>

                    <div className="divider">
                      <span>or</span>
                    </div>

                    <button
                      type="button"
                      className="resend-btn"
                      onClick={resendOtp}
                      disabled={isSubmitting}
                    >
                      Resend Code
                    </button>

                    <p className="signup-link">
                      Wrong email? <span 
                        onClick={() => setStep(1)} 
                        className="signup-link-text"
                      >
                        Change Email
                      </span>
                    </p>
                  </form>
                </>
              )}

              {/* Step 3: New Password */}
              {step === 3 && (
                <>
                  <div className="form-header">
                    <h2>Complete Password Reset</h2>
                    <p>Click the button below to receive final instructions, or use the Firebase reset link from your email</p>
                  </div>

                  {isRedirecting && (
                    <div className="success-message">
                      <div className="success-content">
                        <div className="success-icon">✅</div>
                        <h3>Password Reset Complete!</h3>
                        <p>You will be redirected to the login page shortly...</p>
                      </div>
                    </div>
                  )}

                  <form onSubmit={handlePasswordSubmit} className="reset-form-wrapper">
                    <div className="input-group">
                      <label htmlFor="newPassword">New Password</label>
                      <div className="input-wrapper">
                        <Lock className="input-icon" size={20} />
                        <input
                          id="newPassword"
                          type={showPassword ? "text" : "password"}
                          value={newPassword}
                          onChange={(e) => setNewPassword(e.target.value)}
                          placeholder="Enter new password"
                          disabled={isSubmitting}
                          autoFocus
                        />
                        <button
                          type="button"
                          className="password-toggle"
                          onClick={() => setShowPassword(!showPassword)}
                          tabIndex={-1}
                        >
                          {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                        </button>
                      </div>
                    </div>

                    <div className="input-group">
                      <label htmlFor="confirmPassword">Confirm Password</label>
                      <div className="input-wrapper">
                        <Lock className="input-icon" size={20} />
                        <input
                          id="confirmPassword"
                          type={showConfirmPassword ? "text" : "password"}
                          value={confirmPassword}
                          onChange={(e) => setConfirmPassword(e.target.value)}
                          placeholder="Confirm new password"
                          disabled={isSubmitting}
                        />
                        <button
                          type="button"
                          className="password-toggle"
                          onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                          tabIndex={-1}
                        >
                          {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                        </button>
                      </div>
                    </div>

                    <button 
                      type="submit" 
                      className="reset-btn"
                      disabled={isSubmitting || isRedirecting || newPassword !== confirmPassword || newPassword.length < 6}
                    >
                      {isSubmitting ? (
                        <LoadingSpinner 
                          size="small" 
                          text="Updating..." 
                        />
                      ) : isRedirecting ? (
                        <LoadingSpinner 
                          size="small" 
                          text="Redirecting to login..." 
                        />
                      ) : (
                        <>
                          Update Password
                          <ChevronRight size={20} />
                        </>
                      )}
                    </button>

                    <p className="signup-link">
                      All set? <span 
                        onClick={() => navigate("/login")} 
                        className="signup-link-text"
                      >
                        Sign In Now
                      </span>
                    </p>
                  </form>
                </>
              )}
            </div>
          </div>

          {/* Info Section */}
          <div className="info-section">
            <div className="info-content">
              <div className="info-icon">
                <Lock size={48} />
              </div>
              <h3>Secure Password Recovery</h3>
              <p>
                Reset your password securely with our encrypted verification system and regain access to your MediChain account.
              </p>
              <div className="info-list">
                <div className="info-item">
                  <span>+</span>
                  <span>Email Verification</span>
                </div>
                <div className="info-item">
                  <span>+</span>
                  <span>Secure Reset Process</span>
                </div>
                <div className="info-item">
                  <span>+</span>
                  <span>Account Protection</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer - Same as Login */}
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

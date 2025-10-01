import { useState } from "react"
import "./MedichainLogin.css"
import { useNavigate } from "react-router-dom"
import { Eye, EyeOff, Lock, Mail, Plus, ChevronRight, Key, Shield } from "lucide-react"
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
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

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
    <div className="medichain-container">
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
            <MedichainLogo size={50} usePng={true} />
          </div>
          <h1>MEDICHAIN</h1>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        <div className="login-container">
          {/* Reset Password Form */}
          <div className="login-form">
            <div className="form-content">


              {/* Step 1: Email Input */}
              {step === 1 && (
                <>
                  <div className="form-header">
                    <h2>Reset Password</h2>
                    <p>Enter your email address to reset your password</p>
                  </div>

                  <form onSubmit={handleEmailSubmit} className="login-form-wrapper">
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
                      className="login-btn"
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
                      className="google-btn" 
                      onClick={() => navigate("/login")}
                      disabled={isSubmitting}
                    >
                      <div className="google-icon">←</div>
                      Back to Login
                    </button>

                    <p className="signup-link">
                      Don't have an account? <span 
                        onClick={() => navigate("/signup")} 
                        className="signup-link-text"
                        style={{ cursor: 'pointer' }}
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
                    <h2>Enter Verification Code</h2>
                    <p>We sent a code to {email}</p>
                  </div>

                  <form onSubmit={handleOtpSubmit} className="login-form-wrapper">
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
                          placeholder="Enter 6-digit code"
                          disabled={isSubmitting}
                          autoFocus
                          autoComplete="one-time-code"
                          maxLength={6}
                          style={{ 
                            textAlign: 'center', 
                            letterSpacing: '0.2em', 
                            fontWeight: '600',
                            fontSize: '1.1em'
                          }}
                        />
                      </div>
                    </div>

                    <button 
                      type="submit" 
                      className="login-btn"
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
                      className="google-btn"
                      onClick={resendOtp}
                      disabled={isSubmitting}
                    >
                      Resend Code
                    </button>

                    <p className="signup-link">
                      Wrong email? <span 
                        onClick={() => setStep(1)} 
                        className="signup-link-text"
                        style={{ cursor: 'pointer' }}
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
                    <h2>Set New Password</h2>
                    <p>Create a strong password for your account</p>
                  </div>

                  <form onSubmit={handlePasswordSubmit} className="login-form-wrapper">
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
                      className="login-btn"
                      disabled={isSubmitting || newPassword !== confirmPassword || newPassword.length < 6}
                    >
                      {isSubmitting ? (
                        <LoadingSpinner 
                          size="small" 
                          text="Updating..." 
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
                        style={{ cursor: 'pointer' }}
                      >
                        Sign In Now
                      </span>
                    </p>
                  </form>
                </>
              )}
            </div>
          </div>

          {/* Doctor Image Section */}
          <div className="doctor-image">
            <div className="doctor-placeholder">
              <div className="doctor-icon">
                <Plus size={48} />
              </div>
              <h3>Secure Account Recovery</h3>
              <p>
                Reset your password securely with our encrypted verification system and regain access to your MediChain account.
              </p>
              <div className="login-feature-list">
                <div className="login-feature-item">
                  <Plus size={16} />
                  <span>Email Verification</span>
                </div>
                <div className="login-feature-item">
                  <Plus size={16} />
                  <span>Secure Reset Process</span>
                </div>
                <div className="login-feature-item">
                  <Plus size={16} />
                  <span>Account Protection</span>
                </div>
              </div>
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
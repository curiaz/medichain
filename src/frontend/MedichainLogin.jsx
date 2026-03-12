import { useState, useEffect } from "react"
import "./MedichainLogin.css"
import "../pages/ProfilePage.css" // For modal styling
import { useNavigate, useLocation, useSearchParams } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import { Eye, EyeOff, Lock, Mail, Plus, ChevronRight, AlertCircle, Check, X } from "lucide-react"
import LoadingSpinner from "../components/LoadingSpinner"
import RoleSelectionModal from "../components/RoleSelectionModal"
import { showToast } from "../components/CustomToast"
import medichainLogo from "../assets/medichain_logo.png"

const MedichainLogin = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const [searchParams] = useSearchParams()
  const { login, isAuthenticated, loading, resendVerification, signInWithGoogle } = useAuth()
  
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [rememberMe, setRememberMe] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [isRoleModalOpen, setIsRoleModalOpen] = useState(false)
  const [showVerificationPrompt, setShowVerificationPrompt] = useState(false)
  const [isResendingVerification, setIsResendingVerification] = useState(false)
  const [showReactivationModal, setShowReactivationModal] = useState(false)
  const [reactivationToken, setReactivationToken] = useState(null)
  const [isReactivating, setIsReactivating] = useState(false)
  const [inlineError, setInlineError] = useState("")
  const [isGoogleSigningIn, setIsGoogleSigningIn] = useState(false)
  const [emailFocused, setEmailFocused] = useState(false)

  const handleSignUpClick = () => {
    setIsRoleModalOpen(true)
  }

  const handleRoleSelect = (role) => {
    if (role === 'doctor') {
      navigate('/signup?role=doctor')
    } else if (role === 'patient') {
      navigate('/signup?role=patient')
    }
  }

  const closeRoleModal = () => {
    setIsRoleModalOpen(false)
  }

  // Load remembered credentials on component mount
  useEffect(() => {
    const rememberedEmail = localStorage.getItem("medichain_remembered_email")
    const rememberedPassword = localStorage.getItem("medichain_remembered_password")
    
    if (rememberedEmail && rememberedPassword) {
      setEmail(rememberedEmail)
      setPassword(rememberedPassword)
      setRememberMe(true)
    }
  }, [])

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated && !loading) {
      const from = location.state?.from?.pathname || "/dashboard"
      navigate(from, { replace: true })
    }
  }, [isAuthenticated, loading, navigate, location])

  // Check for verification status from URL params
  useEffect(() => {
    const verification = searchParams.get('verification')
    const pendingEmail = localStorage.getItem('pending_verification_email')
    
    if (verification === 'pending' && pendingEmail) {
      setEmail(pendingEmail)
      setShowVerificationPrompt(true)
      showToast.info("Please check your email and verify your account before logging in.")
    }
  }, [searchParams])

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (isSubmitting) return
    
    // Basic validation
    if (!email.trim() || !password.trim()) {
      showToast.error("Please fill in all fields")
      setInlineError("Please enter both your email and password.")
      return
    }

    setIsSubmitting(true)
    
    try {
      console.log('🔐 Attempting login...');
      setInlineError("")
      const result = await login(email.trim(), password)
      console.log('📊 Login result:', result);
      
      // Check if account requires reactivation (can happen even if success is false)
      if (result.requiresReactivation) {
        console.log('🔔 Showing reactivation modal');
        setReactivationToken(result.token || null)
        setShowReactivationModal(true)
        setInlineError("") // Clear any error messages
        setIsSubmitting(false)
        // Keep email and password in state for reactivation (already available)
        return
      }
      
      if (result.success) {
        // Handle remember me functionality
        if (rememberMe) {
          localStorage.setItem("medichain_remembered_email", email.trim())
          localStorage.setItem("medichain_remembered_password", password)
        } else {
          localStorage.removeItem("medichain_remembered_email")
          localStorage.removeItem("medichain_remembered_password")
        }
        
        // Clear any pending verification email
        localStorage.removeItem('pending_verification_email')
        
        showToast.success("Login successful!")
        
        // Navigate to intended page or dashboard
        const from = location.state?.from?.pathname || "/dashboard"
        navigate(from, { replace: true })
      } else {
        // Check if it's a verification error
        if (result.requiresVerification) {
          setShowVerificationPrompt(true)
          setInlineError("Your email is not verified yet. Please check your inbox for the verification link.")
          showToast.error("Please verify your email before logging in. Check your inbox for the verification link.")
        } else {
          setInlineError(result.message || "Login failed. Please check your credentials and try again.")
          showToast.error(result.message || "Login failed")
        }
      }
    } catch (error) {
      console.error("Login error:", error)
      setInlineError("An unexpected error occurred. Please try again.")
      showToast.error("An unexpected error occurred. Please try again.")
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleResendVerification = async () => {
    if (!email.trim()) {
      showToast.error("Please enter your email address")
      return
    }

    setIsResendingVerification(true)
    
    try {
      const result = await resendVerification(email.trim())
      
      if (result.success) {
        showToast.success("Verification email sent! Please check your inbox.")
      } else {
        showToast.error(result.error || "Failed to send verification email")
      }
    } catch (error) {
      console.error("Resend verification error:", error)
      showToast.error("Failed to send verification email. Please try again.")
    } finally {
      setIsResendingVerification(false)
    }
  }

  const handleReactivateAccount = async () => {
    setIsReactivating(true)
    
    try {
      // Check if we have a token (authenticated reactivation) or email/password (disabled user reactivation)
      let response;
      
      if (reactivationToken) {
        // User is authenticated - use token-based reactivation
        response = await fetch('https://medichainn.onrender.com/api/auth/reactivate-account', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${reactivationToken}`
          }
        })
      } else if (email && password) {
        // User is disabled (deactivated doctor) - use email/password reactivation
        response = await fetch('https://medichainn.onrender.com/api/auth/reactivate-disabled-account', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            email: email.trim(),
            password: password
          })
        })
      } else {
        showToast.error("Invalid reactivation session. Please try logging in again.")
        return
      }

      const result = await response.json()
      
      if (result.success) {
        showToast.success("Account reactivated successfully! Logging you in...")
        setShowReactivationModal(false)
        
        // Handle remember me functionality
        if (rememberMe) {
          localStorage.setItem("medichain_remembered_email", email.trim())
          localStorage.setItem("medichain_remembered_password", password)
        } else {
          localStorage.removeItem("medichain_remembered_email")
          localStorage.removeItem("medichain_remembered_password")
        }
        
        // Now perform actual login to set auth state properly
        const loginResult = await login(email.trim(), password)
        
        if (loginResult.success) {
          // Navigate to dashboard
          const from = location.state?.from?.pathname || "/dashboard"
          navigate(from, { replace: true })
        } else {
          showToast.error("Reactivated but failed to log in. Please try logging in manually.")
          // Still consider it a success since account was reactivated
          setTimeout(() => {
            window.location.reload()
          }, 2000)
        }
      } else {
        showToast.error(result.error || "Failed to reactivate account")
      }
    } catch (error) {
      console.error("Reactivation error:", error)
      showToast.error("Failed to reactivate account. Please try again.")
    } finally {
      setIsReactivating(false)
    }
  }

  const handleCancelReactivation = () => {
    setShowReactivationModal(false)
    setReactivationToken(null)
    showToast.info("Reactivation cancelled. Your account remains deactivated.")
  }

  // Email validation
  const validateEmail = () => {
    if (!email) return null
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email.trim())
  }

  const isEmailValid = validateEmail()

  const handleGoogleSignIn = async () => {
    if (isSubmitting || isGoogleSigningIn) return
    
    setIsGoogleSigningIn(true)
    setInlineError("")
    
    try {
      const result = await signInWithGoogle()
      
      if (result.success) {
        showToast.success(result.message || "Login successful!")
        
        // Navigate to intended page or dashboard
        const from = location.state?.from?.pathname || "/dashboard"
        navigate(from, { replace: true })
      } else if (result.needsSignup) {
        // Account not found - redirect to signup
        showToast.info("Please complete your registration to continue.")
        navigate('/signup?google=true', { replace: true })
      } else {
        setInlineError(result.message || "Google sign-in failed. Please try again.")
        showToast.error(result.message || "Google sign-in failed")
      }
    } catch (error) {
      console.error("Google sign-in error:", error)
      setInlineError("An unexpected error occurred. Please try again.")
      showToast.error("An unexpected error occurred. Please try again.")
    } finally {
      setIsGoogleSigningIn(false)
    }
  }


  // Show loading spinner if checking authentication
  if (loading) {
    return (
      <div className="medichain-container">
        <LoadingSpinner 
          fullScreen={true} 
          text="Authenticating..." 
          size="large"
        />
      </div>
    )
  }

  return (
    <div className={`medichain-container ${(((searchParams.get('theme') || '').toLowerCase()) === 'modern') ? 'theme-modern' : 'theme-classic'}`}>
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
        <div className="login-container">
          {/* Login Form */}
          <div className="login-form">
            <div className="form-content">
              <div className="form-header">
                <h2>Welcome Back!</h2>
                <p>Sign in to your MediChain account</p>
              </div>

              {showVerificationPrompt && (
                <div className="verification-prompt" role="alert" aria-live="polite">
                  <div className="verification-icon" aria-hidden="true">
                    <AlertCircle size={20} color="#f59e0b" />
                  </div>
                  <div className="verification-content">
                    <p>Email verification required</p>
                    <p className="verification-text">
                      Please check your email and click the verification link before logging in.
                    </p>
                    <button 
                      type="button" 
                      className="resend-btn"
                      onClick={handleResendVerification}
                      disabled={isResendingVerification}
                    >
                      {isResendingVerification ? (
                        <LoadingSpinner size="small" text="" />
                      ) : (
                        "Resend verification email"
                      )}
                    </button>
                  </div>
                </div>
              )}

              {inlineError && (
                <div className="form-alert error" role="alert" aria-live="assertive">
                  <p>{inlineError}</p>
                </div>
              )}

              <form onSubmit={handleSubmit} className="login-form-wrapper">
                <div className="input-group">
                  <label htmlFor="email">Email or Username</label>
                  <div className="input-wrapper">
                    <Mail className="input-icon" size={20} />
                    <input
                      id="email"
                      name="email"
                      type="text"
                      autoComplete="username"
                      aria-required="true"
                      aria-invalid={inlineError ? true : false}
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      onFocus={() => setEmailFocused(true)}
                      onBlur={() => setEmailFocused(false)}
                      placeholder="Enter your email or username"
                      disabled={isSubmitting}
                    />
                    {emailFocused && email && email.includes('@') && (
                      <span className="validation-icon">
                        {isEmailValid ? (
                          <Check size={16} className="validation-check" />
                        ) : (
                          <X size={16} className="validation-error" />
                        )}
                      </span>
                    )}
                  </div>
                  {emailFocused && email && email.includes('@') && isEmailValid === false && (
                    <small className="validation-message error">
                      Please enter a valid email address
                    </small>
                  )}
                </div>

                <div className="input-group">
                  <label htmlFor="password">Password</label>
                  <div className="input-wrapper">
                    <Lock className="input-icon" size={20} />
                    <input
                      id="password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      autoComplete="current-password"
                      aria-required="true"
                      aria-invalid={inlineError ? true : false}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Enter your password"
                      disabled={isSubmitting}
                    />
                    <button
                      type="button"
                      className="password-toggle"
                      onClick={() => setShowPassword(!showPassword)}
                      aria-label={showPassword ? "Hide password" : "Show password"}
                      tabIndex={-1}
                    >
                      {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                    </button>
                  </div>
                </div>

                <div className="form-options">
                  <div className="remember-me">
                    <input
                      type="checkbox"
                      id="remember"
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                      disabled={isSubmitting}
                    />
                    <label htmlFor="remember">Remember me</label>
                  </div>
                  <button
                    type="button"
                    className="forgot-password"
                    onClick={() => navigate("/reset-password")}
                    aria-label="Forgot Password"
                  >
                    Forgot Password?
                  </button>
                </div>

                <button 
                  type="submit" 
                  className="login-btn"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <LoadingSpinner 
                      size="small" 
                      text="Logging in..." 
                    />
                  ) : (
                    <>
                      Log In
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
                  onClick={handleGoogleSignIn}
                  disabled={isSubmitting || isGoogleSigningIn}
                >
                  {isGoogleSigningIn ? (
                    <LoadingSpinner size="small" text="" />
                  ) : (
                    <>
                      <div className="google-icon">G</div>
                      Continue with Google
                    </>
                  )}
                </button>

                <p className="signup-link">
                  Don't have an account? <span 
                    onClick={handleSignUpClick} 
                    className="signup-link-text"
                    style={{ cursor: 'pointer' }}
                  >
                    Sign Up
                  </span>
                </p>
              </form>
            </div>
          </div>

          {/* Doctor Image Section */}
          <div className="doctor-image">
            <div className="doctor-placeholder">
              <div className="doctor-icon">
                <Plus size={48} />
              </div>
              <h3>Healthcare Professional</h3>
              <p>
                Securely access AI-generated diagnoses, prescriptions, and encrypted health records stored on the blockchain.
              </p>
              <div className="login-feature-list">
                <div className="login-feature-item">
                  <Plus size={16} />
                  <span>AI-Powered Diagnostics</span>
                </div>
                <div className="login-feature-item">
                  <Plus size={16} />
                  <span>Blockchain Security</span>
                </div>
                <div className="login-feature-item">
                  <Plus size={16} />
                  <span>End-to-End Encryption</span>
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

      {/* Role Selection Modal */}
      <RoleSelectionModal 
        isOpen={isRoleModalOpen}
        onClose={closeRoleModal}
        onRoleSelect={handleRoleSelect}
      />

      {/* Reactivation Confirmation Modal */}
      {showReactivationModal && (
        <div className="profile-modal-overlay" onClick={handleCancelReactivation}>
          <div className="profile-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="profile-modal-header">
              <AlertCircle size={48} className="profile-modal-icon-warning" />
              <h2>Reactivate Your Doctor Account</h2>
              <p>Your account is currently deactivated. Would you like to reactivate it?</p>
            </div>

            <div className="profile-modal-body">
              <div className="profile-modal-warning-box">
                <div>
                  <p className="profile-modal-warning-title">Account Reactivation</p>
                  <p className="profile-modal-warning-text">
                    By reactivating your account, you will:
                  </p>
                  <ul className="profile-modal-warning-list">
                    <li>Regain full access to your doctor dashboard</li>
                    <li>Be able to manage patient records</li>
                    <li>Continue providing medical services</li>
                    <li>Access all your professional data</li>
                  </ul>
                  <p className="profile-modal-warning-text" style={{ marginTop: '15px' }}>
                    Your profile has remained visible to patients during deactivation.
                  </p>
                </div>
              </div>
            </div>

            <div className="profile-modal-footer">
              <button 
                onClick={handleCancelReactivation}
                className="profile-btn profile-btn-secondary"
                disabled={isReactivating}
              >
                Cancel
              </button>
              <button 
                onClick={handleReactivateAccount}
                className="profile-btn profile-btn-success"
                disabled={isReactivating}
              >
                {isReactivating ? 'Reactivating...' : 'Yes, Reactivate My Account'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default MedichainLogin

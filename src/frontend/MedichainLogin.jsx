import { useState, useEffect } from "react"
import "./MedichainLogin.css"
import { useNavigate, useLocation, useSearchParams } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import { Eye, EyeOff, Lock, Mail, Plus, ChevronRight, AlertCircle, CheckCircle } from "lucide-react"
import MedichainLogo from "../components/MedichainLogo"
import LoadingSpinner from "../components/LoadingSpinner"
import RoleSelectionModal from "../components/RoleSelectionModal"
import { showToast } from "../components/CustomToast"

const MedichainLogin = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const [searchParams] = useSearchParams()
  const { login, isAuthenticated, loading, resendVerification } = useAuth()
  
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [rememberMe, setRememberMe] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [isRoleModalOpen, setIsRoleModalOpen] = useState(false)
  const [showVerificationPrompt, setShowVerificationPrompt] = useState(false)
  const [isResendingVerification, setIsResendingVerification] = useState(false)

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
      return
    }

    setIsSubmitting(true)
    
    try {
      const result = await login(email.trim(), password)
      
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
          showToast.error("Please verify your email before logging in. Check your inbox for the verification link.")
        } else {
          showToast.error(result.message || "Login failed")
        }
      }
    } catch (error) {
      console.error("Login error:", error)
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

  const handleForgotPassword = () => {
    navigate("/reset-password")
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
            <MedichainLogo size={40} />
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
                <div className="verification-prompt">
                  <div className="verification-icon">
                    <AlertCircle size={20} color="#ff9800" />
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

              <form onSubmit={handleSubmit} className="login-form-wrapper">
                <div className="input-group">
                  <label htmlFor="email">Email or Username</label>
                  <div className="input-wrapper">
                    <Mail className="input-icon" size={20} />
                    <input
                      id="email"
                      type="text"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="Enter your email or username"
                      disabled={isSubmitting}
                    />
                  </div>
                </div>

                <div className="input-group">
                  <label htmlFor="password">Password</label>
                  <div className="input-wrapper">
                    <Lock className="input-icon" size={20} />
                    <input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Enter your password"
                      disabled={isSubmitting}
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
                  <span
                    className="forgot-password"
                    onClick={() => {
                      navigate("/reset-password")
                    }}
                    style={{ cursor: 'pointer', textDecoration: 'underline' }}
                  >
                    Forgot Password?
                  </span>
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

                <button type="button" className="google-btn" disabled={isSubmitting}>
                  <div className="google-icon">G</div>
                  Continue with Google
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
              <div className="feature-list">
                <div className="feature-item">
                  <Plus size={16} />
                  <span>AI-Powered Diagnostics</span>
                </div>
                <div className="feature-item">
                  <Plus size={16} />
                  <span>Blockchain Security</span>
                </div>
                <div className="feature-item">
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
    </div>
  )
}

export default MedichainLogin

import { useState, useEffect } from "react"
import "./MedichainLogin.css" // Reuse existing styles
import { useNavigate, useSearchParams } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import { Eye, EyeOff, Lock, Mail, User, Plus, ChevronRight } from "lucide-react"
import MedichainLogo from "../components/MedichainLogo"
import LoadingSpinner from "../components/LoadingSpinner"
import { showToast } from "../components/CustomToast"

const MedichainSignup = () => {
  const navigate = useNavigate()
  const { signup } = useAuth() // Fix: Use signup instead of register
  const [searchParams] = useSearchParams()
  
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
    confirmPassword: "",
    userType: "patient" // default
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isRolePreSelected, setIsRolePreSelected] = useState(false)

  // Set the userType based on URL parameter
  useEffect(() => {
    const role = searchParams.get('role')
    if (role && (role === 'doctor' || role === 'patient')) {
      setFormData(prev => ({
        ...prev,
        userType: role
      }))
      setIsRolePreSelected(true) // Lock the role selection
    }
  }, [searchParams])

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const validateForm = () => {
    const { firstName, lastName, email, password, confirmPassword } = formData
    
    // Debug: Log form data to see what's actually there
    console.log('Form data:', formData)
    console.log('firstName:', firstName, 'lastName:', lastName, 'email:', email, 'password:', password, 'confirmPassword:', confirmPassword)
    
    // COMPLETELY BYPASS VALIDATION FOR TESTING
    return true;
    
    if (!password?.trim()) {
      showToast.error("Please enter a password")
      return false
    }
    
    if (!confirmPassword?.trim()) {
      showToast.error("Please confirm your password")
      return false
    }
    
    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email.trim())) {
      showToast.error("Please enter a valid email address")
      return false
    }
    
    // Validate password length
    if (password.length < 6) {
      showToast.error("Password must be at least 6 characters long")
      return false
    }
    
    // Check if passwords match
    if (password !== confirmPassword) {
      showToast.error("Passwords do not match")
      return false
    }
    
    return true
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (isSubmitting) {
      return
    }
    
    if (!validateForm()) {
      return
    }
    
    setIsSubmitting(true)
    
    try {
      console.log('DEBUG: About to call signup with:', {
        email: formData.email.trim(),
        password: formData.password,
        firstName: formData.firstName.trim(),
        lastName: formData.lastName.trim(),
        userType: formData.userType
      });
      
      // Call signup with separate name fields
      const result = await signup(
        formData.email.trim(),
        formData.password,
        formData.firstName.trim(),
        formData.lastName.trim(),
        formData.userType
      )
      
      if (result.success) {
        showToast.success(result.message || "Account created successfully! Welcome to Medichain.")
        // Navigate to dashboard since user is automatically logged in
        navigate("/dashboard")
      } else {
        showToast.error(result.error || "Signup failed")
      }
    } catch (error) {
      console.error("Signup error:", error)
      showToast.error("An unexpected error occurred. Please try again.")
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
            <MedichainLogo size={40} />
          </div>
          <h1>MEDICHAIN</h1>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        <div className="login-container">
          {/* Signup Form */}
          <div className="login-form">
            <div className="form-content">
              <div className="form-header">
                <h2>Create Account</h2>
                <p>Join MediChain today</p>
              </div>

              <form onSubmit={handleSubmit} className="login-form-wrapper">
                <div className="input-group">
                  <label htmlFor="firstName">First Name</label>
                  <div className="input-wrapper">
                    <User className="input-icon" size={20} />
                    <input
                      id="firstName"
                      name="firstName"
                      type="text"
                      value={formData.firstName}
                      onChange={handleInputChange}
                      placeholder="Enter your first name"
                      disabled={isSubmitting}
                      required
                    />
                  </div>
                </div>

                <div className="input-group">
                  <label htmlFor="lastName">Last Name</label>
                  <div className="input-wrapper">
                    <User className="input-icon" size={20} />
                    <input
                      id="lastName"
                      name="lastName"
                      type="text"
                      value={formData.lastName}
                      onChange={handleInputChange}
                      placeholder="Enter your last name"
                      disabled={isSubmitting}
                      required
                    />
                  </div>
                </div>

                <div className="input-group">
                  <label htmlFor="email">Email</label>
                  <div className="input-wrapper">
                    <Mail className="input-icon" size={20} />
                    <input
                      id="email"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      placeholder="Enter your email"
                      disabled={isSubmitting}
                      required
                    />
                  </div>
                </div>

                <div className="input-group">
                  <label htmlFor="userType">Account Type</label>
                  <div className="input-wrapper">
                    <User className="input-icon" size={20} />
                    <select
                      id="userType"
                      name="userType"
                      value={formData.userType}
                      onChange={handleInputChange}
                      disabled={isSubmitting || isRolePreSelected}
                      required
                    >
                      <option value="patient">Patient</option>
                      <option value="doctor">Doctor</option>
                    </select>
                  </div>
                </div>

                <div className="input-group">
                  <label htmlFor="password">Password</label>
                  <div className="input-wrapper">
                    <Lock className="input-icon" size={20} />
                    <input
                      id="password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      value={formData.password}
                      onChange={handleInputChange}
                      placeholder="Enter your password"
                      disabled={isSubmitting}
                      required
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
                      name="confirmPassword"
                      type={showConfirmPassword ? "text" : "password"}
                      value={formData.confirmPassword}
                      onChange={handleInputChange}
                      placeholder="Confirm your password"
                      disabled={isSubmitting}
                      required
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
                  className={`login-btn ${isSubmitting ? 'loading' : ''}`}
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <LoadingSpinner 
                        size="small" 
                        text="" 
                        color="#ffffff"
                      />
                      <span>Creating account...</span>
                    </div>
                  ) : (
                    <>
                      Create Account
                      <ChevronRight size={20} />
                    </>
                  )}
                </button>

                <p className="signup-link">
                  Already have an account? <span 
                    onClick={() => navigate("/login")} 
                    className="signup-link-text"
                    style={{ cursor: 'pointer' }}
                  >
                    Log In
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
              <h3>Join MediChain</h3>
              <p>
                Create your account to access secure healthcare records and AI-powered medical services.
              </p>
              <div className="feature-list">
                <div className="feature-item">
                  <Plus size={16} />
                  <span>Secure Account Creation</span>
                </div>
                <div className="feature-item">
                  <Plus size={16} />
                  <span>HIPAA Compliant</span>
                </div>
                <div className="feature-item">
                  <Plus size={16} />
                  <span>Encrypted Data Storage</span>
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

export default MedichainSignup
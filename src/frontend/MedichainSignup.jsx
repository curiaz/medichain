import { useState, useEffect } from "react"
import "./MedichainLogin.css" // Reuse existing styles
import { useNavigate, useSearchParams } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import { Eye, EyeOff, Lock, Mail, User, Plus, ChevronRight, Upload } from "lucide-react"
import LoadingSpinner from "../components/LoadingSpinner"
import { showToast } from "../components/CustomToast"
import medichainLogo from "../assets/medichain_logo.png"

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
    userType: "patient", // default
    specialization: "", // for doctors
    verificationFile: null // for doctor verification
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
    const { name, value, files } = e.target
    if (name === 'verificationFile') {
      setFormData(prev => ({
        ...prev,
        [name]: files[0] || null
      }))
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }))
    }
  }

  const validateForm = () => {
    const { firstName, lastName, email, password, confirmPassword, userType, specialization, verificationFile } = formData
    
    if (!firstName?.trim()) {
      showToast.error("Please enter your first name")
      return false
    }
    
    if (!lastName?.trim()) {
      showToast.error("Please enter your last name")
      return false
    }
    
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
    
    // Doctor-specific validation
    if (userType === 'doctor') {
      if (!specialization?.trim()) {
        showToast.error("Please enter your medical specialization")
        return false
      }
      
      if (!verificationFile) {
        showToast.error("Please upload your verification document (ID/Certificate)")
        return false
      }
      
      // Validate file type
      const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']
      if (!allowedTypes.includes(verificationFile.type)) {
        showToast.error("Please upload a valid file (PDF, JPG, or PNG)")
        return false
      }
      
      // Validate file size (max 5MB)
      if (verificationFile.size > 5 * 1024 * 1024) {
        showToast.error("File size must be less than 5MB")
        return false
      }
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
      // Doctor signup uses multipart/form-data to include verification file
      if (formData.userType === 'doctor') {
        const signupData = new FormData();
        signupData.append('email', formData.email.trim());
        signupData.append('password', formData.password);
        signupData.append('firstName', formData.firstName.trim());
        signupData.append('lastName', formData.lastName.trim());
        signupData.append('userType', formData.userType);
        signupData.append('specialization', formData.specialization.trim());
        signupData.append('verificationFile', formData.verificationFile);

        const response = await fetch('http://localhost:5000/api/auth/doctor-signup', {
          method: 'POST',
          body: signupData
        });

        const result = await response.json();

        if (result.success) {
          showToast.success(result.message || "Doctor account created successfully! Your documents are under review.");
          localStorage.setItem('medichain_token', result.data.token);
          localStorage.setItem('medichain_user', JSON.stringify(result.data.user));
          navigate("/dashboard");
        } else {
          showToast.error(result.error || "Doctor signup failed");
        }
      } else {
        const result = await signup(
          formData.email.trim(),
          formData.password,
          formData.firstName.trim(),
          formData.lastName.trim(),
          formData.userType
        );

        if (result.success) {
          showToast.success(result.message || "Account created successfully! Welcome to MediChain.");
          navigate("/dashboard");
        } else {
          showToast.error(result.error || "Signup failed");
        }
      }
    } catch (error) {
      console.error("Signup error:", error);
      showToast.error("An unexpected error occurred. Please try again.");
    } finally {
      setIsSubmitting(false);
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
            <img src={medichainLogo} alt="MediChain Logo" width={40} height={40} />
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

                {/* Doctor-specific fields */}
                {formData.userType === 'doctor' && (
                  <>
                    <div className="input-group">
                      <label htmlFor="specialization">Medical Specialization</label>
                      <div className="input-wrapper">
                        <User className="input-icon" size={20} />
                        <input
                          id="specialization"
                          name="specialization"
                          type="text"
                          value={formData.specialization}
                          onChange={handleInputChange}
                          placeholder="e.g., Cardiology, Pediatrics, Internal Medicine"
                          disabled={isSubmitting}
                          required
                        />
                      </div>
                    </div>

                    <div className="input-group">
                      <label htmlFor="verificationFile">Verification Document</label>
                      <div className="input-wrapper file-upload-wrapper">
                        <input
                          id="verificationFile"
                          name="verificationFile"
                          type="file"
                          onChange={handleInputChange}
                          accept=".pdf,.jpg,.jpeg,.png"
                          disabled={isSubmitting}
                          required
                          style={{ display: 'none' }}
                        />
                        <label htmlFor="verificationFile" className="file-upload-label">
                          <Upload size={16} />
                          {formData.verificationFile ? formData.verificationFile.name : 'Upload ID/Certificate (PDF, JPG, PNG)'}
                        </label>
                      </div>
                      <small className="file-help-text">
                        Upload your medical license, ID, or certification document (Max 5MB)
                      </small>
                    </div>
                  </>
                )}

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

          <div className="doctor-image">
            <div className="doctor-placeholder">
              <div className="doctor-icon">
                <Plus size={48} />
              </div>
              <h3>Join MediChain</h3>
              <p>
                Create your account to access secure healthcare records and AI-powered medical services.
              </p>
              <div className="login-feature-list">
                <div className="login-feature-item">
                  <Plus size={16} />
                  <span>Secure Account Creation</span>
                </div>
                <div className="login-feature-item">
                  <Plus size={16} />
                  <span>HIPAA Compliant</span>
                </div>
                <div className="login-feature-item">
                  <Plus size={16} />
                  <span>Encrypted Data Storage</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

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
  );
}

export default MedichainSignup;
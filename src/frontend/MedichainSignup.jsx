import { useState, useEffect } from "react"
import "./MedichainLogin.css" // Reuse existing styles
import { useNavigate, useSearchParams } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import { Eye, EyeOff, Lock, Mail, User, Plus, ChevronRight, Upload, Stethoscope, Heart } from "lucide-react"
import LoadingSpinner from "../components/LoadingSpinner"
import { showToast } from "../components/CustomToast"
import medichainLogo from "../assets/medichain_logo.png"
// eslint-disable-next-line no-unused-vars
import axios from "axios"

const MedichainSignup = () => {
  const navigate = useNavigate()
  const { signup, signInWithGoogle } = useAuth() // Fix: Use signup instead of register
  const [searchParams] = useSearchParams()
  const API_URL = 'https://medichainn.onrender.com/api'
  
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
    confirmPassword: "",
    userType: "patient", // default
    specialization: "General Practitioner", // Fixed to General Practitioner for doctors
    verificationFile: null // for doctor verification
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isRolePreSelected, setIsRolePreSelected] = useState(false)
  const [inlineError, setInlineError] = useState("")
  const [inlineSuccess, setInlineSuccess] = useState("")
  const [isGoogleSignup, setIsGoogleSignup] = useState(false)
  const [googleIdToken, setGoogleIdToken] = useState(null)
  const [isGoogleSigningIn, setIsGoogleSigningIn] = useState(false)

  // Set the userType based on URL parameter
  useEffect(() => {
    const role = searchParams.get('role')
    const isGoogleSignupParam = searchParams.get('google') === 'true'
    
    if (role && (role === 'doctor' || role === 'patient')) {
      setFormData(prev => ({
        ...prev,
        userType: role,
        specialization: role === 'doctor' ? "General Practitioner" : prev.specialization
      }))
      setIsRolePreSelected(true) // Lock the role selection
    }
    
    // Pre-fill Google signup data if available
    if (isGoogleSignupParam) {
      const googleData = sessionStorage.getItem('google_signup_data')
      if (googleData) {
        try {
          const data = JSON.parse(googleData)
          setIsGoogleSignup(true)
          setGoogleIdToken(data.idToken)
          setFormData(prev => ({
            ...prev,
            email: data.email || prev.email,
            firstName: data.firstName || prev.firstName,
            lastName: data.lastName || prev.lastName
          }))
          showToast.info("Please complete your registration to finish setting up your account.")
        } catch (error) {
          console.error('Error parsing Google signup data:', error)
        }
      }
    }
  }, [searchParams])
  
  // Ensure specialization is set when userType changes to doctor
  useEffect(() => {
    if (formData.userType === 'doctor') {
      setFormData(prev => ({
        ...prev,
        specialization: "General Practitioner"
      }))
    }
  }, [formData.userType])

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
    const { firstName, lastName, email, password, confirmPassword, userType, verificationFile } = formData
    
    if (!firstName?.trim()) {
      showToast.error("Please enter your first name")
      return false
    }
    
    if (!lastName?.trim()) {
      showToast.error("Please enter your last name")
      return false
    }
    
    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email.trim())) {
      showToast.error("Please enter a valid email address")
      return false
    }
    
    // Password validation - always required
    if (!password?.trim()) {
      showToast.error("Please enter a password")
      return false
    }
    
    if (!confirmPassword?.trim()) {
      showToast.error("Please confirm your password")
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
      // Specialization is automatically set to "General Practitioner"
      // No need to validate it anymore
      
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
      setInlineError("Please review the highlighted fields and try again.")
      return
    }
    
    setIsSubmitting(true)
    
    try {
      setInlineError("")
      setInlineSuccess("")
      
      // Handle Google signup (uses id_token instead of password)
      if (isGoogleSignup && googleIdToken) {
        console.log('[Signup] Completing Google signup with id_token...')
        
        // For Google signup, use the stored id_token to register
        const name = `${formData.firstName.trim()} ${formData.lastName.trim()}`.trim()
        
        // Doctor signup with Google
        if (formData.userType === 'doctor') {
          // For doctors, we need to upload the verification file
          const signupData = new FormData();
          signupData.append('id_token', googleIdToken);
          signupData.append('name', name);
          signupData.append('role', formData.userType);
          signupData.append('specialization', 'General Practitioner');
          signupData.append('password', formData.password); // Include password for Google signup
          signupData.append('verificationFile', formData.verificationFile);

          const response = await fetch(`${API_URL}/auth/doctor-signup`, {
            method: 'POST',
            body: signupData
          });

          const result = await response.json();

          if (result.success) {
            setInlineSuccess("Doctor account created successfully. Your documents are under review.")
            showToast.success(result.message || "Doctor account created successfully! Your documents are under review.");
            localStorage.setItem('medichain_token', result.data.token);
            localStorage.setItem('medichain_user', JSON.stringify(result.data.user));
            sessionStorage.removeItem('google_signup_data');
            // Redirect to dashboard after successful account creation
            navigate("/dashboard", { replace: true });
            return;
          } else {
            setInlineError(result.error || "Doctor signup failed. Please try again.")
            showToast.error(result.error || "Doctor signup failed");
          }
        } else {
          // Patient signup with Google - call register endpoint directly to use form data
          try {
            const response = await axios.post(`${API_URL}/auth/register`, {
              id_token: googleIdToken,
              name: name,
              role: formData.userType,
              password: formData.password // Include password for Google signup
            });

            if (response.data.success) {
              const userData = response.data.data?.user || response.data.user;
              const token = response.data.data?.token || googleIdToken;
              
              localStorage.setItem('medichain_token', token);
              localStorage.setItem('medichain_user', JSON.stringify(userData));
              sessionStorage.removeItem('google_signup_data');
              
              setInlineSuccess("Account created successfully! Welcome to MediChain.")
              showToast.success("Account created successfully! Welcome to MediChain.");
              // Set flag for welcome popup (patient only)
              if (formData.userType === 'patient') {
                sessionStorage.setItem('medichain_just_signed_up', 'true');
              }
              // Redirect to dashboard after successful account creation
              navigate("/dashboard", { replace: true });
              return;
            } else {
              setInlineError(response.data.error || "Signup failed. Please try again.")
              showToast.error(response.data.error || "Signup failed");
            }
          } catch (error) {
            console.error("Patient signup with Google error:", error);
            const errorMsg = error.response?.data?.error || error.message || "Signup failed. Please try again.";
            setInlineError(errorMsg);
            showToast.error(errorMsg);
          }
        }
        return
      }
      
      // Regular signup (email/password)
      // Doctor signup uses multipart/form-data to include verification file
      if (formData.userType === 'doctor') {
        const signupData = new FormData();
        signupData.append('email', formData.email.trim());
        signupData.append('password', formData.password);
        signupData.append('firstName', formData.firstName.trim());
        signupData.append('lastName', formData.lastName.trim());
        signupData.append('userType', formData.userType);
        signupData.append('specialization', 'General Practitioner'); // Always set to General Practitioner
        signupData.append('verificationFile', formData.verificationFile);

        const response = await fetch(`${API_URL}/auth/doctor-signup`, {
          method: 'POST',
          body: signupData
        });

        const result = await response.json();

        if (result.success) {
          setInlineSuccess("Doctor account created successfully. Your documents are under review.")
          showToast.success(result.message || "Doctor account created successfully! Your documents are under review.");
          localStorage.setItem('medichain_token', result.data.token);
          localStorage.setItem('medichain_user', JSON.stringify(result.data.user));
          sessionStorage.removeItem('google_signup_data');
          // Redirect to dashboard after successful account creation
          navigate("/dashboard", { replace: true });
          return;
        } else {
          setInlineError(result.error || "Doctor signup failed. Please try again.")
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
          setInlineSuccess("Account created successfully! Welcome to MediChain.")
          showToast.success(result.message || "Account created successfully! Welcome to MediChain.");
          sessionStorage.removeItem('google_signup_data');
          // Set flag for welcome popup (patient only)
          if (formData.userType === 'patient') {
            sessionStorage.setItem('medichain_just_signed_up', 'true');
          }
          // Redirect to dashboard after successful account creation
          navigate("/dashboard", { replace: true });
          return;
        } else {
          setInlineError(result.error || "Signup failed. Please try again.")
          showToast.error(result.error || "Signup failed");
        }
      }
    } catch (error) {
      console.error("Signup error:", error);
      setInlineError("An unexpected error occurred. Please try again.")
      showToast.error("An unexpected error occurred. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }
  
  const handleGoogleSignIn = async () => {
    if (isSubmitting || isGoogleSigningIn) return
    
    setIsGoogleSigningIn(true)
    setInlineError("")
    
    try {
      const result = await signInWithGoogle()
      
      if (result.success) {
        showToast.success(result.message || "Login successful!")
        sessionStorage.removeItem('google_signup_data')
        navigate("/dashboard")
      } else if (result.needsSignup) {
        // Account not found - continue with signup
        showToast.info("Please complete your registration to continue.")
        setIsGoogleSignup(true)
        const googleData = sessionStorage.getItem('google_signup_data')
        if (googleData) {
          try {
            const data = JSON.parse(googleData)
            setGoogleIdToken(data.idToken)
            setFormData(prev => ({
              ...prev,
              email: data.email || prev.email,
              firstName: data.firstName || prev.firstName,
              lastName: data.lastName || prev.lastName
            }))
          } catch (error) {
            console.error('Error parsing Google signup data:', error)
          }
        }
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
          {/* Signup Form */}
          <div className="login-form">
            <div className="form-content">
              <div className="form-header">
                <h2>Create Account</h2>
                <p>Join MediChain today</p>
              </div>

              <form onSubmit={handleSubmit} className="login-form-wrapper" noValidate>
                {inlineError && (
                  <div className="form-alert error" role="alert" aria-live="assertive">
                    <p>{inlineError}</p>
                  </div>
                )}
                {inlineSuccess && (
                  <div className="form-alert success" role="status" aria-live="polite">
                    <p>{inlineSuccess}</p>
                  </div>
                )}
                <div className="input-group">
                  <label htmlFor="firstName">First Name</label>
                  <div className="input-wrapper">
                    <User className="input-icon" size={20} />
                    <input
                      id="firstName"
                      name="firstName"
                      type="text"
                      autoComplete="given-name"
                      aria-required="true"
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
                      autoComplete="family-name"
                      aria-required="true"
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
                      autoComplete="email"
                      aria-required="true"
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
                        <Stethoscope className="input-icon" size={20} />
                        <input
                          id="specialization"
                          name="specialization"
                          type="text"
                          aria-required={formData.userType === 'doctor'}
                          value="General Practitioner"
                          readOnly
                          disabled={true}
                          style={{ cursor: 'not-allowed', backgroundColor: '#f5f5f5' }}
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
                          aria-required={formData.userType === 'doctor'}
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

                {/* Password fields - always required */}
                <div className="input-group">
                  <label htmlFor="password">Password</label>
                  <div className="input-wrapper">
                    <Lock className="input-icon" size={20} />
                    <input
                      id="password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      autoComplete="new-password"
                      aria-required="true"
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
                      aria-label={showPassword ? "Hide password" : "Show password"}
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
                      autoComplete="new-password"
                      aria-required="true"
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
                      aria-label={showConfirmPassword ? "Hide password" : "Show password"}
                      tabIndex={-1}
                    >
                      {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                    </button>
                  </div>
                </div>
                
                {isGoogleSignup && (
                  <div className="form-alert info" role="status" aria-live="polite" style={{ backgroundColor: '#e0f2fe', color: '#0369a1', border: '1px solid #bae6fd' }}>
                    <p>You're signing up with Google. Please set a password for your account.</p>
                  </div>
                )}

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
                {formData.userType === 'doctor' ? (
                  <Stethoscope size={48} />
                ) : (
                  <Heart size={48} />
                )}
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
                  <span>AI Driven Diagnosis</span>
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

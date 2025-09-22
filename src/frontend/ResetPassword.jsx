import { useState } from "react"
import "./ResetPassword.css"
import { useNavigate } from "react-router-dom"
import { Mail, ChevronLeft } from "lucide-react"
import MedichainLogo from "../components/MedichainLogo"
import LoadingSpinner from "../components/LoadingSpinner"
import { showToast } from "../components/CustomToast"

const ResetPassword = () => {
  const navigate = useNavigate()
  const [email, setEmail] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e) => {
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
      // Simulate password reset API call
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      showToast.success("Password reset instructions have been sent to your email!")
      setTimeout(() => {
        navigate("/login")
      }, 2000)
    } catch (error) {
      showToast.error("Failed to send reset email. Please try again.")
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
            <div className="form-header">
              <h2>Reset Password</h2>
              <p>Enter your email address and we'll send you instructions to reset your password</p>
            </div>

            <form onSubmit={handleSubmit} className="reset-form-wrapper">
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
                    text="Sending..." 
                  />
                ) : (
                  "Send Reset Instructions"
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
          </div>

          {/* Info Section */}
          <div className="info-section">
            <div className="info-content">
              <h3>Password Reset</h3>
              <p>
                We'll send you an email with instructions to reset your password. 
                Make sure to check your spam folder if you don't see it in your inbox.
              </p>
              <div className="info-list">
                <div className="info-item">
                  <span>✓</span>
                  <span>Check your email inbox</span>
                </div>
                <div className="info-item">
                  <span>✓</span>
                  <span>Follow the reset link</span>
                </div>
                <div className="info-item">
                  <span>✓</span>
                  <span>Create new password</span>
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

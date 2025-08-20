import { useState, useEffect } from "react"
import "./MedichainLogin.css"
import { useNavigate, useLocation } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import { Eye, EyeOff, Lock, Mail, Plus, ChevronRight } from "lucide-react"
import MedichainLogo from "../components/MedichainLogo"
import LoadingSpinner from "../components/LoadingSpinner"
import RoleSelectionModal from "../components/RoleSelectionModal"
import { showToast } from "../components/CustomToast"

const MedichainLogin = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { login, isAuthenticated, loading } = useAuth()
  
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [rememberMe, setRememberMe] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [isRoleModalOpen, setIsRoleModalOpen] = useState(false)

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
    if (isAuthenticated) {
      const from = location.state?.from?.pathname || "/dashboard"
      navigate(from, { replace: true })
    }
  }, [isAuthenticated, navigate, location])

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!email.trim() || !password.trim()) {
      showToast.error("Please fill in all fields")
      return
    }

    setIsSubmitting(true)

    try {
      const result = await login(email.trim(), password)
      
      if (result.success) {
        // Handle remember me
        if (rememberMe) {
          localStorage.setItem("medichain_remembered_email", email.trim())
          localStorage.setItem("medichain_remembered_password", password)
        } else {
          localStorage.removeItem("medichain_remembered_email")
          localStorage.removeItem("medichain_remembered_password")
        }

        showToast.success("Login successful! Welcome to Medichain.")
        
        // Redirect to intended page or dashboard
        const from = location.state?.from?.pathname || "/dashboard"
        navigate(from, { replace: true })
      } else {
        showToast.error(result.message || "Login failed")
      }
    } catch (error) {
      console.error("Login error:", error)
      showToast.error("An unexpected error occurred. Please try again.")
    } finally {
      setIsSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="min-h-screen flex bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Left side - Login Form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="max-w-md w-full space-y-8">
          {/* Logo and Header */}
          <div className="text-center">
            <MedichainLogo className="mx-auto h-16 w-auto" />
            <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
              Welcome back
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              Sign in to your account to continue
            </p>
          </div>

          {/* Login Form */}
          <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
            <div className="space-y-4">
              {/* Email Field */}
              <div>
                <label htmlFor="email" className="sr-only">
                  Email address
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Email address"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
              </div>

              {/* Password Field */}
              <div>
                <label htmlFor="password" className="sr-only">
                  Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    autoComplete="current-password"
                    required
                    className="block w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                    ) : (
                      <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Remember Me */}
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                />
                <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-900">
                  Remember me
                </label>
              </div>
            </div>

            {/* Submit Button */}
            <div>
              <button
                type="submit"
                disabled={isSubmitting}
                className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isSubmitting ? (
                  <LoadingSpinner size="sm" />
                ) : (
                  <>
                    Sign in
                    <ChevronRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </button>
            </div>

            {/* Sign Up Link */}
            <div className="text-center">
              <p className="text-sm text-gray-600">
                Don't have an account?{" "}
                <button
                  type="button"
                  onClick={handleSignUpClick}
                  className="font-medium text-blue-600 hover:text-blue-500 inline-flex items-center"
                >
                  Sign up
                  <Plus className="ml-1 h-4 w-4" />
                </button>
              </p>
            </div>
          </form>
        </div>
      </div>

      {/* Right side - Image */}
      <div className="hidden lg:flex lg:flex-1 relative">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600 to-indigo-700 opacity-10" />
        <img
          className="object-cover w-full h-full"
          src="/images/doctor-login.png"
          alt="Medical professional using technology"
        />
        <div className="absolute inset-0 bg-black bg-opacity-30" />
        <div className="absolute bottom-8 left-8 right-8 text-white">
          <h3 className="text-2xl font-bold mb-2">
            Secure Medical Records Management
          </h3>
          <p className="text-lg opacity-90">
            Access your medical data securely with blockchain technology
          </p>
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

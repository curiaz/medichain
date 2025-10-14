import React, { createContext, useContext, useState, useEffect } from 'react';
import { auth } from '../config/firebase';
import { 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  signInWithPopup,
  GoogleAuthProvider
} from 'firebase/auth';
import axios from 'axios';

// Create the authentication context
const AuthContext = createContext();

// API base URL - simple localhost for development
const API_URL = 'http://localhost:5000/api';

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check for existing authentication on mount
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        try {
          // Get ID token
          const idToken = await firebaseUser.getIdToken();
          
          // Verify with backend
          const response = await axios.post(`${API_URL}/auth/login`, {
            id_token: idToken
          });

          if (response.data.success) {
            localStorage.setItem('medichain_token', idToken);
            localStorage.setItem('medichain_user', JSON.stringify(response.data.user));
            
            setUser(response.data.user);
            setIsAuthenticated(true);
          } else {
            // Clear Firebase auth if backend verification fails
            await signOut(auth);
            localStorage.removeItem('medichain_token');
            localStorage.removeItem('medichain_user');
          }
        } catch (error) {
          console.error('Backend verification error:', error);
          // Clear Firebase auth if backend is unreachable
          await signOut(auth);
          localStorage.removeItem('medichain_token');
          localStorage.removeItem('medichain_user');
        }
      } else {
        // User is signed out
        localStorage.removeItem('medichain_token');
        localStorage.removeItem('medichain_user');
        setIsAuthenticated(false);
        setUser(null);
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  // Login function
  const login = async (email, password) => {
    setLoading(true);
    setError(null);

    try {
      // Attempt backend login first (Supabase-based authentication)
      const response = await axios.post(`${API_URL}/auth/login`, {
        email: email,
        password: password
      });

      if (response.data.success) {
        const token = response.data.data.token;
        const userData = response.data.data.user;
        
        localStorage.setItem('medichain_token', token);
        localStorage.setItem('medichain_user', JSON.stringify(userData));

        setUser(userData);
        setIsAuthenticated(true);

        return {
          success: true,
          message: 'Login successful',
          user: userData
        };
      } else {
        throw new Error(response.data.error || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      
      // Check if it's a network error
      if (error.code === 'ERR_NETWORK' || error.message.includes('Network Error')) {
        setError('Unable to connect to server. Please check if the backend is running.');
        return {
          success: false,
          message: 'Unable to connect to server. Please check if the backend is running.',
          requiresVerification: false
        };
      }
      
      // Check for email verification requirement
      if (error.response?.data?.error?.includes('verify') || error.response?.data?.error?.includes('verification')) {
        setError('Please verify your email before logging in.');
        return {
          success: false,
          message: error.response.data.error || 'Please verify your email before logging in.',
          requiresVerification: true
        };
      }
      
      setError(error.response?.data?.error || error.message || 'Login failed');
      return {
        success: false,
        message: error.response?.data?.error || error.message || 'Login failed',
        requiresVerification: false
      };
    } finally {
      setLoading(false);
    }
  };

  // Signup function
  const signup = async (email, password, firstName, lastName, userType) => {
    setLoading(true);
    setError(null);

    try {
      // Register with backend (with OTP verification)
      const response = await axios.post(`${API_URL}/auth/signup`, {
        email: email,
        password: password,
        name: `${firstName} ${lastName}`,
        role: userType
      });

      if (response.data.success) {
        // Check if email verification is required
        if (response.data.requires_verification) {
          return {
            success: true,
            requiresVerification: true,
            sessionToken: response.data.data.session_token,
            otpCode: response.data.data.otp_code, // Only in dev mode
            email: email,
            message: 'Please check your email for verification code'
          };
        }
        
        // Old flow (if verification not required)
        const token = response.data.data.token;
        const userData = response.data.data.user;
        
        localStorage.setItem('medichain_token', token);
        localStorage.setItem('medichain_user', JSON.stringify(userData));

        setUser(userData);
        setIsAuthenticated(true);

        return {
          success: true,
          message: 'Account created successfully!',
          user: userData
        };
      } else {
        throw new Error(response.data.error || 'Signup failed');
      }
    } catch (error) {
      console.error('Signup error:', error);
      const errorMessage = error.response?.data?.error || error.message || 'Signup failed';
      setError(errorMessage);
      return {
        success: false,
        error: errorMessage
      };
    } finally {
      setLoading(false);
    }
  };

  // Verify email with OTP
  const verifyEmail = async (sessionToken, otpCode) => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/auth/verify-email`, {
        session_token: sessionToken,
        otp_code: otpCode
      });

      if (response.data.success) {
        const token = response.data.data.token;
        const userData = response.data.data.user;
        
        localStorage.setItem('medichain_token', token);
        localStorage.setItem('medichain_user', JSON.stringify(userData));

        setUser(userData);
        setIsAuthenticated(true);

        return {
          success: true,
          message: 'Email verified successfully!',
          user: userData
        };
      } else {
        throw new Error(response.data.error || 'Verification failed');
      }
    } catch (error) {
      console.error('Verification error:', error);
      const errorMessage = error.response?.data?.error || error.message || 'Verification failed';
      setError(errorMessage);
      return {
        success: false,
        error: errorMessage
      };
    } finally {
      setLoading(false);
    }
  };

  // Resend verification code
  const resendVerification = async (email) => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/auth/resend-verification`, {
        email: email
      });

      if (response.data.success) {
        return {
          success: true,
          sessionToken: response.data.data.session_token,
          otpCode: response.data.data.otp_code, // Only in dev mode
          message: 'New verification code sent!'
        };
      } else {
        throw new Error(response.data.error || 'Failed to resend code');
      }
    } catch (error) {
      console.error('Resend verification error:', error);
      const errorMessage = error.response?.data?.error || error.message || 'Failed to resend code';
      setError(errorMessage);
      return {
        success: false,
        error: errorMessage
      };
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const logout = async () => {
    try {
      await signOut(auth);
      localStorage.removeItem('medichain_token');
      localStorage.removeItem('medichain_user');
      setIsAuthenticated(false);
      setUser(null);
      setError(null);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  // Update user function
  const updateUser = (updatedData) => {
    const updatedUser = { ...user, ...updatedData };
    setUser(updatedUser);
    localStorage.setItem('medichain_user', JSON.stringify(updatedUser));
  };

  // Check verification status function (for doctors)
  const checkVerificationStatus = async () => {
    if (!user || !isAuthenticated) return null;
    
    try {
      const token = localStorage.getItem('medichain_token');
      const response = await axios.get(`${API_URL}/auth/verify`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data.success && response.data.user) {
        const updatedUser = response.data.user;
        setUser(updatedUser);
        localStorage.setItem('medichain_user', JSON.stringify(updatedUser));
        return updatedUser;
      }
    } catch (error) {
      console.error('Error checking verification status:', error);
    }
    return null;
  };

  const clearError = () => {
    setError(null);
  };

  // Google Sign-In function
  const signInWithGoogle = async () => {
    setLoading(true);
    setError(null);

    try {
      const provider = new GoogleAuthProvider();
      provider.setCustomParameters({
        prompt: 'select_account'
      });

      // Sign in with popup
      const result = await signInWithPopup(auth, provider);
      const user = result.user;

      // Get ID token
      const idToken = await user.getIdToken();

      // Send to backend to create/update user profile
      const response = await axios.post(`${API_URL}/auth/google-signin`, {
        id_token: idToken,
        email: user.email,
        name: user.displayName || user.email.split('@')[0],
        photo_url: user.photoURL
      });

      if (response.data.success) {
        const token = response.data.data.token;
        const userData = response.data.data.user;

        localStorage.setItem('medichain_token', token);
        localStorage.setItem('medichain_user', JSON.stringify(userData));

        setUser(userData);
        setIsAuthenticated(true);

        return {
          success: true,
          message: 'Google sign-in successful',
          user: userData
        };
      } else {
        throw new Error(response.data.error || 'Google sign-in failed');
      }
    } catch (error) {
      console.error('Google sign-in error:', error);
      
      // Handle specific Firebase errors
      if (error.code === 'auth/popup-closed-by-user') {
        setError('Sign-in cancelled');
        return {
          success: false,
          message: 'Sign-in cancelled'
        };
      } else if (error.code === 'auth/popup-blocked') {
        setError('Pop-up blocked. Please allow pop-ups for this site.');
        return {
          success: false,
          message: 'Pop-up blocked. Please allow pop-ups for this site.'
        };
      }
      
      setError(error.response?.data?.error || error.message || 'Google sign-in failed');
      return {
        success: false,
        message: error.response?.data?.error || error.message || 'Google sign-in failed'
      };
    } finally {
      setLoading(false);
    }
  };

  // Refresh user data from backend
  const refreshUser = async () => {
    try {
      const token = localStorage.getItem('medichain_token');
      if (!token) {
        return { success: false, error: 'No token found' };
      }

      const response = await axios.get(`${API_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.data && response.data.success) {
        const userData = response.data.data;
        
        // Transform the data to match the expected format
        const transformedUser = {
          id: userData.id,
          uid: userData.firebase_uid,
          email: userData.email,
          role: userData.role,
          firebase_uid: userData.firebase_uid,
          profile: {
            first_name: userData.first_name,
            last_name: userData.last_name,
            role: userData.role,
            verification_status: userData.verification_status || 'pending'
          }
        };
        
        // Add doctor_profile if exists
        if (userData.doctor_profile) {
          transformedUser.doctor_profile = userData.doctor_profile;
          transformedUser.profile.verification_status = userData.doctor_profile.verification_status || 'pending';
        }
        
        localStorage.setItem('medichain_user', JSON.stringify(transformedUser));
        setUser(transformedUser);
        return { success: true, user: transformedUser };
      }
    } catch (error) {
      console.error('Error refreshing user:', error);
      return { success: false, error: error.message };
    }
  };

  const value = {
    isAuthenticated,
    user,
    loading,
    error,
    login,
    logout,
    signup,
    verifyEmail,
    resendVerification,
    updateUser,
    checkVerificationStatus,
    clearError,
    signInWithGoogle,
    refreshUser
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;

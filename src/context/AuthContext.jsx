import React, { createContext, useContext, useState, useEffect } from 'react';
import { auth } from '../config/firebase';
import { 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged
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
      // Create user with Firebase
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      
      // Get ID token
      const idToken = await userCredential.user.getIdToken();
      
      // Register with backend
      const response = await axios.post(`${API_URL}/auth/register`, {
        id_token: idToken,
        name: `${firstName} ${lastName}`,
        role: userType
      });

      if (response.data.success) {
        localStorage.setItem('medichain_token', idToken);
        localStorage.setItem('medichain_user', JSON.stringify(response.data.user));

        setUser(response.data.user);
        setIsAuthenticated(true);

        return {
          success: true,
          message: 'Account created successfully!',
          user: response.data.user
        };
      } else {
        throw new Error(response.data.error || 'Signup failed');
      }
    } catch (error) {
      setError(error.message || 'Signup failed');
      return {
        success: false,
        error: error.message || 'Signup failed'
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

  // Resend verification email
  const resendVerification = async (email) => {
    try {
      const response = await axios.post(`${API_URL}/auth/resend-verification`, {
        email: email
      });

      if (response.data.success) {
        return {
          success: true,
          message: 'Verification email sent successfully'
        };
      } else {
        return {
          success: false,
          error: response.data.error || 'Failed to send verification email'
        };
      }
    } catch (error) {
      console.error('Resend verification error:', error);
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to send verification email'
      };
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
    updateUser,
    checkVerificationStatus,
    clearError,
    resendVerification
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;

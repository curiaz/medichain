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

// API base URL - point to your Flask backend
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
      // Sign in with Firebase
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      
      // Get ID token
      const idToken = await userCredential.user.getIdToken();
      
      // Verify with backend
      const response = await axios.post(`${API_URL}/auth/login`, {
        id_token: idToken
      });

      if (response.data.success) {
        // Check if account requires reactivation
        if (response.data.requires_reactivation) {
          return {
            success: true,
            requiresReactivation: true,
            message: 'Account is deactivated',
            user: response.data.user,
            token: idToken
          };
        }

        localStorage.setItem('medichain_token', idToken);
        localStorage.setItem('medichain_user', JSON.stringify(response.data.user));

        setUser(response.data.user);
        setIsAuthenticated(true);

        return {
          success: true,
          message: 'Login successful',
          user: response.data.user
        };
      } else {
        throw new Error(response.data.error || 'Login failed');
      }
    } catch (error) {
      // Special handling for disabled user (deactivated doctor accounts)
      if (error.code === 'auth/user-disabled') {
        console.log('🔍 Detected disabled user, checking if deactivated doctor...');
        
        // Try to check if this is a deactivated doctor account
        try {
          // Use Firebase Admin SDK through backend to check user status
          const checkResponse = await axios.post(`${API_URL}/auth/check-deactivated`, {
            email: email
          });
          
          console.log('✅ Deactivation check response:', checkResponse.data);
          
          if (checkResponse.data.success && checkResponse.data.is_deactivated_doctor) {
            // This is a deactivated doctor - return reactivation required
            console.log('✅ This is a deactivated doctor - showing reactivation modal');
            // DO NOT set error - we want to show the modal, not an error message
            return {
              success: true,
              requiresReactivation: true,
              message: 'Account is deactivated',
              user: checkResponse.data.user,
              email: email,
              password: password // Store for reactivation
            };
          }
        } catch (checkError) {
          console.error('❌ Error checking deactivation status:', checkError);
        }
        
        // If not a deactivated doctor, show the disabled error
        console.log('⚠️ Not a deactivated doctor - showing disabled error');
        setError('This account has been disabled. Please contact support.');
        return {
          success: false,
          message: 'This account has been disabled. Please contact support.'
        };
      }
      
      setError(error.message || 'Login failed');
      return {
        success: false,
        message: error.message || 'Login failed'
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
      // Handle Firebase errors
      let errorMessage = error.message || 'Signup failed';
      
      if (error.code === 'auth/email-already-in-use') {
        errorMessage = 'This email is already registered. Please login instead or use a different email.';
      } else if (error.code === 'auth/weak-password') {
        errorMessage = 'Password is too weak. Please use a stronger password.';
      } else if (error.code === 'auth/invalid-email') {
        errorMessage = 'Invalid email address.';
      } else if (error.response?.data?.error) {
        errorMessage = error.response.data.error;
      }
      
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

  const clearError = () => {
    setError(null);
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
    clearError
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;

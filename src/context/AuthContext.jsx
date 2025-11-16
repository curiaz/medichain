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
          
          // 🔧 FIXED: Send id_token to unified login endpoint
          const response = await axios.post(`${API_URL}/auth/login`, {
            id_token: idToken
          });

          if (response.data.success) {
            // 🔧 FIXED: Handle unified response structure
            const userData = response.data.data.user;
            const token = response.data.data.token;
            
            localStorage.setItem('medichain_token', token);
            localStorage.setItem('medichain_user', JSON.stringify(userData));
            
            setUser(userData);
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

  // Helper function to get user-friendly error messages
  const getFirebaseErrorMessage = (errorCode) => {
    const errorMessages = {
      'auth/invalid-email': 'Invalid email address format.',
      'auth/user-disabled': 'This account has been disabled.',
      'auth/user-not-found': 'No account found with this email.',
      'auth/wrong-password': 'Incorrect password. Please try again.',
      'auth/invalid-credential': 'Invalid email or password.',
      'auth/too-many-requests': 'Too many failed login attempts. Please try again later.',
      'auth/network-request-failed': 'Network error. Please check your internet connection.',
      'auth/email-already-in-use': 'An account with this email already exists.',
      'auth/weak-password': 'Password should be at least 6 characters long.',
      'auth/operation-not-allowed': 'This operation is not allowed. Please contact support.',
      'auth/popup-closed-by-user': 'Sign-in popup was closed before completion.',
      'auth/cancelled-popup-request': 'Only one popup request is allowed at a time.',
    };
    
    return errorMessages[errorCode] || 'An error occurred. Please try again.';
  };

  // Login function
  const login = async (email, password) => {
    setLoading(true);
    setError(null);

    try {
      // Validate inputs
      if (!email || !email.trim()) {
        const error = 'Please enter your email address.';
        setError(error);
        return { success: false, message: error };
      }
      
      if (!password || !password.trim()) {
        const error = 'Please enter your password.';
        setError(error);
        return { success: false, message: error };
      }

<<<<<<< HEAD
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
=======
      // 🔧 FIXED: Try Firebase authentication first
      // This handles users who signed up via Firebase (normal or social)
      try {
        console.log('[Auth] Attempting Firebase login first...');
        const userCredential = await signInWithEmailAndPassword(auth, email.trim(), password);
        const idToken = await userCredential.user.getIdToken();
        
        console.log('[Auth] Firebase login successful, verifying with backend...');
        // Send Firebase token to backend
        const response = await axios.post(`${API_URL}/auth/login`, {
          id_token: idToken
        });
>>>>>>> 7315ad242322e8c1189b814eceb20520246b27b0

        if (response.data.success) {
          const userData = response.data.data.user;
          const token = response.data.data.token;
          
          localStorage.setItem('medichain_token', token);
          localStorage.setItem('medichain_user', JSON.stringify(userData));

          setUser(userData);
          setIsAuthenticated(true);

          console.log('[Auth] ✅ Login successful!');
          return {
            success: true,
            message: 'Login successful!',
            user: userData
          };
        } else {
          throw new Error(response.data.error || 'Backend verification failed');
        }
      } catch (firebaseError) {
        // Handle Firebase-specific errors
        if (firebaseError.code?.startsWith('auth/')) {
          const friendlyMessage = getFirebaseErrorMessage(firebaseError.code);
          console.log('[Auth] Firebase error:', firebaseError.code, '-', friendlyMessage);
          
          // If it's a user-not-found or wrong-password error, try backend auth as fallback
          if (firebaseError.code === 'auth/user-not-found' || 
              firebaseError.code === 'auth/wrong-password' ||
              firebaseError.code === 'auth/invalid-credential') {
            console.log('[Auth] Firebase login failed, trying Supabase auth...');
            
            try {
              const response = await axios.post(`${API_URL}/auth/login`, {
                email: email.trim(),
                password: password
              });

              if (response.data.success) {
                const token = response.data.data.token;
                const userData = response.data.data.user;
                
                localStorage.setItem('medichain_token', token);
                localStorage.setItem('medichain_user', JSON.stringify(userData));

                setUser(userData);
                setIsAuthenticated(true);

                console.log('[Auth] ✅ Supabase login successful!');
                return {
                  success: true,
                  message: 'Login successful!',
                  user: userData
                };
              } else {
                throw new Error(response.data.error || 'Invalid email or password');
              }
            } catch (backendError) {
              const errorMsg = backendError.response?.data?.error || friendlyMessage;
              setError(errorMsg);
              return {
                success: false,
                message: errorMsg,
                errorCode: firebaseError.code
              };
            }
          } else {
            // Other Firebase errors (network, too many requests, etc.)
            setError(friendlyMessage);
            return {
              success: false,
              message: friendlyMessage,
              errorCode: firebaseError.code
            };
          }
        } else {
          // Non-Firebase error (network, axios, etc.)
          throw firebaseError;
        }
      }
    } catch (error) {
<<<<<<< HEAD
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
=======
      console.error('[Auth] Login error:', error);
      
      // Network error
      if (error.code === 'ERR_NETWORK' || error.message.includes('Network Error')) {
        const errorMsg = 'Unable to connect to server. Please check your connection and try again.';
        setError(errorMsg);
        return {
          success: false,
          message: errorMsg,
          errorType: 'network'
        };
      }
      
      // Email verification error
      if (error.response?.data?.error?.includes('verify') || 
          error.response?.data?.error?.includes('verification')) {
        const errorMsg = error.response.data.error || 'Please verify your email before logging in.';
        setError(errorMsg);
        return {
          success: false,
          message: errorMsg,
          requiresVerification: true
        };
      }
      
      // Generic error
      const errorMsg = error.response?.data?.error || error.message || 'Login failed. Please try again.';
      setError(errorMsg);
>>>>>>> 7315ad242322e8c1189b814eceb20520246b27b0
      return {
        success: false,
        message: errorMsg
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
      // Validate inputs
      if (!email || !email.trim()) {
        const error = 'Please enter your email address.';
        setError(error);
        return { success: false, error };
      }
      
      if (!password || !password.trim()) {
        const error = 'Please enter a password.';
        setError(error);
        return { success: false, error };
      }
      
      if (password.length < 6) {
        const error = 'Password must be at least 6 characters long.';
        setError(error);
        return { success: false, error };
      }
      
      if (!firstName || !firstName.trim()) {
        const error = 'Please enter your first name.';
        setError(error);
        return { success: false, error };
      }
      
      if (!lastName || !lastName.trim()) {
        const error = 'Please enter your last name.';
        setError(error);
        return { success: false, error };
      }

      console.log('[Auth] Creating Firebase account...');
      
      // Create user with Firebase
      let userCredential;
      try {
        userCredential = await createUserWithEmailAndPassword(auth, email.trim(), password);
      } catch (firebaseError) {
        // Handle Firebase-specific signup errors
        if (firebaseError.code?.startsWith('auth/')) {
          const friendlyMessage = getFirebaseErrorMessage(firebaseError.code);
          console.error('[Auth] Firebase signup error:', firebaseError.code, '-', friendlyMessage);
          setError(friendlyMessage);
          return {
            success: false,
            error: friendlyMessage,
            errorCode: firebaseError.code
          };
        } else {
          throw firebaseError;
        }
      }
      
      console.log('[Auth] Firebase account created, getting ID token...');
      
      // Get ID token
      const idToken = await userCredential.user.getIdToken();
      
      console.log('[Auth] Registering with backend...');
      
      // 🔧 FIXED: Register with backend - now includes password for hash storage
      try {
        const response = await axios.post(`${API_URL}/auth/register`, {
          id_token: idToken,
          name: `${firstName.trim()} ${lastName.trim()}`,
          role: userType,
          password: password  // 🆕 Send password to be hashed and stored in DB
        });

        if (response.data.success) {
          // 🔧 FIXED: Handle unified response structure
          const userData = response.data.data.user;
          const token = response.data.data.token;
          
          localStorage.setItem('medichain_token', token);
          localStorage.setItem('medichain_user', JSON.stringify(userData));

          setUser(userData);
          setIsAuthenticated(true);

          console.log('[Auth] ✅ Signup successful!');
          return {
            success: true,
            message: 'Account created successfully! Welcome to MediChain.',
            user: userData
          };
        } else {
          // Backend registration failed - clean up Firebase user
          console.error('[Auth] Backend registration failed:', response.data.error);
          
          // Try to delete the Firebase user we just created
          try {
            await userCredential.user.delete();
            console.log('[Auth] Cleaned up Firebase user after backend failure');
          } catch (deleteError) {
            console.error('[Auth] Failed to cleanup Firebase user:', deleteError);
          }
          
          const errorMsg = response.data.error || 'Failed to create account. Please try again.';
          setError(errorMsg);
          return {
            success: false,
            error: errorMsg
          };
        }
      } catch (backendError) {
        // Backend request failed - clean up Firebase user
        console.error('[Auth] Backend request failed:', backendError);
        
        // Try to delete the Firebase user we just created
        try {
          await userCredential.user.delete();
          console.log('[Auth] Cleaned up Firebase user after backend error');
        } catch (deleteError) {
          console.error('[Auth] Failed to cleanup Firebase user:', deleteError);
        }
        
        const errorMsg = backendError.response?.data?.error || 
                        'Failed to register with server. Please try again.';
        setError(errorMsg);
        return {
          success: false,
          error: errorMsg
        };
      }
    } catch (error) {
<<<<<<< HEAD
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
=======
      console.error('[Auth] Signup error:', error);
      
      // Network error
      if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
        const errorMsg = 'Unable to connect to server. Please check your connection and try again.';
        setError(errorMsg);
        return {
          success: false,
          error: errorMsg,
          errorType: 'network'
        };
      }
      
      // Generic error
      const errorMsg = error.message || 'An error occurred during signup. Please try again.';
      setError(errorMsg);
      return {
        success: false,
        error: errorMsg
>>>>>>> 7315ad242322e8c1189b814eceb20520246b27b0
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

  // Helper function to get Firebase token
  const getFirebaseToken = async () => {
    try {
      // Wait for auth state to be ready
      return new Promise((resolve, reject) => {
        const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
          unsubscribe(); // Unsubscribe immediately after first callback
          if (firebaseUser) {
            try {
              const token = await firebaseUser.getIdToken(true); // Force refresh
              resolve(token);
            } catch (error) {
              console.error('[Auth] Error getting Firebase token:', error);
              reject(error);
            }
          } else {
            reject(new Error('No Firebase user found'));
          }
        });
        
        // Timeout after 2 seconds
        setTimeout(() => {
          unsubscribe();
          reject(new Error('Timeout waiting for Firebase auth state'));
        }, 2000);
      });
    } catch (error) {
      console.error('[Auth] Error in getFirebaseToken:', error);
      throw error;
    }
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
    resendVerification,
    getFirebaseToken // Add helper to get Firebase token
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;

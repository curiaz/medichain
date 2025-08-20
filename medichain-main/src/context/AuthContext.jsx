import React, { createContext, useContext, useState, useEffect } from 'react';
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
    const checkExistingAuth = async () => {
      try {
        const token = localStorage.getItem('medichain_token');
        if (!token) {
          setLoading(false);
          return;
        }

        // If token exists, verify with backend
        const response = await axios.get(`${API_URL}/auth/me`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

        if (response.data.success) {
          setUser(response.data.data.user);
          setIsAuthenticated(true);
        } else {
          // Clear invalid token
          localStorage.removeItem('medichain_token');
          localStorage.removeItem('medichain_user');
        }
      } catch (error) {
        console.error('Auth check error:', error);
        localStorage.removeItem('medichain_token');
        localStorage.removeItem('medichain_user');
      } finally {
        setLoading(false);
      }
    };

    checkExistingAuth();
  }, []);

  // Login function
  const login = async (email, password) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`${API_URL}/auth/login`, {
        email,
        password
      });
      
      if (response.data.success) {
        localStorage.setItem('medichain_token', response.data.data.token);
        localStorage.setItem('medichain_user', JSON.stringify(response.data.data.user));
        
        setUser(response.data.data.user);
        setIsAuthenticated(true);
        
        return { 
          success: true, 
          message: 'Login successful',
          user: response.data.data.user
        };
      } else {
        throw new Error(response.data.error || 'Login failed');
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message || 'Login failed';
      setError(errorMessage);
      return { 
        success: false, 
        message: errorMessage
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
      const response = await axios.post(`${API_URL}/auth/signup`, {
        email,
        password,
        first_name: firstName,
        last_name: lastName,
        role: userType
      });
      
      if (response.data.success) {
        localStorage.setItem('medichain_token', response.data.data.token);
        localStorage.setItem('medichain_user', JSON.stringify(response.data.data.user));
        
        setUser(response.data.data.user);
        setIsAuthenticated(true);
        
        return { 
          success: true, 
          message: 'Account created successfully!',
          user: response.data.data.user
        };
      } else {
        throw new Error(response.data.error || 'Signup failed');
      }
    } catch (error) {
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

  // Logout function
  const logout = () => {
    localStorage.removeItem('medichain_token');
    localStorage.removeItem('medichain_user');
    setIsAuthenticated(false);
    setUser(null);
    setError(null);
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

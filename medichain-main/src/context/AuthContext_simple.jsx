import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
      console.error('Backend server is not running or unreachable');
      error.isNetworkError = true;
    }
    return Promise.reject(error);
  }
);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check if user is logged in on mount
  useEffect(() => {
    const checkAuthState = async () => {
      const token = localStorage.getItem('token');
      const savedUser = localStorage.getItem('medichain_user');
      
      if (token && savedUser) {
        try {
          const userData = JSON.parse(savedUser);
          setUser(userData);
          setIsAuthenticated(true);
          // Verify token is still valid
          await fetchCurrentUser();
        } catch (error) {
          console.error('Error parsing saved user data:', error);
          clearAuthData();
        }
      } else {
        setLoading(false);
      }
    };

    checkAuthState();
  }, []);

  const clearAuthData = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('medichain_user');
    setUser(null);
    setIsAuthenticated(false);
    setError(null);
  };

  const fetchCurrentUser = async () => {
    try {
      const response = await api.get('/api/auth/me');
      if (response.data.success) {
        const userData = response.data.data.user;
        setUser(userData);
        setIsAuthenticated(true);
        localStorage.setItem('medichain_user', JSON.stringify(userData));
      }
    } catch (error) {
      console.error('Error fetching current user:', error);
      if (error.response?.status === 401) {
        clearAuthData();
      }
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      setError(null);
      setLoading(true);
      
      const response = await api.post('/api/auth/login', {
        email,
        password,
      });

      if (response.data.success) {
        const { user, token } = response.data.data;
        localStorage.setItem('token', token);
        localStorage.setItem('medichain_user', JSON.stringify(user));
        setUser(user);
        setIsAuthenticated(true);
        return { success: true };
      } else {
        throw new Error(response.data.error || 'Login failed');
      }
    } catch (error) {
      let errorMessage = 'Login failed. Please try again.';
      
      if (error.isNetworkError) {
        errorMessage = 'Cannot connect to server. Please check if the backend is running.';
      } else if (error.response?.data?.error) {
        errorMessage = error.response.data.error;
      } else if (error.message && !error.isNetworkError) {
        errorMessage = error.message;
      }
      
      setError(errorMessage);
      return { success: false, message: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const signup = async (email, password, fullName, role) => {
    try {
      setError(null);
      setLoading(true);
      
      const response = await api.post('/api/auth/signup', {
        email,
        password,
        full_name: fullName,
        role,
      });

      if (response.data.success) {
        // Automatically log in the user after successful signup
        const { user, token } = response.data.data;
        localStorage.setItem('token', token);
        localStorage.setItem('medichain_user', JSON.stringify(user));
        setUser(user);
        setIsAuthenticated(true);
        return { success: true, message: response.data.message };
      } else {
        throw new Error(response.data.error || 'Signup failed');
      }
    } catch (error) {
      let errorMessage = 'Registration failed. Please try again.';
      
      if (error.isNetworkError) {
        errorMessage = 'Cannot connect to server. Please check if the backend is running.';
      } else if (error.response?.data?.error) {
        errorMessage = error.response.data.error;
      } else if (error.message && !error.isNetworkError) {
        errorMessage = error.message;
      }
      
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    clearAuthData();
    return Promise.resolve();
  };

  const value = {
    user,
    login,
    signup,
    logout,
    loading,
    error,
    isAuthenticated,
    setError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;

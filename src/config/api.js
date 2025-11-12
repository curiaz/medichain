/**
 * API Configuration
 * Centralized API endpoints and URL building utilities
 */

// API Base URL - Change this based on environment
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// API Configuration Object
export const API_CONFIG = {
  BASE_URL: API_BASE_URL,
  ENDPOINTS: {
    // Contact endpoint
    CONTACT: '/api/contact',
    
    // Auth endpoints
    AUTH: {
      LOGIN: '/api/auth/login',
      REGISTER: '/api/auth/register',
      LOGOUT: '/api/auth/logout',
      VERIFY: '/api/auth/verify',
      VERIFY_PASSWORD: '/api/auth/verify-password',
      REACTIVATE: '/api/auth/reactivate-account'
    },
    
    // Profile endpoints
    PROFILE: {
      GET: '/api/profile',
      UPDATE: '/api/profile',
      DELETE: '/api/profile/delete-account',
      COMPLETE: '/api/profile/complete'
    },
    
    // Medical AI endpoints
    AI: {
      DIAGNOSE: '/api/medical-ai/diagnose',
      CHAT: '/api/medical-ai/chat',
      HISTORY: '/api/medical-ai/history'
    },
    
    // Patient endpoints
    PATIENT: {
      RECORDS: '/api/patient/records',
      APPOINTMENTS: '/api/patient/appointments',
      PRESCRIPTIONS: '/api/patient/prescriptions'
    },
    
    // Doctor endpoints
    DOCTOR: {
      PATIENTS: '/api/doctor/patients',
      APPOINTMENTS: '/api/doctor/appointments',
      PRESCRIPTIONS: '/api/doctor/prescriptions'
    }
  }
};

/**
 * Build a complete URL from an endpoint path
 * @param {string} endpoint - The API endpoint path
 * @param {Object} params - Optional query parameters
 * @returns {string} Complete URL
 */
export const buildURL = (endpoint, params = null) => {
  let url = `${API_CONFIG.BASE_URL}${endpoint}`;
  
  // Add query parameters if provided
  if (params && Object.keys(params).length > 0) {
    const queryString = Object.entries(params)
      .filter(([_, value]) => value !== null && value !== undefined)
      .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
      .join('&');
    
    if (queryString) {
      url += `?${queryString}`;
    }
  }
  
  return url;
};

/**
 * Helper function to make authenticated API requests
 * @param {string} endpoint - The API endpoint
 * @param {Object} options - Fetch options
 * @returns {Promise} Fetch promise
 */
export const apiRequest = async (endpoint, options = {}) => {
  const token = localStorage.getItem('medichain_token');
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    }
  };
  
  const finalOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers
    }
  };
  
  const url = buildURL(endpoint);
  const response = await fetch(url, finalOptions);
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || `HTTP Error ${response.status}`);
  }
  
  return response.json();
};

export default API_CONFIG;

// API Configuration for MediChain
// This handles different environments (development, production)

const getBaseURL = () => {
  // In development, use local Flask server
  if (process.env.NODE_ENV === 'development') {
    return 'http://localhost:5000';
  }
  
  // In production, use deployed backend
  return 'https://medichain.vercel.app';
};

export const API_CONFIG = {
  BASE_URL: getBaseURL(),
  API_URL: `${getBaseURL()}/api`,
  
  // Specific endpoints
  ENDPOINTS: {
    AUTH: {
      LOGIN: '/api/auth/login',
      REGISTER: '/api/auth/register',
      VERIFY: '/api/auth/verify',
      DOCTOR_SIGNUP: '/api/auth/doctor-signup',
      PROFILE: '/api/auth/profile'
    },
    AI: {
      START_CONVERSATION: '/api/ai/start-conversation',
      CONTINUE_CONVERSATION: '/api/ai/continue-conversation'
    },
    CONTACT: '/contact'
  }
};

// Helper function to build full URL
export const buildURL = (endpoint) => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};

// Helper function to build API URL
export const buildAPIURL = (endpoint) => {
  return `${API_CONFIG.API_URL}${endpoint}`;
};

export default API_CONFIG;
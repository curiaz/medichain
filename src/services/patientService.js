import axios from 'axios';

// Patient Service - handles patient data operations
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

export const patientService = {
  /**
   * Get all patients
   * @returns {Promise<Object>} List of patients
   */
  getAllPatients: async () => {
    try {
      const response = await api.get('/api/patients');
      return {
        success: true,
        data: response.data.data || response.data
      };
    } catch (error) {
      console.error('Get Patients Error:', error);
      
      if (error.isNetworkError) {
        // Return mock data if backend is not available
        return {
          success: true,
          data: [
            { 
              id: 1, 
              patient_id: 'P001', 
              name: 'John Doe', 
              age: 35, 
              gender: 'Male',
              email: 'john.doe@example.com',
              phone: '+1234567890'
            },
            { 
              id: 2, 
              patient_id: 'P002', 
              name: 'Jane Smith', 
              age: 28, 
              gender: 'Female',
              email: 'jane.smith@example.com',
              phone: '+1234567891'
            },
            { 
              id: 3, 
              patient_id: 'P003', 
              name: 'Robert Johnson', 
              age: 42, 
              gender: 'Male',
              email: 'robert.johnson@example.com',
              phone: '+1234567892'
            },
            { 
              id: 4, 
              patient_id: 'P004', 
              name: 'Emily Davis', 
              age: 31, 
              gender: 'Female',
              email: 'emily.davis@example.com',
              phone: '+1234567893'
            },
            { 
              id: 5, 
              patient_id: 'P005', 
              name: 'Michael Wilson', 
              age: 55, 
              gender: 'Male',
              email: 'michael.wilson@example.com',
              phone: '+1234567894'
            }
          ],
          isMockData: true
        };
      }
      
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to fetch patients',
        details: error.response?.data
      };
    }
  },

  /**
   * Get a specific patient by ID
   * @param {string} patientId - The patient ID
   * @returns {Promise<Object>} Patient data
   */
  getPatientById: async (patientId) => {
    try {
      const response = await api.get(`/api/patients/${patientId}`);
      return {
        success: true,
        data: response.data.data || response.data
      };
    } catch (error) {
      console.error('Get Patient Error:', error);
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to fetch patient'
      };
    }
  },

  /**
   * Create a new patient
   * @param {Object} patientData - The patient data
   * @returns {Promise<Object>} Created patient data
   */
  createPatient: async (patientData) => {
    try {
      const response = await api.post('/api/patients', patientData);
      return {
        success: true,
        data: response.data.data || response.data
      };
    } catch (error) {
      console.error('Create Patient Error:', error);
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to create patient'
      };
    }
  },

  /**
   * Update an existing patient
   * @param {string} patientId - The patient ID
   * @param {Object} patientData - The updated patient data
   * @returns {Promise<Object>} Updated patient data
   */
  updatePatient: async (patientId, patientData) => {
    try {
      const response = await api.put(`/api/patients/${patientId}`, patientData);
      return {
        success: true,
        data: response.data.data || response.data
      };
    } catch (error) {
      console.error('Update Patient Error:', error);
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to update patient'
      };
    }
  },

  /**
   * Delete a patient
   * @param {string} patientId - The patient ID
   * @returns {Promise<Object>} Deletion result
   */
  deletePatient: async (patientId) => {
    try {
      await api.delete(`/api/patients/${patientId}`);
      return {
        success: true,
        message: 'Patient deleted successfully'
      };
    } catch (error) {
      console.error('Delete Patient Error:', error);
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to delete patient'
      };
    }
  }
};

export default patientService;

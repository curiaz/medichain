import axios from 'axios';
import { API_CONFIG } from '../config/api';

// Get auth token from localStorage
const getAuthToken = () => {
  return localStorage.getItem('medichain_token');
};

// Create axios instance with default headers
const adminApi = axios.create({
  baseURL: API_CONFIG.API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
adminApi.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const adminService = {
  // Get all users with optional filters
  async getUsers(filters = {}) {
    try {
      const params = new URLSearchParams();
      if (filters.role) params.append('role', filters.role);
      if (filters.search) params.append('search', filters.search);
      if (filters.is_active !== undefined) params.append('is_active', filters.is_active);
      if (filters.page) params.append('page', filters.page);
      if (filters.limit) params.append('limit', filters.limit);

      const response = await adminApi.get(`/admin/users?${params.toString()}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching users:', error);
      throw error;
    }
  },

  // Get single user by ID
  async getUser(userId) {
    try {
      const response = await adminApi.get(`/admin/users/${userId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching user:', error);
      throw error;
    }
  },

  // Create new user
  async createUser(userData) {
    try {
      const response = await adminApi.post('/admin/users', userData);
      return response.data;
    } catch (error) {
      console.error('Error creating user:', error);
      throw error;
    }
  },

  // Update user
  async updateUser(userId, userData) {
    try {
      const response = await adminApi.put(`/admin/users/${userId}`, userData);
      return response.data;
    } catch (error) {
      console.error('Error updating user:', error);
      throw error;
    }
  },

  // Delete user
  async deleteUser(userId) {
    try {
      const response = await adminApi.delete(`/admin/users/${userId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting user:', error);
      throw error;
    }
  },

  // Change user role
  async changeUserRole(userId, newRole) {
    try {
      const response = await adminApi.put(`/admin/users/${userId}/role`, { role: newRole });
      return response.data;
    } catch (error) {
      console.error('Error changing user role:', error);
      throw error;
    }
  },

  // Update user status (activate/deactivate)
  async updateUserStatus(userId, isActive) {
    try {
      const response = await adminApi.put(`/admin/users/${userId}/status`, { is_active: isActive });
      return response.data;
    } catch (error) {
      console.error('Error updating user status:', error);
      throw error;
    }
  },

  // Get admin dashboard statistics
  async getStats() {
    try {
      const response = await adminApi.get('/admin/stats');
      return response.data;
    } catch (error) {
      console.error('Error fetching stats:', error);
      throw error;
    }
  },

  // Get all doctors (for admin view)
  async getDoctors(filters = {}) {
    try {
      const params = new URLSearchParams();
      if (filters.search) params.append('search', filters.search);
      if (filters.verified !== undefined) params.append('verified', filters.verified);

      const response = await adminApi.get(`/admin/doctors?${params.toString()}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching doctors:', error);
      throw error;
    }
  },

  // Get pending doctor verifications
  async getPendingDoctors() {
    try {
      const response = await adminApi.get('/admin/doctors/pending');
      return response.data;
    } catch (error) {
      console.error('Error fetching pending doctors:', error);
      throw error;
    }
  },

  // Approve doctor verification
  async approveDoctor(doctorId) {
    try {
      const response = await adminApi.post(`/admin/doctors/${doctorId}/approve`);
      return response.data;
    } catch (error) {
      console.error('Error approving doctor:', error);
      throw error;
    }
  },

  // Decline doctor verification
  async declineDoctor(doctorId, reason) {
    try {
      const response = await adminApi.post(`/admin/doctors/${doctorId}/decline`, { reason });
      return response.data;
    } catch (error) {
      console.error('Error declining doctor:', error);
      throw error;
    }
  },

  // Get doctor verification document
  async getDoctorDocument(doctorId) {
    try {
      const response = await adminApi.get(`/admin/doctors/${doctorId}/document`, {
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching doctor document:', error);
      throw error;
    }
  },
};

export default adminService;


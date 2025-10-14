/**
 * Settings Service
 * Handles all settings-related API calls for the MediChain application
 */

import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

/**
 * Get authorization header with Firebase token
 */
const getAuthHeader = () => {
  const token = localStorage.getItem('medichain_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

/**
 * Notification Preferences
 */
export const getNotificationPreferences = async () => {
  try {
    const response = await axios.get(`${API_URL}/settings/notifications`, {
      headers: getAuthHeader()
    });
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    console.error('Error fetching notification preferences:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to fetch notification preferences'
    };
  }
};

export const updateNotificationPreferences = async (preferences) => {
  try {
    const response = await axios.put(`${API_URL}/settings/notifications`, preferences, {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json'
      }
    });
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    console.error('Error updating notification preferences:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to update notification preferences'
    };
  }
};

/**
 * Password Management
 */
export const changePassword = async (passwordData) => {
  try {
    const response = await axios.post(`${API_URL}/settings/security/password`, passwordData, {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json'
      }
    });
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    console.error('Error changing password:', error);
    return {
      success: false,
      error: error.response?.data?.error || error.response?.data?.message || 'Failed to change password'
    };
  }
};

/**
 * Account Management
 */
export const deactivateAccount = async (password, reason = '') => {
  try {
    const response = await axios.post(`${API_URL}/settings/security/account/deactivate`, {
      password,
      reason
    }, {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json'
      }
    });
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    console.error('Error deactivating account:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to deactivate account'
    };
  }
};

export const deleteAccount = async (password, reason = '') => {
  try {
    const response = await axios.delete(`${API_URL}/settings/security/account/delete`, {
      data: {
        password,
        reason
      },
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json'
      }
    });
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    console.error('Error deleting account:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to delete account'
    };
  }
};

export const cancelAccountDeletion = async () => {
  try {
    const response = await axios.post(`${API_URL}/settings/security/account/delete/cancel`, {}, {
      headers: getAuthHeader()
    });
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    console.error('Error cancelling account deletion:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to cancel account deletion'
    };
  }
};

/**
 * Security Audit Log
 */
export const getSecurityAuditLog = async (limit = 50, offset = 0) => {
  try {
    const response = await axios.get(`${API_URL}/settings/security/audit-log`, {
      params: { limit, offset },
      headers: getAuthHeader()
    });
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    console.error('Error fetching audit log:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to fetch audit log'
    };
  }
};

/**
 * Active Sessions
 */
export const getActiveSessions = async () => {
  try {
    const response = await axios.get(`${API_URL}/settings/security/sessions`, {
      headers: getAuthHeader()
    });
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    console.error('Error fetching active sessions:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to fetch active sessions'
    };
  }
};

/**
 * Health Check
 */
export const healthCheck = async () => {
  try {
    const response = await axios.get(`${API_URL}/settings/health`);
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    console.error('Settings service health check failed:', error);
    return {
      success: false,
      error: 'Settings service is unavailable'
    };
  }
};

const settingsService = {
  getNotificationPreferences,
  updateNotificationPreferences,
  changePassword,
  deactivateAccount,
  deleteAccount,
  cancelAccountDeletion,
  getSecurityAuditLog,
  getActiveSessions,
  healthCheck
};

export default settingsService;

import axios from 'axios';

// Notification Service - connects to the notification backend
const NOTIFICATION_BASE_URL = process.env.REACT_APP_NOTIFICATION_API_URL || process.env.REACT_APP_API_URL || 'https://medichainn.onrender.com';

const api = axios.create({
  baseURL: NOTIFICATION_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
      console.error('Notification server is not running or unreachable');
    }
    return Promise.reject(error);
  }
);

export const notificationService = {
  /**
   * Get notifications for a user
   * @param {Object} params - Query parameters
   * @returns {Promise<Object>} Notifications response
   */
  getNotifications: async (params = {}) => {
    try {
      const {
        user_id = 'default_user',
        category = '',
        is_read = '',
        priority = '',
        page = 1,
        per_page = 20
      } = params;

      const queryParams = new URLSearchParams({
        user_id,
        page: page.toString(),
        per_page: per_page.toString()
      });

      if (category) queryParams.append('category', category);
      if (is_read !== '') queryParams.append('is_read', is_read.toString());
      if (priority) queryParams.append('priority', priority);

      console.log('🔔 Fetching notifications from:', `${NOTIFICATION_BASE_URL}/api/notifications?${queryParams}`);
      const response = await api.get(`/api/notifications?${queryParams}`);
      console.log('✅ Notifications fetched successfully:', response.data);
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('❌ Failed to get notifications:', error);
      console.error('Error details:', {
        message: error.message,
        code: error.code,
        response: error.response?.data,
        status: error.response?.status,
        baseURL: NOTIFICATION_BASE_URL
      });
      
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to load notifications'
      };
    }
  },

  /**
   * Create a new notification
   * @param {Object} notificationData - Notification data
   * @returns {Promise<Object>} Creation response
   */
  createNotification: async (notificationData) => {
    try {
      const response = await api.post('/api/notifications', notificationData);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Failed to create notification:', error);
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to create notification'
      };
    }
  },

  /**
   * Update a notification (mark as read, archive, etc.)
   * @param {string} notificationId - Notification ID
   * @param {Object} updateData - Update data
   * @returns {Promise<Object>} Update response
   */
  updateNotification: async (notificationId, updateData) => {
    try {
      const response = await api.put(`/api/notifications/${notificationId}`, updateData);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Failed to update notification:', error);
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to update notification'
      };
    }
  },

  /**
   * Delete a notification
   * @param {string} notificationId - Notification ID
   * @param {string} userId - User ID
   * @returns {Promise<Object>} Delete response
   */
  deleteNotification: async (notificationId, userId) => {
    try {
      const response = await api.delete(`/api/notifications/${notificationId}?user_id=${userId}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Failed to delete notification:', error);
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to delete notification'
      };
    }
  },

  /**
   * Bulk update notifications
   * @param {Object} bulkData - Bulk operation data
   * @returns {Promise<Object>} Bulk operation response
   */
  bulkUpdateNotifications: async (bulkData) => {
    try {
      const response = await api.post('/api/notifications/bulk', bulkData);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Failed to perform bulk operation:', error);
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to perform bulk operation'
      };
    }
  },

  /**
   * Get notification statistics
   * @param {string} userId - User ID
   * @returns {Promise<Object>} Statistics response
   */
  getNotificationStats: async (userId = 'default_user') => {
    try {
      const response = await api.get(`/api/notifications/stats?user_id=${userId}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Failed to get notification stats:', error);
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to get statistics',
        data: {
          stats: {
            total: 0,
            unread: 0,
            by_priority: {},
            by_category: {},
            recent: 0
          }
        }
      };
    }
  },

  /**
   * Mark notification as read
   * @param {string} notificationId - Notification ID
   * @param {string} userId - User ID
   * @returns {Promise<Object>} Update response
   */
  markAsRead: async (notificationId, userId) => {
    return notificationService.updateNotification(notificationId, {
      user_id: userId,
      is_read: true
    });
  },

  /**
   * Mark all notifications as read
   * @param {string} userId - User ID
   * @returns {Promise<Object>} Bulk update response
   */
  markAllAsRead: async (userId) => {
    return notificationService.bulkUpdateNotifications({
      user_id: userId,
      action: 'mark_all_read'
    });
  },

  /**
   * Create a medical notification (for AI diagnosis completion, etc.)
   * @param {string} userId - User ID
   * @param {string} title - Notification title
   * @param {string} message - Notification message
   * @param {Object} options - Additional options
   * @returns {Promise<Object>} Creation response
   */
  createMedicalNotification: async (userId, title, message, options = {}) => {
    const notificationData = {
      user_id: userId,
      title,
      message,
      type: options.type || 'info',
      category: 'medical',
      priority: options.priority || 'normal',
      action_url: options.action_url,
      action_label: options.action_label,
      metadata: options.metadata || {},
      expires_at: options.expires_at
    };

    return notificationService.createNotification(notificationData);
  },

  /**
   * Create a system notification
   * @param {string} userId - User ID
   * @param {string} title - Notification title
   * @param {string} message - Notification message
   * @param {Object} options - Additional options
   * @returns {Promise<Object>} Creation response
   */
  createSystemNotification: async (userId, title, message, options = {}) => {
    const notificationData = {
      user_id: userId,
      title,
      message,
      type: options.type || 'info',
      category: 'system',
      priority: options.priority || 'low',
      action_url: options.action_url,
      action_label: options.action_label,
      metadata: options.metadata || {}
    };

    return notificationService.createNotification(notificationData);
  }
};

export default notificationService;

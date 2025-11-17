import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './NotificationTable.css';

// Icons
const BellIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
  </svg>
);

const CheckIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
  </svg>
);

const TrashIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
  </svg>
);

const ArchiveIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8l6 6 6-6" />
  </svg>
);


const RefreshIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
  </svg>
);

const NotificationTable = ({ userId = 'default_user' }) => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({});
  const [selectedNotifications, setSelectedNotifications] = useState([]);
  const [filters, setFilters] = useState({
    category: '',
    priority: '',
    is_read: ''
  });
  const [pagination, setPagination] = useState({
    current_page: 1,
    per_page: 10,
    total: 0,
    total_pages: 0
  });

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://medichain.clinic';

  // Fetch notifications
  const fetchNotifications = useCallback(async (page = 1) => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        user_id: userId,
        page: page.toString(),
        per_page: pagination.per_page.toString()
      });

      // Add filters if set
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });

      const response = await axios.get(`${API_BASE_URL}/api/notifications?${params}`);
      
      if (response.data.success) {
        setNotifications(response.data.notifications);
        setPagination(response.data.pagination);
      } else {
        setError(response.data.error);
      }
    } catch (err) {
      setError('Failed to fetch notifications');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [filters, userId, pagination.per_page]);

  // Fetch notification stats
  const fetchStats = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/notifications/stats?user_id=${userId}`);
      if (response.data.success) {
        setStats(response.data.stats);
      }
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  }, [userId]);

  // Initial load
  useEffect(() => {
    fetchNotifications();
    fetchStats();
  }, [fetchNotifications, fetchStats]);

  // Mark notification as read
  const markAsRead = async (notificationId) => {
    try {
      await axios.put(`${API_BASE_URL}/api/notifications/${notificationId}`, {
        user_id: userId,
        is_read: true
      });
      
      // Update local state
      setNotifications(prev => 
        prev.map(notif => 
          notif.id === notificationId 
            ? { ...notif, is_read: true }
            : notif
        )
      );
      
      fetchStats(); // Refresh stats
    } catch (err) {
      console.error('Failed to mark as read:', err);
    }
  };

  // Archive notification
  const archiveNotification = async (notificationId) => {
    try {
      await axios.put(`${API_BASE_URL}/api/notifications/${notificationId}`, {
        user_id: userId,
        is_archived: true
      });
      
      // Remove from local state
      setNotifications(prev => prev.filter(notif => notif.id !== notificationId));
      fetchStats(); // Refresh stats
    } catch (err) {
      console.error('Failed to archive:', err);
    }
  };

  // Delete notification
  const deleteNotification = async (notificationId) => {
    if (!window.confirm('Are you sure you want to delete this notification?')) return;
    
    try {
      await axios.delete(`${API_BASE_URL}/api/notifications/${notificationId}?user_id=${userId}`);
      
      // Remove from local state
      setNotifications(prev => prev.filter(notif => notif.id !== notificationId));
      fetchStats(); // Refresh stats
    } catch (err) {
      console.error('Failed to delete:', err);
    }
  };

  // Bulk actions
  const handleBulkAction = async (action) => {
    if (selectedNotifications.length === 0) return;
    
    try {
      await axios.post(`${API_BASE_URL}/api/notifications/bulk`, {
        user_id: userId,
        action: action,
        notification_ids: selectedNotifications
      });
      
      // Refresh data
      fetchNotifications(pagination.current_page);
      fetchStats();
      setSelectedNotifications([]);
    } catch (err) {
      console.error('Bulk action failed:', err);
    }
  };

  // Toggle notification selection
  const toggleSelection = (notificationId) => {
    setSelectedNotifications(prev => 
      prev.includes(notificationId)
        ? prev.filter(id => id !== notificationId)
        : [...prev, notificationId]
    );
  };

  // Select all notifications
  const selectAll = () => {
    if (selectedNotifications.length === notifications.length) {
      setSelectedNotifications([]);
    } else {
      setSelectedNotifications(notifications.map(n => n.id));
    }
  };

  // Get priority badge class
  const getPriorityClass = (priority) => {
    switch (priority) {
      case 'high': return 'priority-high';
      case 'medium': return 'priority-medium';
      case 'low': return 'priority-low';
      default: return 'priority-normal';
    }
  };


  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffHours < 1) {
      const diffMins = Math.floor(diffMs / (1000 * 60));
      return `${diffMins}m ago`;
    } else if (diffHours < 24) {
      return `${diffHours}h ago`;
    } else if (diffDays < 7) {
      return `${diffDays}d ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  return (
    <div className="notification-table-container">
      {/* Header with Stats */}
      <div className="notification-header">
        <div className="header-title">
          <BellIcon />
          <h2>Notifications</h2>
          {stats.unread > 0 && (
            <span className="unread-badge">{stats.unread}</span>
          )}
        </div>
        
        <div className="header-stats">
          <div className="stat-item">
            <span className="stat-label">Total:</span>
            <span className="stat-value">{stats.total || 0}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Unread:</span>
            <span className="stat-value unread">{stats.unread || 0}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Recent:</span>
            <span className="stat-value">{stats.recent || 0}</span>
          </div>
        </div>
      </div>

      {/* Filters and Actions */}
      <div className="notification-controls">
        <div className="filters">
          <select 
            value={filters.category} 
            onChange={(e) => setFilters(prev => ({...prev, category: e.target.value}))}
            className="filter-select"
          >
            <option value="">All Categories</option>
            <option value="general">General</option>
            <option value="medical">Medical</option>
            <option value="system">System</option>
            <option value="appointment">Appointment</option>
          </select>
          
          <select 
            value={filters.priority} 
            onChange={(e) => setFilters(prev => ({...prev, priority: e.target.value}))}
            className="filter-select"
          >
            <option value="">All Priorities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="normal">Normal</option>
            <option value="low">Low</option>
          </select>
          
          <select 
            value={filters.is_read} 
            onChange={(e) => setFilters(prev => ({...prev, is_read: e.target.value}))}
            className="filter-select"
          >
            <option value="">All Status</option>
            <option value="false">Unread</option>
            <option value="true">Read</option>
          </select>
          
          <button onClick={() => fetchNotifications(1)} className="refresh-btn">
            <RefreshIcon />
          </button>
        </div>

        {selectedNotifications.length > 0 && (
          <div className="bulk-actions">
            <span className="selected-count">
              {selectedNotifications.length} selected
            </span>
            <button onClick={() => handleBulkAction('mark_all_read')} className="bulk-btn">
              <CheckIcon />
              Mark Read
            </button>
            <button onClick={() => handleBulkAction('archive_all')} className="bulk-btn">
              <ArchiveIcon />
              Archive
            </button>
          </div>
        )}
      </div>

      {/* Notification Table */}
      <div className="notification-table">
        {loading ? (
          <div className="loading-state">Loading notifications...</div>
        ) : error ? (
          <div className="error-state">Error: {error}</div>
        ) : notifications.length === 0 ? (
          <div className="empty-state">
            <BellIcon />
            <p>No notifications found</p>
          </div>
        ) : (
          <>
            <div className="table-header">
              <div className="header-cell select-cell">
                <input 
                  type="checkbox" 
                  checked={selectedNotifications.length === notifications.length}
                  onChange={selectAll}
                />
              </div>
              <div className="header-cell">Status</div>
              <div className="header-cell">Title</div>
              <div className="header-cell">Category</div>
              <div className="header-cell">Priority</div>
              <div className="header-cell">Date</div>
              <div className="header-cell">Actions</div>
            </div>
            
            <div className="table-body">
              {notifications.map((notification) => (
                <div 
                  key={notification.id} 
                  className={`table-row ${!notification.is_read ? 'unread' : ''}`}
                >
                  <div className="table-cell select-cell">
                    <input 
                      type="checkbox" 
                      checked={selectedNotifications.includes(notification.id)}
                      onChange={() => toggleSelection(notification.id)}
                    />
                  </div>
                  
                  <div className="table-cell">
                    <span className={`status-indicator ${notification.is_read ? 'read' : 'unread'}`}>
                      {notification.is_read ? '●' : '●'}
                    </span>
                  </div>
                  
                  <div className="table-cell title-cell">
                    <div className="notification-title">{notification.title}</div>
                    <div className="notification-message">{notification.message}</div>
                    {notification.action_url && (
                      <a href={notification.action_url} className="notification-action">
                        {notification.action_label || 'View Details'}
                      </a>
                    )}
                  </div>
                  
                  <div className="table-cell">
                    <span className="category-badge">{notification.category}</span>
                  </div>
                  
                  <div className="table-cell">
                    <span className={`priority-badge ${getPriorityClass(notification.priority)}`}>
                      {notification.priority}
                    </span>
                  </div>
                  
                  <div className="table-cell date-cell">
                    <span className="date-text">{formatDate(notification.created_at)}</span>
                  </div>
                  
                  <div className="table-cell actions-cell">
                    {!notification.is_read && (
                      <button 
                        onClick={() => markAsRead(notification.id)}
                        className="action-btn read-btn"
                        title="Mark as read"
                      >
                        <CheckIcon />
                      </button>
                    )}
                    <button 
                      onClick={() => archiveNotification(notification.id)}
                      className="action-btn archive-btn"
                      title="Archive"
                    >
                      <ArchiveIcon />
                    </button>
                    <button 
                      onClick={() => deleteNotification(notification.id)}
                      className="action-btn delete-btn"
                      title="Delete"
                    >
                      <TrashIcon />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      {/* Pagination */}
      {pagination.total_pages > 1 && (
        <div className="pagination">
          <button 
            onClick={() => fetchNotifications(pagination.current_page - 1)}
            disabled={pagination.current_page === 1}
            className="pagination-btn"
          >
            Previous
          </button>
          
          <span className="pagination-info">
            Page {pagination.current_page} of {pagination.total_pages}
          </span>
          
          <button 
            onClick={() => fetchNotifications(pagination.current_page + 1)}
            disabled={pagination.current_page === pagination.total_pages}
            className="pagination-btn"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default NotificationTable;
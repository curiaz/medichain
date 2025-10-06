import React, { useState, useEffect } from "react"
import Header from "./Header"
import { Bell, Check, X, AlertCircle, Info, Heart, Calendar, FileText, Settings } from "lucide-react"
import { useAuth } from "../context/AuthContext"
import notificationService from "../services/notificationService"
import "../assets/styles/ModernDashboard.css"

const Notifications = () => {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(false);
  const [, setStats] = useState({ total: 0, unread: 0 });

  useEffect(() => {
    // Load notifications when component mounts
    if (user?.uid) {
      loadNotifications();
      loadNotificationStats();
    }
  }, [user]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadNotificationStats = async () => {
    try {
      const result = await notificationService.getNotificationStats(user?.uid || 'default_user');
      if (result.success && result.data) {
        setStats(result.data.stats);
      }
    } catch (err) {
      console.error('Error loading notification stats:', err);
    }
  };

  const loadNotifications = async () => {
    try {
      setLoading(true);
      console.log('Loading notifications for user:', user?.uid);
      
      const result = await notificationService.getNotifications({
        user_id: user?.uid || 'default_user',
        page: 1,
        per_page: 50
      });

      if (result.success && result.data) {
        // Transform backend data to match frontend format
        const transformedNotifications = result.data.notifications?.map(notif => ({
          id: notif.id,
          type: notif.category || 'system',
          title: notif.title,
          message: notif.message,
          timestamp: new Date(notif.created_at),
          read: notif.is_read,
          priority: notif.priority,
          action_url: notif.action_url,
          action_label: notif.action_label
        })) || [];

        setNotifications(transformedNotifications);
        console.log('Loaded notifications:', transformedNotifications.length);
      } else {
        console.error('Failed to load notifications:', result.error);
        // Fallback to empty array on error
        setNotifications([]);
      }
    } catch (err) {
      console.error('Error loading notifications:', err);
      setNotifications([]);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      const result = await notificationService.markAsRead(notificationId, user?.uid || 'default_user');
      
      if (result.success) {
        setNotifications(prev => 
          prev.map(notif => 
            notif.id === notificationId 
              ? { ...notif, read: true }
              : notif
          )
        );
        console.log('Marked notification as read:', notificationId);
      } else {
        console.error('Failed to mark notification as read:', result.error);
      }
    } catch (err) {
      console.error('Error marking notification as read:', err);
    }
  };

  const markAllAsRead = async () => {
    try {
      const result = await notificationService.markAllAsRead(user?.uid || 'default_user');
      
      if (result.success) {
        setNotifications(prev => 
          prev.map(notif => ({ ...notif, read: true }))
        );
        console.log('Marked all notifications as read');
      } else {
        console.error('Failed to mark all notifications as read:', result.error);
      }
    } catch (err) {
      console.error('Error marking all notifications as read:', err);
    }
  };

  const deleteNotification = async (notificationId) => {
    try {
      const result = await notificationService.deleteNotification(notificationId, user?.uid || 'default_user');
      
      if (result.success) {
        setNotifications(prev => 
          prev.filter(notif => notif.id !== notificationId)
        );
        console.log('Deleted notification:', notificationId);
      } else {
        console.error('Failed to delete notification:', result.error);
      }
    } catch (err) {
      console.error('Error deleting notification:', err);
    }
  };

  const filteredNotifications = notifications.filter(notif => {
    if (filter === 'unread') return !notif.read;
    if (filter === 'read') return notif.read;
    return true;
  });

  const unreadCount = notifications.filter(n => !n.read).length;

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'appointment': return <Calendar size={20} />;
      case 'diagnosis': return <FileText size={20} />;
      case 'medication': return <Heart size={20} />;
      case 'system': return <Info size={20} />;
      default: return <Bell size={20} />;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return '#e74c3c';
      case 'medium': return '#f39c12';
      case 'low': return '#3498db';
      default: return '#95a5a6';
    }
  };

  const formatTimestamp = (timestamp) => {
    const now = new Date();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  };

  return (
    <div className="dashboard-container">
      {/* Background crosses */}
      <div className="background-crosses">
        {[...Array(24)].map((_, i) => (
          <span key={i} className={`cross cross-${i + 1}`}>
            +
          </span>
        ))}
      </div>

      <Header />

      <main className="dashboard-main-content">
        <div className="dashboard-header-section">
          <div className="dashboard-title-section">
            <h1 className="dashboard-title">NOTIFICATIONS</h1>
            {user && user.profile && (
              <div className="user-welcome">
                <span>Stay updated, <strong>{user.profile.first_name || user.profile.name}</strong></span>
                <span className="user-role">
                  {unreadCount > 0 ? `${unreadCount} unread notifications` : 'All caught up!'}
                </span>
              </div>
            )}
          </div>
        </div>

        <div className="dashboard-grid">

          {/* Main Content Area */}
          <div className="main-and-sidebar-grid">
            <div className="main-content-area">
              <div className="content-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                  <h3>
                    <Bell size={24} />
                    Your Notifications
                  </h3>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button 
                      className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
                      onClick={() => setFilter('all')}
                      style={{
                        padding: '8px 16px',
                        border: filter === 'all' ? '2px solid #2563eb' : '1px solid #d1d5db',
                        borderRadius: '6px',
                        backgroundColor: filter === 'all' ? '#eff6ff' : 'white',
                        color: filter === 'all' ? '#2563eb' : '#6b7280',
                        cursor: 'pointer',
                        fontSize: '14px',
                        fontWeight: filter === 'all' ? '600' : '400'
                      }}
                    >
                      All ({notifications.length})
                    </button>
                    <button 
                      className={`filter-btn ${filter === 'unread' ? 'active' : ''}`}
                      onClick={() => setFilter('unread')}
                      style={{
                        padding: '8px 16px',
                        border: filter === 'unread' ? '2px solid #2563eb' : '1px solid #d1d5db',
                        borderRadius: '6px',
                        backgroundColor: filter === 'unread' ? '#eff6ff' : 'white',
                        color: filter === 'unread' ? '#2563eb' : '#6b7280',
                        cursor: 'pointer',
                        fontSize: '14px',
                        fontWeight: filter === 'unread' ? '600' : '400'
                      }}
                    >
                      Unread ({unreadCount})
                    </button>
                  </div>
                </div>
                <div className="notifications-list">
                  {loading ? (
                    <div className="loading-state">
                      <p>Loading notifications...</p>
                    </div>
                  ) : filteredNotifications.length === 0 ? (
                    <div className="empty-state">
                      <Bell size={48} />
                      <p>No notifications to show</p>
                      <small>You're all caught up!</small>
                    </div>
                  ) : (
                    filteredNotifications.map(notification => (
                      <div 
                        key={notification.id} 
                        className={`notification-item ${!notification.read ? 'unread' : ''}`}
                      >
                        <div 
                          className="notification-priority-indicator"
                          style={{ backgroundColor: getPriorityColor(notification.priority) }}
                        ></div>
                        <div className="notification-icon">
                          {getNotificationIcon(notification.type)}
                        </div>
                        <div className="notification-content">
                          <div className="notification-title">
                            {notification.title}
                          </div>
                          <div className="notification-message">
                            {notification.message}
                          </div>
                          <div className="notification-timestamp">
                            {formatTimestamp(notification.timestamp)}
                          </div>
                        </div>
                        <div className="notification-actions">
                          {!notification.read && (
                            <button 
                              className="notification-action-btn"
                              onClick={() => markAsRead(notification.id)}
                              title="Mark as read"
                            >
                              <Check size={16} />
                            </button>
                          )}
                          <button 
                            className="notification-action-btn delete"
                            onClick={() => deleteNotification(notification.id)}
                            title="Delete notification"
                          >
                            <X size={16} />
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>

            {/* Sidebar */}
            <div className="sidebar-area">
              <div className="notification-settings-card">
                <h3 className="card-title">
                  <Settings size={20} />
                  Notification Settings
                </h3>
                <div className="settings-list">
                  <div className="setting-item">
                    <span>Email notifications</span>
                    <input type="checkbox" defaultChecked />
                  </div>
                  <div className="setting-item">
                    <span>SMS alerts</span>
                    <input type="checkbox" />
                  </div>
                  <div className="setting-item">
                    <span>Appointment reminders</span>
                    <input type="checkbox" defaultChecked />
                  </div>
                  <div className="setting-item">
                    <span>Medication reminders</span>
                    <input type="checkbox" defaultChecked />
                  </div>
                </div>
              </div>

              <div className="quick-access-card">
                <h3 className="card-title">
                  <Bell size={20} />
                  Quick Actions
                </h3>
                <div className="quick-actions">
                  <button className="quick-action-btn" onClick={markAllAsRead}>
                    <Check size={16} />
                    Mark All Read
                  </button>
                  <button className="quick-action-btn">
                    <Settings size={16} />
                    Notification Settings
                  </button>
                  <button className="quick-action-btn">
                    <AlertCircle size={16} />
                    Emergency Alerts
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default Notifications
import React, { useState, useEffect } from "react"
import Header from "./Header"
import { Bell, Check, X, AlertCircle, Info, Heart, Calendar, FileText, Settings } from "lucide-react"
import { useAuth } from "../context/AuthContext"
import "../assets/styles/ModernDashboard.css"

const Notifications = () => {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Load notifications when component mounts
    if (user?.uid) {
      loadNotifications();
    }
  }, [user]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadNotifications = async () => {
    try {
      setLoading(true);
      // TODO: Implement notifications loading from database
      // For now, using mock data
      const mockNotifications = [
        {
          id: 1,
          type: 'appointment',
          title: 'Appointment Reminder',
          message: 'Your appointment with Dr. Smith is scheduled for tomorrow at 2:00 PM',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
          read: false,
          priority: 'high'
        },
        {
          id: 2,
          type: 'diagnosis',
          title: 'AI Diagnosis Available',
          message: 'Your recent symptom analysis is ready for review',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1 day ago
          read: true,
          priority: 'medium'
        },
        {
          id: 3,
          type: 'medication',
          title: 'Medication Reminder',
          message: 'Time to take your prescribed medication',
          timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
          read: false,
          priority: 'high'
        },
        {
          id: 4,
          type: 'system',
          title: 'System Update',
          message: 'MediChain platform has been updated with new features',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 48), // 2 days ago
          read: true,
          priority: 'low'
        }
      ];
      setNotifications(mockNotifications);
      console.log('Loading notifications for user:', user?.uid);
    } catch (err) {
      console.error('Error loading notifications:', err);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = (notificationId) => {
    setNotifications(prev => 
      prev.map(notif => 
        notif.id === notificationId 
          ? { ...notif, read: true }
          : notif
      )
    );
  };

  const markAllAsRead = () => {
    setNotifications(prev => 
      prev.map(notif => ({ ...notif, read: true }))
    );
  };

  const deleteNotification = (notificationId) => {
    setNotifications(prev => 
      prev.filter(notif => notif.id !== notificationId)
    );
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
                <h3>
                  <Bell size={24} />
                  Your Notifications
                </h3>
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
                  <div className="coming-soon">
                    <p>🔔 Advanced notification system is being developed</p>
                    <p>Soon you'll receive real-time alerts for appointments, medication reminders, and health updates</p>
                  </div>
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
                  <button className="quick-action-btn">
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
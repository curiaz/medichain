import React, { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import Header from "./Header"
import { Bell, Check, X, AlertCircle, Info, Heart, Calendar, FileText, Settings } from "lucide-react"
import { useAuth } from "../context/AuthContext"
import { auth } from "../config/firebase"
import axios from "axios"
import "../assets/styles/ModernDashboard.css"

const Notifications = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
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
      // Get Firebase token (same pattern as loadNotifications)
      let token = null;
      
      try {
        const currentUser = auth.currentUser;
        if (currentUser) {
          token = await currentUser.getIdToken(true);
        }
      } catch (firebaseError) {
        console.warn('⚠️ Notifications: Could not get Firebase token for stats:', firebaseError);
      }
      
      if (!token) {
        token = sessionStorage.getItem('firebase_id_token') || 
                localStorage.getItem('firebase_id_token') ||
                localStorage.getItem('medichain_token');
      }
      
      if (!token) {
        console.warn('⚠️ Notifications: No token for stats request');
        return;
      }
      
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
      const response = await axios.get(`${API_BASE_URL}/api/notifications/stats`, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.data?.success && response.data?.stats) {
        setStats(response.data.stats);
        console.log('✅ Notifications: Stats loaded:', response.data.stats);
      }
    } catch (err) {
      console.error('❌ Notifications: Error loading notification stats:', err);
    }
  };

  const loadNotifications = async () => {
    try {
      setLoading(true);
      console.log('🔔 Notifications: Starting to load notifications...');
      
      // Get Firebase token (same pattern as other pages)
      let token = null;
      let tokenSource = 'unknown';
      
      // Strategy 1: Try to get Firebase token from auth.currentUser
      try {
        const currentUser = auth.currentUser;
        if (currentUser) {
          console.log('🔔 Notifications: Getting Firebase token from currentUser...');
          token = await currentUser.getIdToken(true); // Force refresh to get fresh token
          tokenSource = 'firebase';
          console.log('✅ Notifications: Got fresh Firebase token (length:', token.length, ')');
        } else {
          console.warn('⚠️ Notifications: auth.currentUser is null');
        }
      } catch (firebaseError) {
        console.warn('⚠️ Notifications: Could not get Firebase token:', firebaseError);
      }
      
      // Strategy 2: Check stored Firebase token
      if (!token) {
        const storedFirebaseToken = sessionStorage.getItem('firebase_id_token') || 
                                    localStorage.getItem('firebase_id_token');
        if (storedFirebaseToken) {
          console.log('✅ Notifications: Using stored Firebase token');
          token = storedFirebaseToken;
          tokenSource = 'stored_firebase';
        }
      }
      
      // Strategy 3: Fallback to medichain_token
      if (!token) {
        token = localStorage.getItem('medichain_token');
        tokenSource = 'medichain_token';
        if (token) {
          console.log('✅ Notifications: Using medichain_token as fallback (length:', token.length, ')');
        }
      }
      
      if (!token) {
        console.error('❌ Notifications: No token found, cannot load notifications');
        setNotifications([]);
        setLoading(false);
        return;
      }
      
      console.log('✅ Notifications: Token obtained from', tokenSource);
      console.log('🔔 Notifications: Making API request to http://localhost:5000/api/notifications');
      
      // Make API request
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
      const response = await axios.get(`${API_BASE_URL}/api/notifications`, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        params: {
          limit: 50
        }
      });

      console.log('📥 Notifications: API Response received:', response.status, response.statusText);
      console.log('📥 Notifications: Response data:', response.data);

      if (response.data?.success) {
        // Transform backend data to match frontend format
        const transformedNotifications = (response.data.notifications || []).map(notif => ({
          id: notif.id,
          type: notif.category || 'system',
          title: notif.title,
          message: notif.message,
          timestamp: new Date(notif.created_at),
          read: notif.is_read,
          priority: notif.priority,
          action_url: notif.action_url,
          action_label: notif.action_label,
          metadata: typeof notif.metadata === 'string' 
            ? (notif.metadata ? JSON.parse(notif.metadata) : {}) 
            : (notif.metadata || {}) // Include metadata for appointment links
        }));

        setNotifications(transformedNotifications);
        console.log('✅ Notifications: Loaded', transformedNotifications.length, 'notifications');
        console.log('✅ Notifications: Unread count:', response.data.unread_count);
      } else {
        console.error('❌ Notifications: Failed to load -', response.data?.error);
        setNotifications([]);
      }
    } catch (err) {
      console.error('❌ Notifications: Error loading notifications:', err);
      console.error('❌ Notifications: Error details:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status,
        statusText: err.response?.statusText
      });
      setNotifications([]);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      // Get Firebase token
      let token = null;
      try {
        const currentUser = auth.currentUser;
        if (currentUser) {
          token = await currentUser.getIdToken(true);
        }
      } catch (firebaseError) {
        console.warn('⚠️ Notifications: Could not get Firebase token:', firebaseError);
      }
      
      if (!token) {
        token = sessionStorage.getItem('firebase_id_token') || 
                localStorage.getItem('firebase_id_token') ||
                localStorage.getItem('medichain_token');
      }
      
      if (!token) {
        console.error('❌ Notifications: No token for mark as read');
        return;
      }
      
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
      const response = await axios.put(`${API_BASE_URL}/api/notifications/${notificationId}`, {
        is_read: true
      }, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.data?.success) {
        setNotifications(prev => 
          prev.map(notif => 
            notif.id === notificationId 
              ? { ...notif, read: true }
              : notif
          )
        );
        console.log('✅ Notifications: Marked notification as read:', notificationId);
        // Reload stats
        loadNotificationStats();
      } else {
        console.error('❌ Notifications: Failed to mark as read:', response.data?.error);
      }
    } catch (err) {
      console.error('❌ Notifications: Error marking as read:', err);
    }
  };

  const markAllAsRead = async () => {
    try {
      // Get Firebase token
      let token = null;
      try {
        const currentUser = auth.currentUser;
        if (currentUser) {
          token = await currentUser.getIdToken(true);
        }
      } catch (firebaseError) {
        console.warn('⚠️ Notifications: Could not get Firebase token:', firebaseError);
      }
      
      if (!token) {
        token = sessionStorage.getItem('firebase_id_token') || 
                localStorage.getItem('firebase_id_token') ||
                localStorage.getItem('medichain_token');
      }
      
      if (!token) {
        console.error('❌ Notifications: No token for mark all as read');
        return;
      }
      
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
      const response = await axios.post(`${API_BASE_URL}/api/notifications/read-all`, {}, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.data?.success) {
        setNotifications(prev => prev.map(notif => ({ ...notif, read: true })));
        console.log('✅ Notifications: Marked all notifications as read');
        // Reload stats
        loadNotificationStats();
      } else {
        console.error('❌ Notifications: Failed to mark all as read:', response.data?.error);
      }
    } catch (err) {
      console.error('❌ Notifications: Error marking all as read:', err);
    }
  };

  const deleteNotification = async (notificationId) => {
    try {
      // Get Firebase token
      let token = null;
      try {
        const currentUser = auth.currentUser;
        if (currentUser) {
          token = await currentUser.getIdToken(true);
        }
      } catch (firebaseError) {
        console.warn('⚠️ Notifications: Could not get Firebase token:', firebaseError);
      }
      
      if (!token) {
        token = sessionStorage.getItem('firebase_id_token') || 
                localStorage.getItem('firebase_id_token') ||
                localStorage.getItem('medichain_token');
      }
      
      if (!token) {
        console.error('❌ Notifications: No token for delete');
        return;
      }
      
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
      const response = await axios.delete(`${API_BASE_URL}/api/notifications/${notificationId}`, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.data?.success) {
        setNotifications(prev => prev.filter(notif => notif.id !== notificationId));
        console.log('✅ Notifications: Deleted notification:', notificationId);
        // Reload stats
        loadNotificationStats();
      } else {
        console.error('❌ Notifications: Failed to delete:', response.data?.error);
      }
    } catch (err) {
      console.error('❌ Notifications: Error deleting notification:', err);
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
      case 'high': return '#2196F3'; // Light blue
      case 'urgent': return '#1976D2'; // Darker blue
      case 'medium': return '#42A5F5'; // Medium blue
      case 'low': return '#90CAF9'; // Light blue
      default: return '#BBDEFB'; // Very light blue
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
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center', 
                  marginBottom: '24px',
                  paddingBottom: '16px',
                  borderBottom: '2px solid #E3F2FD'
                }}>
                  <h3 style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '12px',
                    color: '#1976D2',
                    fontSize: '1.5rem',
                    fontWeight: '700',
                    margin: 0
                  }}>
                    <div style={{
                      width: '40px',
                      height: '40px',
                      borderRadius: '10px',
                      background: 'linear-gradient(135deg, #2196F3 0%, #1976D2 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      boxShadow: '0 4px 12px rgba(33, 150, 243, 0.2)'
                    }}>
                      <Bell size={20} color="white" />
                    </div>
                    Your Notifications
                  </h3>
                  <div style={{ 
                    display: 'flex', 
                    gap: '8px',
                    background: '#f5f7fa',
                    padding: '4px',
                    borderRadius: '10px',
                    border: '1px solid #e1e8ed'
                  }}>
                    <button 
                      className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
                      onClick={() => setFilter('all')}
                      style={{
                        padding: '10px 20px',
                        border: 'none',
                        borderRadius: '8px',
                        backgroundColor: filter === 'all' ? '#2196F3' : 'transparent',
                        color: filter === 'all' ? 'white' : '#64748b',
                        cursor: 'pointer',
                        fontSize: '14px',
                        fontWeight: filter === 'all' ? '600' : '500',
                        transition: 'all 0.2s ease',
                        boxShadow: filter === 'all' ? '0 2px 4px rgba(33, 150, 243, 0.2)' : 'none'
                      }}
                    >
                      All ({notifications.length})
                    </button>
                    <button 
                      className={`filter-btn ${filter === 'unread' ? 'active' : ''}`}
                      onClick={() => setFilter('unread')}
                      style={{
                        padding: '10px 20px',
                        border: 'none',
                        borderRadius: '8px',
                        backgroundColor: filter === 'unread' ? '#2196F3' : 'transparent',
                        color: filter === 'unread' ? 'white' : '#64748b',
                        cursor: 'pointer',
                        fontSize: '14px',
                        fontWeight: filter === 'unread' ? '600' : '500',
                        transition: 'all 0.2s ease',
                        boxShadow: filter === 'unread' ? '0 2px 4px rgba(33, 150, 243, 0.2)' : 'none'
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
                        style={{
                          borderLeft: !notification.read ? `4px solid ${getPriorityColor(notification.priority)}` : '4px solid transparent',
                          background: !notification.read ? 'linear-gradient(135deg, #E3F2FD 0%, #ffffff 100%)' : 'white',
                          boxShadow: !notification.read ? '0 2px 8px rgba(33, 150, 243, 0.1)' : '0 1px 3px rgba(0, 0, 0, 0.05)'
                        }}
                      >
                        <div className="notification-icon" style={{
                          background: !notification.read 
                            ? 'linear-gradient(135deg, #2196F3 0%, #1976D2 100%)' 
                            : 'linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%)',
                          color: !notification.read ? 'white' : '#1976D2',
                          boxShadow: !notification.read 
                            ? '0 4px 12px rgba(33, 150, 243, 0.2)' 
                            : '0 2px 6px rgba(33, 150, 243, 0.1)'
                        }}>
                          {getNotificationIcon(notification.type)}
                        </div>
                        <div className="notification-content" style={{ flex: 1 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                            <div className="notification-title" style={{
                              color: !notification.read ? '#1976D2' : '#1a202c',
                              fontWeight: !notification.read ? '700' : '600'
                            }}>
                              {notification.title}
                            </div>
                            {!notification.read && (
                              <span style={{
                                width: '8px',
                                height: '8px',
                                borderRadius: '50%',
                                background: '#2196F3',
                                display: 'inline-block'
                              }}></span>
                            )}
                          </div>
                          <div className="notification-message" style={{
                            color: '#4a5568',
                            lineHeight: '1.5',
                            marginBottom: '6px'
                          }}>
                            {notification.message}
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                            <div className="notification-timestamp" style={{
                              color: '#90CAF9',
                              fontSize: '12px',
                              fontWeight: '500'
                            }}>
                              {formatTimestamp(notification.timestamp)}
                            </div>
                            {(notification.action_url || notification.metadata?.meeting_url) && (
                              <span style={{
                                fontSize: '12px',
                                color: '#2196F3',
                                fontWeight: '500',
                                cursor: 'pointer',
                                textDecoration: 'underline'
                              }} onClick={(e) => {
                                e.stopPropagation();
                                if (!notification.read) markAsRead(notification.id);
                                
                                // Check metadata first for meeting_url (Jitsi)
                                const meetingUrl = notification.metadata?.meeting_url;
                                const actionUrl = notification.action_url;
                                
                                // Priority: meeting_url > action_url
                                const urlToUse = meetingUrl || actionUrl;
                                
                                if (!urlToUse) return;
                                
                                // Check if it's an external URL (Jitsi meeting, etc.)
                                if (urlToUse.startsWith('http://') || urlToUse.startsWith('https://')) {
                                  // Check if it's a Jitsi meeting URL
                                  if (urlToUse.includes('meet.jit.si')) {
                                    const roomName = urlToUse.match(/meet\.jit\.si\/([^#\s]+)/)?.[1];
                                    if (roomName) {
                                      navigate(`/video/${roomName}`);
                                    } else {
                                      window.open(urlToUse, '_blank');
                                    }
                                  } else {
                                    // Other external URLs - open in new tab
                                    window.open(urlToUse, '_blank');
                                  }
                                } else {
                                  // Internal route - handle different cases
                                  if (urlToUse.startsWith('/appointments/')) {
                                    // Extract appointment ID
                                    const appointmentId = urlToUse.replace('/appointments/', '');
                                    // Navigate based on user role
                                    const userProfile = user?.profile || user;
                                    const userRole = userProfile?.role;
                                    if (userRole === 'doctor') {
                                      navigate('/doctor-schedule');
                                    } else {
                                      navigate('/my-appointments');
                                    }
                                  } else if (urlToUse.startsWith('/appointments')) {
                                    // General appointments page
                                    const userProfile = user?.profile || user;
                                    const userRole = userProfile?.role;
                                    if (userRole === 'doctor') {
                                      navigate('/doctor-schedule');
                                    } else {
                                      navigate('/my-appointments');
                                    }
                                  } else {
                                    // Other internal routes - use React Router navigate
                                    navigate(urlToUse);
                                  }
                                }
                              }}>
                                {notification.metadata?.meeting_url ? 'Join Call →' : 'View Details →'}
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="notification-actions" style={{ display: 'flex', gap: '6px' }}>
                          {!notification.read && (
                            <button 
                              className="notification-action-btn"
                              onClick={() => markAsRead(notification.id)}
                              title="Mark as read"
                              style={{
                                background: '#E3F2FD',
                                border: '1px solid #BBDEFB',
                                color: '#1976D2'
                              }}
                            >
                              <Check size={16} />
                            </button>
                          )}
                          <button 
                            className="notification-action-btn delete"
                            onClick={() => deleteNotification(notification.id)}
                            title="Delete notification"
                            style={{
                              background: '#f7fafc',
                              border: '1px solid #e2e8f0',
                              color: '#64748b'
                            }}
                            onMouseEnter={(e) => {
                              e.target.style.background = '#fee2e2';
                              e.target.style.borderColor = '#fecaca';
                              e.target.style.color = '#dc2626';
                            }}
                            onMouseLeave={(e) => {
                              e.target.style.background = '#f7fafc';
                              e.target.style.borderColor = '#e2e8f0';
                              e.target.style.color = '#64748b';
                            }}
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

export default Notifications;
import React, { useState, useEffect } from "react"
import { NavLink, useNavigate } from "react-router-dom"
import { Menu, X, User, LogOut, Bell, AlertCircle } from "lucide-react"
import { useAuth } from "../context/AuthContext"
import { auth } from "../config/firebase"
import axios from "axios"
import MedichainLogo from "../components/MedichainLogo"
import "../assets/styles/Header.css"

const Header = () => {
  const { logout, user } = useAuth()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [unreadCount, setUnreadCount] = useState(0)
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false)
  const navigate = useNavigate()

  const handleLogoutClick = () => {
    setShowLogoutConfirm(true)
  }

  const handleLogoutConfirm = () => {
    setShowLogoutConfirm(false)
    logout()
    navigate('/')
  }

  const handleLogoutCancel = () => {
    setShowLogoutConfirm(false)
  }

  const handleProfileClick = () => {
    console.log('Profile icon clicked in Header!')
    // Navigate to appropriate profile page based on user role
    if (user?.profile?.role === 'doctor') {
      navigate('/doctor-profile')
    } else {
      navigate('/profile')
    }
  }

  // Fetch notification stats
  const loadNotificationStats = React.useCallback(async () => {
    try {
      // Get Firebase token
      let token = null;
      
      try {
        const currentUser = auth.currentUser;
        if (currentUser) {
          token = await currentUser.getIdToken(true);
        }
      } catch (firebaseError) {
        console.warn('⚠️ Header: Could not get Firebase token for stats:', firebaseError);
      }
      
      if (!token) {
        token = sessionStorage.getItem('firebase_id_token') || 
                localStorage.getItem('firebase_id_token') ||
                localStorage.getItem('medichain_token');
      }
      
      if (!token) {
        console.log('⚠️ Header: No token available for notification stats');
        setUnreadCount(0);
        return;
      }
      
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
      console.log('🔔 Header: Fetching notification stats from', `${API_BASE_URL}/api/notifications/stats`);
      const response = await axios.get(`${API_BASE_URL}/api/notifications/stats`, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      console.log('✅ Header: Notification stats response:', response.data);
      
      if (response.data?.success && response.data?.stats) {
        const unread = response.data.stats.unread || 0;
        console.log('🔔 Header: Setting unread count to', unread);
        setUnreadCount(unread);
      } else {
        console.warn('⚠️ Header: Invalid stats response:', response.data);
        setUnreadCount(0);
      }
    } catch (err) {
      console.error('❌ Header: Error loading notification stats:', err);
      if (err.response) {
        console.error('❌ Header: Error response:', err.response.status, err.response.data);
      }
      setUnreadCount(0);
    }
  }, []);

  // Load notification stats when user changes
  useEffect(() => {
    // Get Firebase UID from user object - check multiple possible fields
    const userUid = user?.uid || user?.firebase_uid || user?.profile?.firebase_uid || user?.id;
    
    console.log('🔔 Header: User object:', user);
    console.log('🔔 Header: Checking UID fields - uid:', user?.uid, 'firebase_uid:', user?.firebase_uid, 'profile.firebase_uid:', user?.profile?.firebase_uid, 'id:', user?.id);
    
    if (userUid) {
      console.log('🔔 Header: User logged in, loading notification stats for:', userUid);
      loadNotificationStats();
      // Refresh stats every 30 seconds
      const interval = setInterval(loadNotificationStats, 30000);
      
      // Listen for appointment booked event to refresh notifications immediately
      const handleAppointmentBooked = () => {
        console.log('🔔 Header: Appointment booked, refreshing notifications...');
        // Wait a bit for backend to create notification
        setTimeout(() => {
          loadNotificationStats();
        }, 1500);
      };
      
      window.addEventListener('appointmentBooked', handleAppointmentBooked);
      
      return () => {
        clearInterval(interval);
        window.removeEventListener('appointmentBooked', handleAppointmentBooked);
      };
    } else {
      console.log('⚠️ Header: No user or no UID found, setting unread count to 0');
      console.log('⚠️ Header: User object:', user);
      setUnreadCount(0);
    }
  }, [user, loadNotificationStats]);

  // Refresh stats when navigating to notifications page
  useEffect(() => {
    const handleRouteChange = () => {
      if (window.location.pathname === '/notifications') {
        loadNotificationStats();
      }
    };
    
    // Listen for route changes
    window.addEventListener('popstate', handleRouteChange);
    return () => window.removeEventListener('popstate', handleRouteChange);
  }, []);

  return (
    <>
    <header className="dashboard-header">
      <div className="dashboard-header-container">
        {/* Left: Logo */}
        <div className="header-left">
          <div className="logo-container" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <MedichainLogo size={40} usePng={true} />
            <div>
              MEDICHAIN
            </div>
          </div>
        </div>

        {/* Center: Navigation */}
        <div className="header-center">
          <nav className="nav-links">
            <NavLink 
              to="/dashboard" 
              className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}
            >
              DASHBOARD
            </NavLink>

            <NavLink 
              to="/notifications" 
              className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}
              onClick={() => loadNotificationStats()}
            >
              <span style={{ display: 'flex', alignItems: 'center', gap: '8px', position: 'relative' }}>
                NOTIFICATIONS
                {unreadCount > 0 && (
                  <span className="notification-badge">{unreadCount > 99 ? '99+' : unreadCount}</span>
                )}
              </span>
            </NavLink>
          </nav>
        </div>

        {/* Right: Action Buttons */}
        <div className="header-right">
          {/* Desktop: Profile and Logout buttons */}
          <button className="icon-button desktop-only" title="Profile" onClick={handleProfileClick}>
            <User size={20} />
          </button>
          <button className="icon-button desktop-only" onClick={handleLogoutClick} title="Logout">
            <LogOut size={20} />
          </button>
          
          {/* Mobile: Burger menu only */}
          <button className="icon-button mobile-only burger-menu-button" title="Menu" aria-expanded={mobileOpen} onClick={() => setMobileOpen(!mobileOpen)}>
            {mobileOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>
      {mobileOpen && (
        <div className="mobile-dashboard-nav" role="navigation">
          <NavLink to="/dashboard" className={({ isActive }) => "nav-link" + (isActive ? " active" : "")} onClick={() => setMobileOpen(false)}>DASHBOARD</NavLink>
          <NavLink 
            to="/notifications" 
            className={({ isActive }) => "nav-link" + (isActive ? " active" : "")} 
            onClick={() => { setMobileOpen(false); loadNotificationStats(); }}
          >
            <span style={{ display: 'flex', alignItems: 'center', gap: '8px', position: 'relative' }}>
              NOTIFICATIONS
              {unreadCount > 0 && (
                <span className="notification-badge">{unreadCount > 99 ? '99+' : unreadCount}</span>
              )}
            </span>
          </NavLink>
          <button className="nav-link" onClick={() => { setMobileOpen(false); handleProfileClick(); }}>PROFILE</button>
          <button className="nav-link" onClick={handleLogoutClick}>LOG OUT</button>
        </div>
      )}
    </header>

    {/* Logout Confirmation Modal - Outside header for proper z-index */}
    {showLogoutConfirm && (
      <div className="logout-modal-overlay" onClick={handleLogoutCancel}>
        <div className="logout-modal" onClick={(e) => e.stopPropagation()}>
          <div className="logout-modal-header">
            <AlertCircle size={24} className="logout-modal-icon" />
            <h3 className="logout-modal-title">Confirm Logout</h3>
          </div>
          <div className="logout-modal-body">
            <p>Are you sure you want to log out?</p>
          </div>
          <div className="logout-modal-footer">
            <button className="logout-modal-button logout-modal-button-cancel" onClick={handleLogoutCancel}>
              Cancel
            </button>
            <button className="logout-modal-button logout-modal-button-confirm" onClick={handleLogoutConfirm}>
              Log Out
            </button>
          </div>
        </div>
      </div>
    )}
    </>
  )
}

export default Header

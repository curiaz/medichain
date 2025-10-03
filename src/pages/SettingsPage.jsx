import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { 
  Bell, Lock, Shield, Trash2, AlertCircle, 
  CheckCircle, Eye, EyeOff, Mail, MessageSquare,
  Calendar, Activity, Save, ArrowLeft, Power
} from 'lucide-react';
import Header from './Header';
import './SettingsPage.css';

export const SettingsPage = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  
  // State management
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Notification Preferences State
  const [notifications, setNotifications] = useState({
    email_notifications: true,
    sms_notifications: false,
    appointment_reminders: true,
    diagnosis_alerts: true
  });
  
  // Password Change State
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  });
  
  // Danger Zone State
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showDeactivateModal, setShowDeactivateModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  useEffect(() => {
    // Load saved preferences from localStorage
    const savedPreferences = localStorage.getItem('notification_preferences');
    if (savedPreferences) {
      try {
        setNotifications(JSON.parse(savedPreferences));
      } catch (err) {
        console.error('Error loading saved preferences:', err);
      }
    }
    setLoading(false);
  }, []);

  // =============================================================================
  // NOTIFICATION PREFERENCES
  // =============================================================================

  const handleNotificationToggle = (field) => {
    setNotifications(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };

  const handleSaveNotifications = () => {
    try {
      setSaving(true);
      setError('');
      setSuccess('');
      
      // Save to localStorage
      localStorage.setItem('notification_preferences', JSON.stringify(notifications));
      
      setSuccess('Notification preferences saved successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error('Error saving notification preferences:', err);
      setError('Failed to save notification preferences');
    } finally {
      setSaving(false);
    }
  };

  // =============================================================================
  // PASSWORD MANAGEMENT
  // =============================================================================

  const handlePasswordChange = (field, value) => {
    setPasswordData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const togglePasswordVisibility = (field) => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };

  const validatePasswordMatch = () => {
    if (passwordData.new_password !== passwordData.confirm_password) {
      setError('New passwords do not match');
      return false;
    }
    return true;
  };

  const handleChangePassword = (e) => {
    e.preventDefault();
    
    if (!validatePasswordMatch()) {
      return;
    }
    
    try {
      setSaving(true);
      setError('');
      setSuccess('');
      
      // Validate password strength
      if (passwordData.new_password.length < 8) {
        setError('Password must be at least 8 characters long');
        setSaving(false);
        return;
      }
      
      // Simulate password change success
      setSuccess('Password changed successfully!');
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: ''
      });
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error('Error changing password:', err);
      setError('Failed to change password');
    } finally {
      setSaving(false);
    }
  };

  // =============================================================================
  // ACCOUNT MANAGEMENT
  // =============================================================================

  const handleDeactivateAccount = () => {
    if (!confirmPassword) {
      setError('Please enter your password to confirm');
      return;
    }

    try {
      setSaving(true);
      setError('');
      
      setSuccess('Account deactivated successfully. Logging out...');
      setTimeout(() => {
        logout();
        navigate('/login');
      }, 2000);
    } catch (err) {
      console.error('Error deactivating account:', err);
      setError('Failed to deactivate account');
    } finally {
      setSaving(false);
      setShowDeactivateModal(false);
      setConfirmPassword('');
    }
  };

  const handleDeleteAccount = () => {
    if (!confirmPassword) {
      setError('Please enter your password to confirm');
      return;
    }

    try {
      setSaving(true);
      setError('');
      
      setSuccess('Account deletion initiated. Logging out...');
      setTimeout(() => {
        logout();
        navigate('/login');
      }, 2000);
    } catch (err) {
      console.error('Error deleting account:', err);
      setError('Failed to delete account');
    } finally {
      setSaving(false);
      setShowDeleteModal(false);
      setConfirmPassword('');
    }
  };

  // =============================================================================
  // RENDER
  // =============================================================================

  if (loading) {
    return (
      <>
        <Header />
        <div className="settings-container">
          <div className="settings-loading">
            <div className="spinner"></div>
            <p>Loading settings...</p>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Header />
      <div className="settings-container">
        <div className="settings-header">
          <button onClick={() => navigate(-1)} className="back-button">
            <ArrowLeft size={20} />
            Back
          </button>
          <h1>Settings</h1>
          <p className="settings-subtitle">Manage your account preferences and security</p>
        </div>

        {/* Error/Success Messages */}
        {error && (
          <div className="alert alert-error">
            <AlertCircle size={20} />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="alert alert-success">
            <CheckCircle size={20} />
            <span>{success}</span>
          </div>
        )}

        {/* Notification Preferences Section */}
        <div className="settings-card">
          <div className="settings-card-header">
            <Bell size={24} />
            <h2>Notification Preferences</h2>
          </div>
          <div className="settings-card-body">
            <div className="notification-item">
              <div className="notification-info">
                <Mail size={20} />
                <div>
                  <h3>Email Notifications</h3>
                  <p>Receive updates via email</p>
                </div>
              </div>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={notifications.email_notifications}
                  onChange={() => handleNotificationToggle('email_notifications')}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>

            <div className="notification-item">
              <div className="notification-info">
                <MessageSquare size={20} />
                <div>
                  <h3>SMS Notifications</h3>
                  <p>Receive text message alerts</p>
                </div>
              </div>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={notifications.sms_notifications}
                  onChange={() => handleNotificationToggle('sms_notifications')}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>

            <div className="notification-item">
              <div className="notification-info">
                <Calendar size={20} />
                <div>
                  <h3>Appointment Reminders</h3>
                  <p>Get reminded about upcoming appointments</p>
                </div>
              </div>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={notifications.appointment_reminders}
                  onChange={() => handleNotificationToggle('appointment_reminders')}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>

            <div className="notification-item">
              <div className="notification-info">
                <Activity size={20} />
                <div>
                  <h3>Diagnosis Alerts</h3>
                  <p>Receive AI diagnosis notifications</p>
                </div>
              </div>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={notifications.diagnosis_alerts}
                  onChange={() => handleNotificationToggle('diagnosis_alerts')}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>

            <button
              onClick={handleSaveNotifications}
              disabled={saving}
              className="save-button"
            >
              <Save size={20} />
              {saving ? 'Saving...' : 'Save Preferences'}
            </button>
          </div>
        </div>

        {/* Security & Password Section */}
        <div className="settings-card">
          <div className="settings-card-header">
            <Lock size={24} />
            <h2>Security & Password</h2>
          </div>
          <div className="settings-card-body">
            <form onSubmit={handleChangePassword}>
              <div className="form-group">
                <label>Current Password</label>
                <div className="password-input-wrapper">
                  <input
                    type={showPasswords.current ? 'text' : 'password'}
                    value={passwordData.current_password}
                    onChange={(e) => handlePasswordChange('current_password', e.target.value)}
                    placeholder="Enter current password"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => togglePasswordVisibility('current')}
                    className="password-toggle"
                  >
                    {showPasswords.current ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
              </div>

              <div className="form-group">
                <label>New Password</label>
                <div className="password-input-wrapper">
                  <input
                    type={showPasswords.new ? 'text' : 'password'}
                    value={passwordData.new_password}
                    onChange={(e) => handlePasswordChange('new_password', e.target.value)}
                    placeholder="Enter new password"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => togglePasswordVisibility('new')}
                    className="password-toggle"
                  >
                    {showPasswords.new ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
              </div>

              <div className="form-group">
                <label>Confirm New Password</label>
                <div className="password-input-wrapper">
                  <input
                    type={showPasswords.confirm ? 'text' : 'password'}
                    value={passwordData.confirm_password}
                    onChange={(e) => handlePasswordChange('confirm_password', e.target.value)}
                    placeholder="Confirm new password"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => togglePasswordVisibility('confirm')}
                    className="password-toggle"
                  >
                    {showPasswords.confirm ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={saving}
                className="change-password-button"
              >
                <Lock size={20} />
                {saving ? 'Changing...' : 'Change Password'}
              </button>
            </form>
          </div>
        </div>

        {/* Danger Zone Section */}
        <div className="settings-card danger-zone">
          <div className="settings-card-header">
            <Shield size={24} />
            <h2>Danger Zone</h2>
          </div>
          <div className="settings-card-body">
            <div className="danger-warning">
              <AlertCircle size={20} />
              <p>These actions are permanent and cannot be undone. Please proceed with caution.</p>
            </div>

            <div className="danger-actions">
              <button
                onClick={() => setShowDeactivateModal(true)}
                className="danger-button deactivate"
              >
                <Power size={20} />
                Deactivate Account
              </button>

              <button
                onClick={() => setShowDeleteModal(true)}
                className="danger-button delete"
              >
                <Trash2 size={20} />
                Delete Account
              </button>
            </div>
          </div>
        </div>

        {/* Deactivate Account Modal */}
        {showDeactivateModal && (
          <div className="modal-overlay">
            <div className="modal">
              <h3>Deactivate Account</h3>
              <p>Your account will be temporarily disabled. You can reactivate it by logging in again.</p>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Enter your password to confirm"
              />
              <div className="modal-actions">
                <button
                  onClick={() => {
                    setShowDeactivateModal(false);
                    setConfirmPassword('');
                  }}
                  className="modal-cancel"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDeactivateAccount}
                  disabled={saving}
                  className="modal-confirm deactivate"
                >
                  {saving ? 'Deactivating...' : 'Deactivate'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Delete Account Modal */}
        {showDeleteModal && (
          <div className="modal-overlay">
            <div className="modal">
              <h3>Delete Account</h3>
              <p className="modal-warning">
                This action is permanent and cannot be undone. All your data will be deleted within 30 days.
              </p>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Enter your password to confirm"
              />
              <div className="modal-actions">
                <button
                  onClick={() => {
                    setShowDeleteModal(false);
                    setConfirmPassword('');
                  }}
                  className="modal-cancel"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDeleteAccount}
                  disabled={saving}
                  className="modal-confirm delete"
                >
                  {saving ? 'Deleting...' : 'Delete Account'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default SettingsPage;

import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { 
  User, Heart, Lock, Key, 
  X,
  AlertCircle, CheckCircle, ArrowLeft, ShieldOff
} from 'lucide-react';
import './ProfilePage.css';

const DoctorProfilePage = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [activeTab, setActiveTab] = useState('personal');
  
  // Deactivate Account Modal States
  const [showDeactivateModal, setShowDeactivateModal] = useState(false);
  const [deactivateStep, setDeactivateStep] = useState(1); // 1: password, 2: confirmation
  const [deactivatePassword, setDeactivatePassword] = useState('');
  const [passwordVerifying, setPasswordVerifying] = useState(false);
  const [passwordError, setPasswordError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (user) {
      loadProfile();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  const loadProfile = async () => {
    try {
      setLoading(true);
      setError('');
      
      if (!user || user.profile?.role !== 'doctor') {
        setError('Access denied. This page is for doctors only.');
        setLoading(false);
        return;
      }

      // Load doctor profile data
      const userProfile = {
        first_name: user.profile?.first_name || user.displayName?.split(' ')[0] || '',
        last_name: user.profile?.last_name || user.displayName?.split(' ')[1] || '',
        email: user.email || user.profile?.email || '',
        phone: user.profile?.phone || '',
        role: 'doctor',
        avatar_url: user.profile?.avatar_url || user.photoURL || null,
        specialization: user.profile?.specialization || '',
        license_number: user.profile?.license_number || '',
        years_of_experience: user.profile?.years_of_experience || 0,
        hospital_affiliation: user.profile?.hospital_affiliation || '',
        bio: user.profile?.bio || ''
      };

      setProfile(userProfile);
      setLoading(false);
    } catch (err) {
      console.error('Error loading profile:', err);
      setError('Failed to load profile');
      setLoading(false);
    }
  };

  const handleDeactivateAccount = () => {
    setShowDeactivateModal(true);
    setDeactivateStep(1);
    setDeactivatePassword('');
    setPasswordError('');
  };

  const handleCloseDeactivateModal = () => {
    setShowDeactivateModal(false);
    setDeactivateStep(1);
    setDeactivatePassword('');
    setPasswordError('');
    setPasswordVerifying(false);
  };

  const handleVerifyPassword = async () => {
    if (!deactivatePassword.trim()) {
      setPasswordError('Please enter your password');
      return;
    }

    try {
      setPasswordVerifying(true);
      setPasswordError('');
      
      const token = localStorage.getItem('medichain_token');
      if (!token) {
        setPasswordError('Authentication token not found. Please log in again.');
        return;
      }

      const userEmail = user?.email || profile?.email;
      
      if (!userEmail) {
        setPasswordError('Email not found. Please log in again.');
        return;
      }

      const response = await fetch('http://localhost:5000/api/auth/verify-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          email: userEmail,
          password: deactivatePassword
        })
      });

      const result = await response.json();
      
      if (result.success) {
        setDeactivateStep(2);
        setPasswordError('');
      } else {
        const errorMsg = result.error || 'Incorrect password. Please try again.';
        setPasswordError(errorMsg);
      }
    } catch (err) {
      console.error('Error verifying password:', err);
      setPasswordError('Failed to verify password. Please try again.');
    } finally {
      setPasswordVerifying(false);
    }
  };

  const handleConfirmDeactivate = async () => {
    try {
      setSaving(true);
      setError('');
      
      const token = localStorage.getItem('medichain_token');
      if (!token) {
        setError('Authentication token not found. Please log in again.');
        return;
      }

      const response = await fetch('http://localhost:5000/api/profile/delete-account', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      const result = await response.json();
      
      if (result.success) {
        localStorage.removeItem('medichain_token');
        localStorage.removeItem('medichain_user');
        
        handleCloseDeactivateModal();
        
        setSuccess('✅ Your account has been deactivated. You will be redirected...');
        
        setTimeout(() => {
          window.location.href = '/';
        }, 2000);
      } else {
        setError(result.error || 'Failed to deactivate account. Please try again.');
        handleCloseDeactivateModal();
      }
    } catch (err) {
      console.error('Error deactivating account:', err);
      setError('Failed to deactivate account. Please try again or contact support.');
      handleCloseDeactivateModal();
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="profile-page">
        <div className="profile-loading-container">
          <div className="profile-loading-spinner"></div>
          <p>Loading your profile...</p>
        </div>
      </div>
    );
  }

  if (!user || user.profile?.role !== 'doctor') {
    return (
      <div className="profile-page">
        <div className="profile-error-container">
          <AlertCircle size={64} />
          <h2>Access Denied</h2>
          <p>This page is only accessible to doctors.</p>
        </div>
      </div>
    );
  }

  const userProfile = profile || {};

  return (
    <div className="profile-page">
      {/* Header */}
      <div className="profile-header-nav">
        <div className="container">
          <div className="profile-header-content">
            <div className="profile-header-left">
              <button 
                onClick={() => window.history.back()}
                className="profile-back-btn"
              >
                <ArrowLeft size={20} />
              </button>
              <h1 className="profile-header-title">Doctor Profile Management</h1>
            </div>
            <div className="profile-header-right">
              <div className="profile-welcome-text">
                Welcome, Dr. {userProfile.first_name || 'Doctor'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Alert Messages */}
      {error && (
        <div className="profile-alert-error">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}
      
      {success && (
        <div className="profile-alert-success">
          <CheckCircle size={20} />
          <span>{success}</span>
        </div>
      )}

      <div className="container">
        <div className="profile-main-container">
          {/* Profile Card */}
          <div className="profile-card-header">
            <div className="profile-card-content">
              <div className="profile-card-left">
                <div className="profile-avatar-container">
                  <div className="profile-avatar">
                    {userProfile.avatar_url ? (
                      <img src={userProfile.avatar_url} alt="Avatar" />
                    ) : (
                      <span>
                        {userProfile.first_name?.charAt(0)?.toUpperCase() || 'D'}
                      </span>
                    )}
                  </div>
                </div>
                <div className="profile-card-info">
                  <h2>Dr. {userProfile.first_name} {userProfile.last_name}</h2>
                  <p className="profile-card-role">{userProfile.specialization || 'Medical Doctor'}</p>
                  <p className="profile-card-email">{userProfile.email}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Tab Container */}
          <div className="profile-tab-container">
            {/* Tab Navigation */}
            <div className="profile-tab-navigation">
              <nav className="profile-tab-nav-list">
                {[
                  { id: 'personal', label: 'Personal Info', icon: User },
                  { id: 'professional', label: 'Professional Details', icon: Heart },
                  { id: 'credentials', label: 'Account Security', icon: Key }
                ].map(tab => (
                  <li key={tab.id} className="profile-tab-nav-item">
                    <button
                      onClick={() => setActiveTab(tab.id)}
                      className={`profile-tab-nav-button ${activeTab === tab.id ? 'active' : ''}`}
                    >
                      <tab.icon size={18} />
                      <span>{tab.label}</span>
                    </button>
                  </li>
                ))}
              </nav>
            </div>

            {/* Tab Content */}
            <div className="profile-tab-content">
              {activeTab === 'credentials' && (
                <div className="profile-tab-section">
                  <h3 className="profile-tab-title">Account Security</h3>
                  
                  {/* Security Settings */}
                  <div className="profile-security-settings">
                    {/* Email Address */}
                    <div className="profile-security-item">
                      <div className="profile-security-item-content">
                        <h4>Email Address</h4>
                        <p className="profile-security-item-description">Update your email address</p>
                      </div>
                      <button className="profile-btn profile-btn-primary profile-btn-sm">
                        Update Email
                      </button>
                    </div>

                    {/* Password */}
                    <div className="profile-security-item">
                      <div className="profile-security-item-content">
                        <h4>Password</h4>
                        <p className="profile-security-item-description">Change your password</p>
                      </div>
                      <button className="profile-btn profile-btn-primary profile-btn-sm">
                        Change Password
                      </button>
                    </div>

                    {/* Two-Factor Authentication */}
                    <div className="profile-security-item">
                      <div className="profile-security-item-content">
                        <h4>Two-Factor Authentication</h4>
                        <p className="profile-security-item-description">Add an extra layer of security</p>
                      </div>
                      <button className="profile-btn profile-btn-success profile-btn-sm">
                        Enable 2FA
                      </button>
                    </div>
                  </div>
                  
                  {/* Deactivate Account Section */}
                  <div className="profile-danger-zone">
                    <h4 className="profile-danger-zone-title">Account Deactivation</h4>
                    <div className="profile-danger-zone-content">
                      <div className="profile-danger-warning">
                        <ShieldOff size={20} />
                        <div>
                          <p className="profile-danger-warning-title">Deactivate Doctor Account</p>
                          <p className="profile-danger-warning-text">
                            Deactivating your account will disable your login access, but patients will still be able to view 
                            your profile and past medical records. This action prevents data loss for patient care continuity.
                          </p>
                        </div>
                      </div>
                      <button 
                        onClick={handleDeactivateAccount}
                        disabled={saving}
                        className="profile-btn profile-btn-danger"
                      >
                        <ShieldOff size={16} />
                        {saving ? 'Processing...' : 'Deactivate Account'}
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'personal' && (
                <div className="profile-tab-section">
                  <h3 className="profile-tab-title">Personal Information</h3>
                  <p>Personal information management for doctors.</p>
                </div>
              )}

              {activeTab === 'professional' && (
                <div className="profile-tab-section">
                  <h3 className="profile-tab-title">Professional Details</h3>
                  <p>Professional information, specialization, and credentials.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Deactivate Account Modal */}
      {showDeactivateModal && (
        <div className="profile-modal-overlay" onClick={handleCloseDeactivateModal}>
          <div className="profile-modal-content profile-delete-modal" onClick={(e) => e.stopPropagation()}>
            <button className="profile-modal-close" onClick={handleCloseDeactivateModal}>
              <X size={24} />
            </button>

            {deactivateStep === 1 ? (
              /* Step 1: Password Verification */
              <>
                <div className="profile-modal-header">
                  <AlertCircle size={48} className="profile-modal-icon-warning" />
                  <h2>Verify Your Identity</h2>
                  <p>Please enter your password to continue with account deactivation</p>
                </div>

                <div className="profile-modal-body">
                  <div className="profile-modal-warning-box">
                    <div>
                      <p className="profile-modal-warning-title">Account Deactivation for Doctors</p>
                      <p className="profile-modal-warning-text">
                        Deactivating your doctor account will:
                      </p>
                      <ul className="profile-modal-warning-list">
                        <li>Disable your login access</li>
                        <li>Keep your profile visible to patients</li>
                        <li>Preserve all medical records and history</li>
                        <li>Maintain patient care continuity</li>
                        <li>Allow profile viewing but not editing</li>
                      </ul>
                    </div>
                  </div>

                  <div className="profile-form-group">
                    <label className="profile-form-label">
                      <Lock size={16} />
                      Enter Your Password
                    </label>
                    <input
                      type="password"
                      value={deactivatePassword}
                      onChange={(e) => setDeactivatePassword(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleVerifyPassword()}
                      className="profile-form-input"
                      placeholder="Enter your password"
                      autoFocus
                      disabled={passwordVerifying}
                    />
                    {passwordError && (
                      <p className="profile-form-error">
                        <AlertCircle size={16} />
                        {passwordError}
                      </p>
                    )}
                  </div>
                </div>

                <div className="profile-modal-footer">
                  <button 
                    onClick={handleCloseDeactivateModal}
                    className="profile-btn profile-btn-secondary"
                    disabled={passwordVerifying}
                  >
                    Cancel
                  </button>
                  <button 
                    onClick={handleVerifyPassword}
                    className="profile-btn profile-btn-primary"
                    disabled={passwordVerifying || !deactivatePassword.trim()}
                  >
                    {passwordVerifying ? 'Verifying...' : 'Verify Password'}
                  </button>
                </div>
              </>
            ) : (
              /* Step 2: Final Confirmation */
              <>
                <div className="profile-modal-header">
                  <ShieldOff size={48} className="profile-modal-icon-danger" />
                  <h2>Final Confirmation</h2>
                  <p>Are you sure you want to deactivate your doctor account?</p>
                </div>

                <div className="profile-modal-body">
                  <div className="profile-modal-danger-box">
                    <h3>⚠️ Deactivation Details:</h3>
                    <div className="profile-modal-delete-list">
                      <div className="profile-modal-delete-item">
                        <CheckCircle size={20} />
                        <span>Your login access will be disabled</span>
                      </div>
                      <div className="profile-modal-delete-item">
                        <CheckCircle size={20} />
                        <span>Patients can still view your profile</span>
                      </div>
                      <div className="profile-modal-delete-item">
                        <CheckCircle size={20} />
                        <span>All medical records remain accessible</span>
                      </div>
                      <div className="profile-modal-delete-item">
                        <CheckCircle size={20} />
                        <span>Patient care continuity is maintained</span>
                      </div>
                      <div className="profile-modal-delete-item">
                        <CheckCircle size={20} />
                        <span>Your professional data is preserved</span>
                      </div>
                    </div>
                    <p className="profile-modal-danger-text">
                      <strong>Note:</strong> You will not be able to login after deactivation. 
                      Contact support to reactivate your account.
                    </p>
                  </div>
                </div>

                <div className="profile-modal-footer">
                  <button 
                    onClick={handleCloseDeactivateModal}
                    className="profile-btn profile-btn-success"
                    disabled={saving}
                  >
                    No, Keep My Account Active
                  </button>
                  <button 
                    onClick={handleConfirmDeactivate}
                    className="profile-btn profile-btn-danger"
                    disabled={saving}
                  >
                    <ShieldOff size={16} />
                    {saving ? 'Deactivating...' : 'Yes, Deactivate My Account'}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default DoctorProfilePage;

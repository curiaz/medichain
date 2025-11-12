import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { SupabaseService } from '../config/supabase';
import { 
  User, Heart, FileText, Lock, Key, History, 
  Edit3, Save, X, Camera, Plus, Trash2, 
  AlertCircle, CheckCircle, UploadIcon, ArrowLeft
} from 'lucide-react';
import './ProfilePage.css';

const ProfilePage = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [editing, setEditing] = useState(false);
  const [activeTab, setActiveTab] = useState('personal');
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    email: ''
  });

  const [medicalInfo, setMedicalInfo] = useState({
    medical_conditions: [],
    allergies: [],
    current_medications: [],
    blood_type: '',
    medical_notes: ''
  });

  const [privacySettings, setPrivacySettings] = useState({
    profile_visibility: 'private',
    medical_info_visible_to_doctors: true,
    medical_info_visible_to_hospitals: false,
    medical_info_visible_to_admins: false,
    allow_ai_analysis: true,
    share_data_for_research: false,
    emergency_access_enabled: true,
    two_factor_enabled: false,
    login_notifications: true,
    data_export_enabled: true
  });

  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [auditTrail, setAuditTrail] = useState([]);
  
  // Delete Account Modal States
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteStep, setDeleteStep] = useState(1); // 1: password, 2: confirmation
  const [deletePassword, setDeletePassword] = useState('');
  const [passwordVerifying, setPasswordVerifying] = useState(false);
  const [passwordError, setPasswordError] = useState('');

  useEffect(() => {
    if (user) {
      loadProfile();
    }
  }, [user]);

  const createBasicFallback = (user) => {
    console.log('🔧 Creating fallback for user:', user);
    const firstName = user.displayName?.split(' ')[0] || user.email?.split('@')[0] || 'User';
    const lastName = user.displayName?.split(' ')[1] || '';
    const email = user.email || '';
    
    console.log('🔧 Generated data:', { firstName, lastName, email });
    
    return {
      first_name: firstName,
      last_name: lastName,
      phone: '',
      email: email,
      medical_conditions: [],
      allergies: [],
      current_medications: [],
      blood_type: '',
      medical_notes: ''
    };
  };

  const loadProfile = async () => {
    console.log('🚀 LOADING PROFILE - ENHANCED MODE');
    console.log('👤 User object:', user);
    
    try {
      setLoading(true);
      setError('');
      
      if (!user) {
        console.log('❌ No user found');
        setError('No user found');
        setLoading(false);
        return;
      }
      
      // Check if user is a patient
      if (user.profile?.role === 'doctor') {
        setError('Access denied. This page is for patients only. Please use the Doctor Profile page.');
        setLoading(false);
        return;
      }
      
      // Debug: Log the complete user object structure
      console.log('🔍 Complete user object structure:', JSON.stringify(user, null, 2));
      console.log('🔍 User properties:', Object.keys(user));
      
      // Extract profile data from the nested structure
      const profile = user.profile || {};
      console.log('🔍 Profile data:', profile);
      
      // Parse name more intelligently
      let firstName = '';
      let lastName = '';
      
      // Try different name sources - profile data first, then fallback to Firebase data
      if (profile.first_name && profile.last_name) {
        firstName = profile.first_name;
        lastName = profile.last_name;
      } else if (profile.full_name) {
        const nameParts = profile.full_name.split(' ');
        firstName = nameParts[0] || '';
        lastName = nameParts.slice(1).join(' ') || '';
      } else if (user.displayName) {
        const nameParts = user.displayName.split(' ');
        firstName = nameParts[0] || '';
        lastName = nameParts.slice(1).join(' ') || '';
      } else if (user.name) {
        const nameParts = user.name.split(' ');
        firstName = nameParts[0] || '';
        lastName = nameParts.slice(1).join(' ') || '';
      } else if (user.email) {
        firstName = user.email.split('@')[0] || 'User';
        lastName = '';
      } else {
        firstName = 'User';
        lastName = '';
      }
      
      console.log('🎯 Parsed names - First:', firstName, 'Last:', lastName);
      
      // Start with user data from AuthContext (Firebase + Backend)
      let userData = {
        first_name: firstName,
        last_name: lastName,
        phone: profile.phone || user.phone || user.phoneNumber || '',
        email: user.email || profile.email || '',
        role: profile.role || user.role || 'patient',
        patient_id: profile.patient_id || user.patient_id || user.uid || null,
        avatar_url: profile.avatar_url || user.avatar_url || user.photoURL || null,
        created_at: profile.created_at || user.created_at || user.metadata?.creationTime || null,
        last_login: profile.last_login || user.last_login || user.metadata?.lastSignInTime || null,
        medical_conditions: profile.medical_conditions || user.medical_conditions || [],
        allergies: profile.allergies || user.allergies || [],
        current_medications: profile.current_medications || user.current_medications || [],
        blood_type: profile.blood_type || user.blood_type || '',
        medical_notes: profile.medical_notes || user.medical_notes || ''
      };
      
      console.log('📋 Initial userData:', userData);
      
      // Try to fetch additional profile data from Supabase (only if we don't already have it)
      console.log('🔍 Fetching additional profile data from Supabase...');
      const userId = user.uid || user.profile?.firebase_uid;
      console.log('🆔 Using user ID for Supabase fetch:', userId);
      
      try {
        const profileResult = await SupabaseService.getUserProfile(userId);
        if (profileResult.success && profileResult.data) {
          console.log('📊 Supabase profile data:', profileResult.data);
          // Merge Supabase data with existing user data, but don't overwrite what we already have
          userData = {
            ...profileResult.data,
            ...userData,
            // Keep Firebase auth data as primary for email and user ID
            email: user.email,
            firebase_uid: userId
          };
          console.log('🔄 Merged profile data:', userData);
        } else {
          console.log('ℹ️ No additional profile data found in Supabase, using auth data only');
          console.log('ℹ️ Profile result:', profileResult);
        }
      } catch (supabaseError) {
        console.warn('⚠️ Could not fetch Supabase profile data:', supabaseError);
        // Continue with auth data only
      }
      
      console.log('🎯 Final user data:', userData);
      
      setProfile(userData);
      setFormData({
        first_name: userData.first_name,
        last_name: userData.last_name,
        phone: userData.phone,
        email: userData.email
      });
      setMedicalInfo({
        medical_conditions: userData.medical_conditions,
        allergies: userData.allergies,
        current_medications: userData.current_medications,
        blood_type: userData.blood_type,
        medical_notes: userData.medical_notes
      });
      setDocuments([]);
      setAuditTrail([]);
      setSuccess('Profile loaded successfully!');
      setTimeout(() => setSuccess(''), 3000);
      
      console.log('✅ PROFILE LOADED SUCCESSFULLY!');
    } catch (error) {
      console.error('❌ Error loading profile:', error);
      setError('Failed to load profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handlePersonalInfoUpdate = async () => {
    try {
      setSaving(true);
      setError('');
      
      console.log('💾 Updating personal info via backend API...');
      
      const updateData = {
        first_name: formData.first_name,
        last_name: formData.last_name,
        phone: formData.phone,
        role: profile?.role || 'patient'
      };

      // Use backend API instead of direct Supabase to bypass RLS issues
      const token = localStorage.getItem('medichain_token');
      if (!token) {
        setError('Authentication token not found. Please log in again.');
        setSaving(false);
        return;
      }

      const response = await fetch('http://localhost:5000/api/auth/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(updateData)
      });

      const result = await response.json();
      
      if (result.success) {
        // Update local state
        const updatedProfile = { ...profile, ...updateData };
        setProfile(updatedProfile);
        setFormData({
          ...formData,
          first_name: updateData.first_name,
          last_name: updateData.last_name,
          phone: updateData.phone
        });
        setSuccess('Personal information updated successfully!');
        setEditing(false);
        setTimeout(() => setSuccess(''), 3000);
        console.log('✅ Personal info updated successfully via backend!');
      } else {
        setError(result.error || 'Failed to update personal information');
        console.log('❌ Backend update failed:', result.error);
      }
    } catch (err) {
      console.error('❌ Error updating personal info:', err);
      setError('Failed to update personal information. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleMedicalInfoUpdate = async () => {
    try {
      setSaving(true);
      setError('');
      
      console.log('💾 Updating medical info via backend API...');
      
      const updateData = {
        medical_conditions: medicalInfo.medical_conditions,
        allergies: medicalInfo.allergies,
        current_medications: medicalInfo.current_medications,
        blood_type: medicalInfo.blood_type,
        medical_notes: medicalInfo.medical_notes
      };

      // Use backend API instead of direct Supabase to bypass RLS issues
      const token = localStorage.getItem('medichain_token');
      if (!token) {
        setError('Authentication token not found. Please log in again.');
        return;
      }

      const response = await fetch('http://localhost:5000/api/auth/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(updateData)
      });

      const result = await response.json();
      
      if (result.success) {
        // Update local state
        const updatedProfile = { ...profile, ...updateData };
        setProfile(updatedProfile);
        setMedicalInfo(updateData);
        setSuccess('Medical information updated successfully!');
        setEditing(false);
        setTimeout(() => setSuccess(''), 3000);
        console.log('✅ Medical info updated successfully via backend!');
      } else {
        setError(result.error || 'Failed to update medical information');
        console.log('❌ Backend update failed:', result.error);
      }
    } catch (err) {
      console.error('❌ Error updating medical info:', err);
      setError('Failed to update medical information. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handlePrivacySettingsUpdate = async () => {
    try {
      setSaving(true);
      setError('');
      
      console.log('💾 Updating privacy settings...');
      
      // Note: Privacy settings might need a separate table in the future
      // For now, we'll store them in the user profile
      const updateData = {
        privacy_settings: privacySettings
      };

      const userId = user.uid || user.profile?.firebase_uid;
      console.log('🆔 Using user ID for privacy update:', userId);
      const result = await SupabaseService.updateUserProfile(userId, updateData);
      
      if (result.success) {
        setSuccess('Privacy settings updated successfully!');
        setEditing(false);
        setTimeout(() => setSuccess(''), 3000);
        console.log('✅ Privacy settings updated successfully!');
      } else {
        setError(result.error || 'Failed to update privacy settings');
        console.log('❌ Update failed:', result.error);
      }
    } catch (err) {
      console.error('❌ Error updating privacy settings:', err);
      setError('Failed to update privacy settings. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleDocumentUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      setUploading(true);
      setError('');
      
      console.log('📄 Uploading document...');
      
      // For now, we'll just show a success message
      // Document upload functionality would need to be implemented with Supabase Storage
      setSuccess('Document upload functionality coming soon!');
      setTimeout(() => setSuccess(''), 3000);
      console.log('✅ Document upload (placeholder)');
      
    } catch (err) {
      console.error('❌ Error uploading document:', err);
      setError('Failed to upload document. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleDocumentDelete = async (documentId) => {
    try {
      setError('');
      
      console.log('🗑️ Deleting document...');
      
      // For now, we'll just show a success message
      // Document deletion functionality would need to be implemented with Supabase Storage
      setSuccess('Document deletion functionality coming soon!');
      setTimeout(() => setSuccess(''), 3000);
      console.log('✅ Document deletion (placeholder)');
      
    } catch (err) {
      console.error('❌ Error deleting document:', err);
      setError('Failed to delete document. Please try again.');
    }
  };

  const handleDeleteAccount = () => {
    // Open the delete account modal
    setShowDeleteModal(true);
    setDeleteStep(1);
    setDeletePassword('');
    setPasswordError('');
  };

  const handleCloseDeleteModal = () => {
    setShowDeleteModal(false);
    setDeleteStep(1);
    setDeletePassword('');
    setPasswordError('');
    setPasswordVerifying(false);
  };

  const handleVerifyPassword = async () => {
    if (!deletePassword.trim()) {
      setPasswordError('Please enter your password');
      return;
    }

    try {
      setPasswordVerifying(true);
      setPasswordError('');
      
      console.log('🔐 Verifying password...');
      console.log('👤 User object:', user);
      console.log('📧 User email:', user?.email || userProfile?.email);
      
      // Get authentication token
      const token = localStorage.getItem('medichain_token');
      if (!token) {
        setPasswordError('Authentication token not found. Please log in again.');
        return;
      }

      // Get email from user object or profile
      const userEmail = user?.email || userProfile?.email || profile?.email;
      
      if (!userEmail) {
        setPasswordError('Email not found. Please log in again.');
        return;
      }

      console.log('📤 Sending verification request with email:', userEmail);

      // Verify password by attempting to re-authenticate
      const response = await fetch('http://localhost:5000/api/auth/verify-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          email: userEmail,
          password: deletePassword
        })
      });

      const result = await response.json();
      console.log('📥 Verification response:', result);
      
      if (result.success) {
        console.log('✅ Password verified successfully!');
        // Move to confirmation step
        setDeleteStep(2);
        setPasswordError('');
      } else {
        const errorMsg = result.error || 'Incorrect password. Please try again.';
        setPasswordError(errorMsg);
        console.log('❌ Password verification failed:', errorMsg);
      }
    } catch (err) {
      console.error('❌ Error verifying password:', err);
      setPasswordError('Failed to verify password. Please try again.');
    } finally {
      setPasswordVerifying(false);
    }
  };

  const handleConfirmDelete = async () => {
    try {
      setSaving(true);
      setError('');
      
      console.log('🗑️ Deleting user account...');
      
      // Get authentication token
      const token = localStorage.getItem('medichain_token');
      if (!token) {
        setError('Authentication token not found. Please log in again.');
        return;
      }

      // Call backend API to delete account
      const response = await fetch('http://localhost:5000/api/profile/delete-account', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      const result = await response.json();
      
      if (result.success) {
        // Clear local storage
        localStorage.removeItem('medichain_token');
        localStorage.removeItem('medichain_user');
        
        // Close modal
        handleCloseDeleteModal();
        
        // Show success message
        setSuccess('✅ Your account has been successfully deleted.');
        
        // Redirect to home page after a short delay
        setTimeout(() => {
          window.location.href = '/';
        }, 2000);
        
        console.log('✅ Account deleted successfully!');
      } else {
        setError(result.error || 'Failed to delete account. Please try again.');
        console.log('❌ Account deletion failed:', result.error);
        handleCloseDeleteModal();
      }
    } catch (err) {
      console.error('❌ Error deleting account:', err);
      setError('Failed to delete account. Please try again or contact support.');
      handleCloseDeleteModal();
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

  // Use profile directly since we're setting it correctly in loadProfile
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
              <h1 className="profile-header-title">Patient Profile Management</h1>
            </div>
            <div className="profile-header-right">
              <div className="profile-welcome-text">
                Welcome, {userProfile.first_name || user?.first_name || user?.displayName?.split(' ')[0] || 'User'}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="profile-main-container">
        {/* Profile Header */}
        <div className="profile-card-header">
          <div className="profile-card-content">
            <div className="profile-card-left">
              <div className="profile-avatar-container">
                <div className="profile-avatar">
                  {userProfile.avatar_url ? (
                    <img 
                      src={userProfile.avatar_url} 
                      alt="Avatar" 
                    />
                  ) : (
                    <span>
                      {userProfile.first_name?.charAt(0)?.toUpperCase() || 'U'}
                    </span>
                  )}
                </div>
                <label className="profile-avatar-upload">
                  <Camera size={16} />
                  <span className="profile-avatar-upload-label">Upload Photo</span>
                  <input
                    type="file"
                    accept="image/*"
                  />
                </label>
              </div>
              <div className="profile-info">
                <h2 className="profile-name">
                  {userProfile.first_name || 'Loading...'} {userProfile.last_name || ''}
                </h2>
                <p className="profile-role">{userProfile.role || 'Patient'}</p>
                {userProfile.patient_id && (
                  <p className="profile-specialization">Patient ID: {userProfile.patient_id}</p>
                )}
              </div>
            </div>
            <div className="profile-card-actions">
              {editing ? (
                <>
                  <button
                    onClick={handlePersonalInfoUpdate}
                    disabled={saving}
                    className="profile-btn profile-btn-success"
                  >
                    {saving ? (
                      <>
                        <div className="profile-btn-spinner"></div>
                        <span>Saving...</span>
                      </>
                    ) : (
                      <>
                        <Save size={18} />
                        <span>Save Changes</span>
                      </>
                    )}
                  </button>
                  <button
                    onClick={() => setEditing(false)}
                    className="profile-btn profile-btn-secondary"
                  >
                    <X size={18} />
                    <span>Cancel</span>
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setEditing(true)}
                  className="profile-btn profile-btn-primary"
                >
                  <Edit3 size={18} />
                  <span>Edit Profile</span>
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Success/Error Messages */}
        {success && (
          <div className="profile-alert profile-alert-success">
            <CheckCircle size={20} />
            {success}
          </div>
        )}
        {error && (
          <div className="profile-alert profile-alert-error">
            <AlertCircle size={20} />
            {error}
          </div>
        )}

        {/* Tab Navigation */}
        <div className="profile-tab-container">
          <div className="profile-tab-navigation">
            <nav className="profile-tab-nav-list">
              {[
                { id: 'personal', label: 'Personal Info', icon: User },
                { id: 'medical', label: 'Medical Records', icon: Heart },
                { id: 'documents', label: 'Health Documents', icon: FileText },
                { id: 'privacy', label: 'Privacy Settings', icon: Lock },
                { id: 'credentials', label: 'Account Security', icon: Key },
                { id: 'audit', label: 'Health History', icon: History }
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
            {activeTab === 'personal' && (
              <div className="profile-tab-section">
                <h3 className="profile-tab-title">Personal Information</h3>
                
                <div className="profile-form-grid">
                  <div className="profile-form-group">
                    <label className="profile-form-label">First Name</label>
                    <input
                      type="text"
                      value={formData.first_name}
                      onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                      disabled={!editing}
                      className="profile-form-input"
                      placeholder="Enter your first name"
                    />
                  </div>
                  
                  <div className="profile-form-group">
                    <label className="profile-form-label">Last Name</label>
                    <input
                      type="text"
                      value={formData.last_name}
                      onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                      disabled={!editing}
                      className="profile-form-input"
                      placeholder="Enter your last name"
                    />
                  </div>
                  
                  <div className="profile-form-group">
                    <label className="profile-form-label">Phone Number</label>
                    <input
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => setFormData({...formData, phone: e.target.value})}
                      disabled={!editing}
                      className="profile-form-input"
                      placeholder="Enter your phone number"
                    />
                  </div>
                  
                  <div className="profile-form-group">
                    <label className="profile-form-label">Email</label>
                    <input
                      type="email"
                      value={formData.email}
                      disabled={true}
                      className="profile-form-input"
                      placeholder="Email cannot be changed"
                    />
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'credentials' && (
              <div className="profile-tab-section">
                <h3 className="profile-tab-title">Account Security</h3>
                
                <div className="profile-credentials-info">
                  <h4>Account Information</h4>
                  <div className="profile-credentials-details">
                    <p><strong>Email:</strong> {userProfile.email || 'Not available'}</p>
                    <p><strong>Role:</strong> {userProfile.role || 'Not available'}</p>
                    <p><strong>Member since:</strong> {userProfile.created_at ? new Date(userProfile.created_at).toLocaleDateString() : 'Not available'}</p>
                  </div>
                </div>
                
                <div className="profile-credentials-security-notice">
                  <h4>Security Notice</h4>
                  <p>
                    For security reasons, password changes must be done through Firebase Authentication. 
                    Your health information is protected with enterprise-grade security. 
                    Contact support if you need assistance with account security.
                  </p>
                </div>

                <div className="profile-credentials-actions">
                  <div className="profile-credential-action">
                    <div className="profile-credential-info">
                      <h4>Email Address</h4>
                      <p>Update your email address</p>
                    </div>
                    <button className="profile-btn profile-btn-primary">
                      Update Email
                    </button>
                  </div>

                  <div className="profile-credential-action">
                    <div className="profile-credential-info">
                      <h4>Password</h4>
                      <p>Change your password</p>
                    </div>
                    <button className="profile-btn profile-btn-primary">
                      Change Password
                    </button>
                  </div>

                  <div className="profile-credential-action">
                    <div className="profile-credential-info">
                      <h4>Two-Factor Authentication</h4>
                      <p>Add an extra layer of security</p>
                    </div>
                    <button className="profile-btn profile-btn-success">
                      Enable 2FA
                    </button>
                  </div>
                </div>

                {/* Delete Account Section */}
                <div className="profile-danger-zone">
                  <h4 className="profile-danger-zone-title">Danger Zone</h4>
                  <div className="profile-danger-zone-content">
                    <div className="profile-danger-warning">
                      <AlertCircle size={20} />
                      <div>
                        <p className="profile-danger-warning-title">Delete Account</p>
                        <p className="profile-danger-warning-text">
                          Once you delete your account, there is no going back. This will permanently delete all your medical records, 
                          appointments, prescriptions, and personal information. Please be certain.
                        </p>
                      </div>
                    </div>
                    <button 
                      onClick={handleDeleteAccount}
                      disabled={saving}
                      className="profile-btn profile-btn-danger"
                    >
                      <Trash2 size={16} />
                      {saving ? 'Deleting...' : 'Delete Account'}
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Other tabs can be added here */}
            {activeTab === 'medical' && (
              <div className="profile-tab-section">
                <div className="profile-documents-empty">
                  <Heart size={64} className="profile-documents-empty-icon" />
                  <p className="text-lg">Medical Records</p>
                  <p>View your medical history, conditions, allergies, and medications</p>
                </div>
              </div>
            )}

            {activeTab === 'documents' && (
              <div className="profile-tab-section">
                <div className="profile-documents-empty">
                  <FileText size={64} className="profile-documents-empty-icon" />
                  <p className="text-lg">Health Documents</p>
                  <p>Upload and manage your medical certificates, prescriptions, and reports</p>
                </div>
              </div>
            )}

            {activeTab === 'privacy' && (
              <div className="profile-tab-section">
                <div className="profile-documents-empty">
                  <Lock size={64} className="profile-documents-empty-icon" />
                  <p className="text-lg">Privacy Settings</p>
                  <p>Control who can access your health information and medical records</p>
                </div>
              </div>
            )}

            {activeTab === 'audit' && (
              <div className="profile-tab-section">
                <div className="profile-audit-trail-empty">
                  <History size={64} className="profile-audit-trail-empty-icon" />
                  <p className="text-lg">Health History</p>
                  <p>Track all changes to your medical records and profile information</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Delete Account Modal */}
      {showDeleteModal && (
        <div className="profile-modal-overlay" onClick={handleCloseDeleteModal}>
          <div className="profile-modal-content profile-delete-modal" onClick={(e) => e.stopPropagation()}>
            <button className="profile-modal-close" onClick={handleCloseDeleteModal}>
              <X size={24} />
            </button>

            {deleteStep === 1 ? (
              /* Step 1: Password Verification */
              <>
                <div className="profile-modal-header">
                  <AlertCircle size={48} className="profile-modal-icon-warning" />
                  <h2>Verify Your Identity</h2>
                  <p>Please enter your password to continue with account deletion</p>
                </div>

                <div className="profile-modal-body">
                  <div className="profile-modal-warning-box">
                    <AlertCircle size={20} />
                    <div>
                      <p className="profile-modal-warning-title">⚠️ This action is irreversible</p>
                      <p className="profile-modal-warning-text">
                        Deleting your account will permanently remove:
                      </p>
                      <ul className="profile-modal-warning-list">
                        <li>All your medical records and history</li>
                        <li>Appointments and prescriptions</li>
                        <li>Uploaded health documents</li>
                        <li>Privacy settings and preferences</li>
                        <li>Your entire account from the system</li>
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
                      value={deletePassword}
                      onChange={(e) => setDeletePassword(e.target.value)}
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
                    onClick={handleCloseDeleteModal}
                    className="profile-btn profile-btn-secondary"
                    disabled={passwordVerifying}
                  >
                    Cancel
                  </button>
                  <button 
                    onClick={handleVerifyPassword}
                    className="profile-btn profile-btn-primary"
                    disabled={passwordVerifying || !deletePassword.trim()}
                  >
                    {passwordVerifying ? 'Verifying...' : 'Verify Password'}
                  </button>
                </div>
              </>
            ) : (
              /* Step 2: Final Confirmation */
              <>
                <div className="profile-modal-header">
                  <AlertCircle size={48} className="profile-modal-icon-danger" />
                  <h2>Final Confirmation</h2>
                  <p>Are you absolutely sure you want to delete your account?</p>
                </div>

                <div className="profile-modal-body">
                  <div className="profile-modal-danger-box">
                    <h3>⚠️ This Will Permanently Delete:</h3>
                    <div className="profile-modal-delete-list">
                      <div className="profile-modal-delete-item">
                        <CheckCircle size={20} />
                        <span>All medical records and health history</span>
                      </div>
                      <div className="profile-modal-delete-item">
                        <CheckCircle size={20} />
                        <span>All appointments and prescriptions</span>
                      </div>
                      <div className="profile-modal-delete-item">
                        <CheckCircle size={20} />
                        <span>All uploaded health documents</span>
                      </div>
                      <div className="profile-modal-delete-item">
                        <CheckCircle size={20} />
                        <span>Your account and authentication credentials</span>
                      </div>
                      <div className="profile-modal-delete-item">
                        <CheckCircle size={20} />
                        <span>All privacy settings and preferences</span>
                      </div>
                    </div>
                    <p className="profile-modal-danger-text">
                      <strong>This action cannot be undone.</strong> Your data will be permanently removed from our systems.
                    </p>
                  </div>
                </div>

                <div className="profile-modal-footer">
                  <button 
                    onClick={handleCloseDeleteModal}
                    className="profile-btn profile-btn-success"
                    disabled={saving}
                  >
                    No, Keep My Account
                  </button>
                  <button 
                    onClick={handleConfirmDelete}
                    className="profile-btn profile-btn-danger"
                    disabled={saving}
                  >
                    <Trash2 size={16} />
                    {saving ? 'Deleting Account...' : 'Yes, Delete My Account'}
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

export default ProfilePage;

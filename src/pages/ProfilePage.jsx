import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { SupabaseService } from '../config/supabase';
import { 
  User, Heart, FileText, Lock, Key, History, 
  Edit3, Save, X, Camera,
  AlertCircle, CheckCircle, ArrowLeft
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

  const [privacySettings] = useState({
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

  // eslint-disable-next-line no-unused-vars
  const [documents, setDocuments] = useState([]);
  // eslint-disable-next-line no-unused-vars
  const [uploading, setUploading] = useState(false);
  const [saving, setSaving] = useState(false);
  // eslint-disable-next-line no-unused-vars
  const [auditTrail, setAuditTrail] = useState([]);

  const loadProfile = useCallback(async () => {
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
  }, [user]);

  useEffect(() => {
    if (user) {
      loadProfile();
    }
  }, [user, loadProfile]);

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

  // eslint-disable-next-line no-unused-vars
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

  // eslint-disable-next-line no-unused-vars
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

  // eslint-disable-next-line no-unused-vars
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

  // eslint-disable-next-line no-unused-vars
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
    </div>
  );
};

export default ProfilePage;

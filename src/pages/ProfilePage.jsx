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
  // Per-section edit modes for a more interactive UX
  const [editingPersonal, setEditingPersonal] = useState(false);
  const [editingMedical, setEditingMedical] = useState(false);
  const [editingPrivacy, setEditingPrivacy] = useState(false);
  const [editingDocuments, setEditingDocuments] = useState(false);
  const [activeTab, setActiveTab] = useState('personal');
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    email: '',
    date_of_birth: '',
    gender: '',
    avatar_url: null,
    address: {
      street: '',
      brgy: '',
      city: '',
      region: ''
    }
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
  const [avatarFile, setAvatarFile] = useState(null);

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
        date_of_birth: profile.date_of_birth || user.date_of_birth || '',
        gender: profile.gender || user.gender || '',
        role: profile.role || user.role || 'patient',
        patient_id: profile.patient_id || user.patient_id || user.uid || null,
        avatar_url: profile.avatar_url || user.avatar_url || user.photoURL || null,
        address: profile.address || user.address || { street: '', brgy: '', city: '', region: '' },
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
      
      // Ensure we have basic fallback values if nothing else provided
      if (!userData.first_name) {
        userData = { ...createBasicFallback(user), ...userData };
      }

      // patient_id should be created during signup and returned by the backend.
      // If it's missing here, log a warning (don't generate it in the profile page).
      if (!userData.patient_id) {
        console.warn('⚠️ No patient_id found for user. Ensure the backend returns the patient_id created during signup.');
      }
      
      console.log('🎯 Final user data:', userData);
      
      setProfile(userData);
      setFormData({
        first_name: userData.first_name,
        last_name: userData.last_name,
        phone: userData.phone,
        email: userData.email,
        date_of_birth: userData.date_of_birth || '',
        gender: userData.gender || '',
        avatar_url: userData.avatar_url || null,
        address: userData.address || { street: '', brgy: '', city: '', region: '' }
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

  const handlePersonalInfoUpdate = async () => {
    try {
      setSaving(true);
      setError('');
      
      console.log('💾 Updating personal info via backend API...');
      
      const updateData = {
        first_name: formData.first_name,
        last_name: formData.last_name,
        phone: formData.phone,
        role: profile?.role || 'patient',
        date_of_birth: formData.date_of_birth,
        gender: formData.gender,
        avatar_url: formData.avatar_url,
        address: formData.address
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
          phone: updateData.phone,
          date_of_birth: updateData.date_of_birth,
          gender: updateData.gender,
          avatar_url: updateData.avatar_url,
          address: updateData.address
        });
  setSuccess('Personal information updated successfully!');
  setEditingPersonal(false);
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

  const handleAvatarChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setAvatarFile(file);
    // Local preview - actual upload handled elsewhere
    const preview = URL.createObjectURL(file);
    setFormData({...formData, avatar_url: preview});
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
  setEditingMedical(false);
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
        setEditingPrivacy(false);
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
                    onChange={handleAvatarChange}
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
              {editingPersonal ? (
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
                        <span>Save</span>
                      </>
                    )}
                  </button>
                  <button
                    onClick={() => setEditingPersonal(false)}
                    className="profile-btn profile-btn-secondary"
                  >
                    <X size={18} />
                    <span>Cancel</span>
                  </button>
                </>
              ) : (
                <div className="profile-card-mini-actions">
                  <button onClick={() => setEditingPersonal(true)} className="profile-btn profile-btn-primary">
                    <Edit3 size={16} />
                    <span>Edit</span>
                  </button>
                </div>
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
                        disabled={!editingPersonal}
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
                        disabled={!editingPersonal}
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
                        disabled={!editingPersonal}
                        className="profile-form-input"
                      placeholder="Enter your phone number"
                    />
                  </div>
                  
                  <div className="profile-form-group">
                    <label className="profile-form-label">Date of Birth</label>
                    <input
                      type="date"
                        value={formData.date_of_birth}
                        onChange={(e) => setFormData({...formData, date_of_birth: e.target.value})}
                        disabled={!editingPersonal}
                        className="profile-form-input"
                    />
                  </div>

                  <div className="profile-form-group">
                    <label className="profile-form-label">Gender</label>
                    <select value={formData.gender} onChange={(e) => setFormData({...formData, gender: e.target.value})} disabled={!editingPersonal} className="profile-form-input">
                      <option value="">Select</option>
                      <option value="female">Female</option>
                      <option value="male">Male</option>
                      <option value="other">Other</option>
                      <option value="prefer_not_to_say">Prefer not to say</option>
                    </select>
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
                  
                  <div className="profile-form-group profile-address-group">
                    <label className="profile-form-label">Address</label>
                    <input type="text" placeholder="Street" value={formData.address.street} onChange={(e) => setFormData({...formData, address: {...formData.address, street: e.target.value}})} className="profile-form-input" disabled={!editingPersonal} />
                    <input type="text" placeholder="Brgy" value={formData.address.brgy} onChange={(e) => setFormData({...formData, address: {...formData.address, brgy: e.target.value}})} className="profile-form-input" disabled={!editingPersonal} />
                    <input type="text" placeholder="City" value={formData.address.city} onChange={(e) => setFormData({...formData, address: {...formData.address, city: e.target.value}})} className="profile-form-input" disabled={!editingPersonal} />
                    <input type="text" placeholder="Region (e.g. Metro Manila)" value={formData.address.region} onChange={(e) => setFormData({...formData, address: {...formData.address, region: e.target.value}})} className="profile-form-input" disabled={!editingPersonal} />
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
                <h3 className="profile-tab-title">Medical Records</h3>

                <div className="profile-form-grid">
                  <div className="profile-form-group">
                    <label className="profile-form-label">Medical Conditions (comma separated)</label>
                    <input
                      type="text"
                      value={medicalInfo.medical_conditions.join(', ')}
                      onChange={(e) => setMedicalInfo({...medicalInfo, medical_conditions: e.target.value.split(',').map(s => s.trim()).filter(Boolean)})}
                      className="profile-form-input"
                      placeholder="e.g. Diabetes, Hypertension"
                      disabled={!editingMedical}
                    />
                  </div>

                  <div className="profile-form-group">
                    <label className="profile-form-label">Allergies (comma separated)</label>
                    <input
                      type="text"
                      value={medicalInfo.allergies.join(', ')}
                      onChange={(e) => setMedicalInfo({...medicalInfo, allergies: e.target.value.split(',').map(s => s.trim()).filter(Boolean)})}
                      className="profile-form-input"
                      placeholder="e.g. Penicillin"
                      disabled={!editingMedical}
                    />
                  </div>

                  <div className="profile-form-group">
                    <label className="profile-form-label">Current Medications (comma separated)</label>
                    <input
                      type="text"
                      value={medicalInfo.current_medications.join(', ')}
                      onChange={(e) => setMedicalInfo({...medicalInfo, current_medications: e.target.value.split(',').map(s => s.trim()).filter(Boolean)})}
                      className="profile-form-input"
                      placeholder="e.g. Metformin"
                      disabled={!editingMedical}
                    />
                  </div>

                  <div className="profile-form-group">
                    <label className="profile-form-label">Blood Type</label>
                    <input
                      type="text"
                      value={medicalInfo.blood_type}
                      onChange={(e) => setMedicalInfo({...medicalInfo, blood_type: e.target.value})}
                      className="profile-form-input"
                      placeholder="e.g. O+"
                      disabled={!editingMedical}
                    />
                  </div>

                  <div className="profile-form-group">
                    <label className="profile-form-label">Medical Notes</label>
                    <textarea
                      value={medicalInfo.medical_notes}
                      onChange={(e) => setMedicalInfo({...medicalInfo, medical_notes: e.target.value})}
                      className="profile-form-input"
                      placeholder="Any important notes"
                      disabled={!editingMedical}
                    />
                  </div>
                </div>

                <div className="profile-tab-actions">
                  {editingMedical ? (
                    <>
                      <button onClick={handleMedicalInfoUpdate} className="profile-btn profile-btn-success" disabled={saving}>{saving ? 'Saving...' : 'Save'}</button>
                      <button onClick={() => setEditingMedical(false)} className="profile-btn profile-btn-secondary">Cancel</button>
                    </>
                    ) : (
                    <>
                      <button onClick={() => setEditingMedical(true)} className="profile-btn profile-btn-primary">Edit</button>
                    </>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'documents' && (
              <div className="profile-tab-section">
                <h3 className="profile-tab-title">Health Documents</h3>

                <div className="profile-documents-actions">
                  {editingDocuments ? (
                    <label className="profile-file-upload">
                      <input type="file" accept="application/pdf,image/*" onChange={handleDocumentUpload} />
                      <span>Choose file to upload</span>
                    </label>
                  ) : (
                    <div className="profile-documents-controls">
                      <button onClick={() => setEditingDocuments(true)} className="profile-btn profile-btn-primary">Upload</button>
                    </div>
                  )}
                </div>

                <div className="profile-documents-list">
                  {documents.length === 0 ? (
                    <div className="profile-documents-empty">
                      <FileText size={64} className="profile-documents-empty-icon" />
                      <p className="text-lg">No documents uploaded</p>
                      <p>You can upload medical certificates, prescriptions, and reports</p>
                    </div>
                  ) : (
                    <ul>
                      {documents.map((doc) => (
                        <li key={doc.id || doc.name} className="profile-document-item">
                          <a href={doc.url} target="_blank" rel="noreferrer">{doc.name || doc.filename || 'Document'}</a>
                          <button onClick={() => handleDocumentDelete(doc.id)} className="profile-btn profile-btn-secondary">Delete</button>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'privacy' && (
              <div className="profile-tab-section">
                <h3 className="profile-tab-title">Privacy Settings</h3>

                <div className="profile-form-grid">
                  <div className="profile-form-group">
                    <label className="profile-form-label">Profile Visibility</label>
                    <select value={privacySettings.profile_visibility} onChange={(e) => setPrivacySettings({...privacySettings, profile_visibility: e.target.value})} className="profile-form-input">
                      <option value="private">Private</option>
                      <option value="doctors">Visible to Doctors</option>
                      <option value="public">Public</option>
                    </select>
                  </div>

                  <div className="profile-form-group">
                    <label className="profile-form-label">Allow AI Analysis</label>
                    <input type="checkbox" checked={privacySettings.allow_ai_analysis} onChange={(e) => setPrivacySettings({...privacySettings, allow_ai_analysis: e.target.checked})} disabled={!editingPrivacy} />
                  </div>

                  <div className="profile-form-group">
                    <label className="profile-form-label">Share Data for Research</label>
                    <input type="checkbox" checked={privacySettings.share_data_for_research} onChange={(e) => setPrivacySettings({...privacySettings, share_data_for_research: e.target.checked})} disabled={!editingPrivacy} />
                  </div>
                </div>

                <div className="profile-tab-actions">
                  {editingPrivacy ? (
                    <>
                      <button onClick={handlePrivacySettingsUpdate} className="profile-btn profile-btn-success" disabled={saving}>{saving ? 'Saving...' : 'Save'}</button>
                      <button onClick={() => setEditingPrivacy(false)} className="profile-btn profile-btn-secondary">Cancel</button>
                    </>
                  ) : (
                    <>
                      <button onClick={() => setEditingPrivacy(true)} className="profile-btn profile-btn-primary">Edit</button>
                    </>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'audit' && (
              <div className="profile-tab-section">
                <h3 className="profile-tab-title">Health History</h3>

                {auditTrail.length === 0 ? (
                  <div className="profile-audit-trail-empty">
                    <History size={64} className="profile-audit-trail-empty-icon" />
                    <p className="text-lg">No audit entries</p>
                    <p>Changes to your profile and medical records will appear here</p>
                  </div>
                ) : (
                  <ul className="profile-audit-list">
                    {auditTrail.map((entry, idx) => (
                      <li key={entry.id || idx} className="profile-audit-item">
                        <div className="profile-audit-meta">{entry.action} — {entry.timestamp ? new Date(entry.timestamp).toLocaleString() : 'Unknown time'}</div>
                        <div className="profile-audit-details">{entry.details}</div>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;

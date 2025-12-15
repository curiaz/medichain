import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  User, Heart, FileText, Lock, Shield, Edit3, Save, X, AlertCircle, 
  CheckCircle, ArrowLeft, Upload, Trash2, Eye, CreditCard
} from 'lucide-react';
import './ProfilePage.css';

const ProfilePage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [activeTab, setActiveTab] = useState('personal');
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  
  // Personal Info State
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    email: '',
    date_of_birth: '',
    gender: '',
    address: '',
    city: '',
    state: '',
    zip_code: ''
  });

  // Medical Info State
  const [medicalInfo, setMedicalInfo] = useState({
    medical_conditions: [],
    allergies: [],
    current_medications: [],
    blood_type: '',
    medical_notes: ''
  });

  // Documents State
  const [documents, setDocuments] = useState([]);
  
  // Payment History State
  const [paymentHistory, setPaymentHistory] = useState([]);
  const [paymentHistoryLoading, setPaymentHistoryLoading] = useState(false);

  // Privacy Settings State
  const [privacySettings, setPrivacySettings] = useState({
    profile_visibility: 'private',
    show_email: false,
    show_phone: false,
    medical_info_visible_to_doctors: true,
    allow_ai_analysis: true,
    share_data_for_research: false
  });

  // Account Security States
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteStep, setDeleteStep] = useState(1);
  const [deletePassword, setDeletePassword] = useState('');
  const [passwordVerifying, setPasswordVerifying] = useState(false);
  const [passwordError, setPasswordError] = useState('');

  // Redirect doctors to doctor profile
  useEffect(() => {
    if (user?.role === 'doctor') {
      navigate('/doctor-profile');
    }
  }, [user, navigate]);

  useEffect(() => {
    if (user) {
      loadProfile();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);
  
  // Fetch payment history when payment history tab is active
  useEffect(() => {
    if (activeTab === 'payments' && user) {
      fetchPaymentHistory();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab, user]);

  const loadProfile = async (skipRedirect = false) => {
    try {
      setLoading(true);
      console.log('🔍 Loading patient profile, user object:', user);
      
      if (!user && !skipRedirect) {
        console.error('❌ No user found, redirecting to login');
        navigate('/login');
        return;
      }

      // If user is available, use it first (fast)
      if (user) {
        // Load personal info
        setFormData({
          first_name: user.first_name || '',
          last_name: user.last_name || '',
          phone: user.phone || '',
          email: user.email || '',
          date_of_birth: user.date_of_birth || '',
          gender: user.gender || '',
          address: user.address || '',
          city: user.city || '',
          state: user.state || '',
          zip_code: user.zip_code || ''
        });

        // Load medical info
        setMedicalInfo({
          medical_conditions: user.medical_conditions || [],
          allergies: user.allergies || [],
          current_medications: user.current_medications || [],
          blood_type: user.blood_type || '',
          medical_notes: user.medical_notes || ''
        });

        // Load privacy settings
        setPrivacySettings({
          profile_visibility: user.profile_visibility || 'private',
          show_email: user.show_email || false,
          show_phone: user.show_phone || false,
          medical_info_visible_to_doctors: user.medical_info_visible_to_doctors !== false,
          allow_ai_analysis: user.allow_ai_analysis !== false,
          share_data_for_research: user.share_data_for_research || false
        });
      }

      // Fetch fresh data from backend
      const token = localStorage.getItem('medichain_token');
      if (token) {
        try {
          const response = await fetch('https://medichainn.onrender.com/api/profile/patient', {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          if (response.ok) {
            const result = await response.json();
            if (result.success && result.profile) {
              const profileData = result.profile.user_profile || result.profile;
              
              // Update form data with fresh backend data
              setFormData({
                first_name: profileData.first_name || '',
                last_name: profileData.last_name || '',
                phone: profileData.phone || '',
                email: profileData.email || '',
                date_of_birth: profileData.date_of_birth || '',
                gender: profileData.gender || '',
                address: profileData.address || '',
                city: profileData.city || '',
                state: profileData.state || '',
                zip_code: profileData.zip_code || ''
              });

              // Update medical info with fresh backend data
              const medicalData = result.profile.medical_info || {};
              setMedicalInfo({
                medical_conditions: profileData.medical_conditions || medicalData.medical_conditions || [],
                allergies: profileData.allergies || medicalData.allergies || [],
                current_medications: profileData.current_medications || medicalData.current_medications || [],
                blood_type: profileData.blood_type || medicalData.blood_type || '',
                medical_notes: profileData.medical_notes || medicalData.medical_notes || ''
              });

              // Update privacy settings with fresh backend data
              const privacyData = result.profile.privacy_settings || {};
              setPrivacySettings({
                profile_visibility: profileData.profile_visibility || privacyData.profile_visibility || 'private',
                show_email: profileData.show_email !== undefined ? profileData.show_email : (privacyData.show_email || false),
                show_phone: profileData.show_phone !== undefined ? profileData.show_phone : (privacyData.show_phone || false),
                medical_info_visible_to_doctors: profileData.medical_info_visible_to_doctors !== false,
                allow_ai_analysis: profileData.allow_ai_analysis !== false,
                share_data_for_research: profileData.share_data_for_research || false
              });
            }
          }
        } catch (fetchErr) {
          console.warn('⚠️  Could not fetch fresh profile data from backend, using cached data:', fetchErr);
          // Continue with cached user data if backend fetch fails
        }
      }

      console.log('✅ Profile loaded successfully');
      setLoading(false);
    } catch (err) {
      console.error('❌ Error loading profile:', err);
      if (!skipRedirect) {
        setError('Failed to load profile');
      }
      setLoading(false);
    }
  };

  const fetchPaymentHistory = async () => {
    try {
      setPaymentHistoryLoading(true);
      const token = localStorage.getItem('medichain_token');
      if (!token) {
        setError('Please log in again');
        return;
      }

      const response = await fetch('https://medichainn.onrender.com/api/appointments/payments', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const result = await response.json();
      
      if (result.success) {
        setPaymentHistory(result.payments || []);
      } else {
        setError(result.error || 'Failed to load payment history');
        setPaymentHistory([]);
      }
    } catch (err) {
      console.error('Error fetching payment history:', err);
      setError('Failed to load payment history. Please try again.');
      setPaymentHistory([]);
    } finally {
      setPaymentHistoryLoading(false);
    }
  };

  const handleSavePersonalInfo = async () => {
    try {
      setSaving(true);
      setError('');
      
      const token = localStorage.getItem('medichain_token');
      if (!token) {
        setError('Please log in again');
        return;
      }

      console.log('📤 Sending profile update request:', formData);
      
      const response = await fetch('https://medichainn.onrender.com/api/profile/patient/update', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      const result = await response.json();
      console.log('📥 Profile update response:', result);
      
      if (result.success) {
        setSuccess('Personal information updated successfully!');
        setEditing(false);
        
        // Reload profile data from backend without full page reload
        setTimeout(() => {
          loadProfile(true); // Pass skipRedirect=true to prevent redirect on refresh
        }, 500);
      } else {
        console.error('❌ Profile update failed:', result.error);
        setError(result.error || 'Failed to update');
      }
    } catch (err) {
      console.error('Error updating:', err);
      setError('Failed to update. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleSaveMedicalInfo = async () => {
    try {
      setSaving(true);
      setError('');
      
      const token = localStorage.getItem('medichain_token');
      if (!token) {
        setError('Please log in again');
        return;
      }

      const response = await fetch('https://medichainn.onrender.com/api/profile/patient/medical', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(medicalInfo)
      });

      const result = await response.json();
      
      if (result.success) {
        setSuccess('Medical information updated successfully!');
        setEditing(false);
        setTimeout(() => setSuccess(''), 3000);
      } else {
        setError(result.error || 'Failed to update medical information');
      }
    } catch (err) {
      console.error('Error updating medical info:', err);
      setError('Failed to update. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleDocumentUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    try {
      setUploading(true);
      setError('');

      const token = localStorage.getItem('medichain_token');
      if (!token) {
        setError('Please log in again');
        return;
      }

      const formData = new FormData();
      formData.append('file', file);
      formData.append('document_type', 'health_document');
      formData.append('description', file.name);

      const response = await fetch('https://medichainn.onrender.com/api/profile/patient/documents', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      const result = await response.json();
      
      if (result.success) {
        setSuccess('Document uploaded successfully!');
        setDocuments([...documents, result.data]);
        setTimeout(() => setSuccess(''), 3000);
      } else {
        setError(result.error || 'Failed to upload document');
      }
    } catch (err) {
      console.error('Error uploading document:', err);
      setError('Failed to upload. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleSavePrivacySettings = async () => {
    try {
      setSaving(true);
      setError('');
      
      const token = localStorage.getItem('medichain_token');
      if (!token) {
        setError('Please log in again');
        return;
      }

      console.log('Saving privacy settings:', privacySettings);

      const response = await fetch('https://medichainn.onrender.com/api/profile/patient/privacy', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(privacySettings)
      });

      const result = await response.json();
      console.log('Privacy settings response:', result);
      
      if (result.success) {
        setSuccess('Privacy settings updated successfully!');
        setTimeout(() => setSuccess(''), 3000);
      } else {
        console.error('Privacy settings error:', result.error);
        setError(result.error || 'Failed to update privacy settings');
      }
    } catch (err) {
      console.error('Error updating privacy settings:', err);
      setError(`Failed to update: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  // eslint-disable-next-line no-unused-vars
  const handleAvatarUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('Please select an image file');
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('Image size must be less than 5MB');
      return;
    }

    try {
      setUploading(true);
      setError('');
      
      console.log('📷 Uploading avatar...');
      
      // Convert image to base64
      const reader = new FileReader();
      reader.onloadend = async () => {
        try {
          const base64String = reader.result;
          
          // Send to backend
          const token = localStorage.getItem('medichain_token');
          if (!token) {
            setError('Authentication token not found. Please log in again.');
            return;
          }

          const updateData = {
            firebase_uid: user.uid || user.profile?.firebase_uid,
            avatar_url: base64String
          };

          console.log('📤 Sending avatar update:', {
            firebase_uid: updateData.firebase_uid,
            avatar_url_length: base64String?.length,
            avatar_url_preview: base64String?.substring(0, 50)
          });

          const response = await fetch('http://localhost:5000/api/profile/patient/update', {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ avatar_url: base64String })
          });

          console.log('📥 Backend response status:', response.status);
          console.log('📥 Backend response headers:', response.headers);

          const result = await response.json();
          
          if (result.success) {
            // Reload profile to get updated data
            loadProfile(true);
            setSuccess('Profile photo updated successfully!');
            setTimeout(() => setSuccess(''), 3000);
            console.log('✅ Avatar uploaded successfully!');
          } else {
            setError(result.error || 'Failed to upload photo');
            console.log('❌ Backend upload failed:', result.error);
          }
        } catch (err) {
          console.error('❌ Error uploading avatar:', err);
          setError('Failed to upload photo. Please try again.');
        } finally {
          setUploading(false);
        }
      };
      
      reader.onerror = () => {
        setError('Failed to read image file');
        setUploading(false);
      };
      
      reader.readAsDataURL(file);
      
    } catch (err) {
      console.error('❌ Error uploading avatar:', err);
      setError('Failed to upload photo. Please try again.');
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

  // eslint-disable-next-line no-unused-vars
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
    try {
      setPasswordVerifying(true);
      setPasswordError('');
      
      const token = localStorage.getItem('medichain_token');
      if (!token) {
        setPasswordError('Authentication token not found. Please log in again.');
        return;
      }

      const response = await fetch('https://medichainn.onrender.com/api/auth/verify-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          email: user?.email,
          password: deletePassword
        })
      });

      const result = await response.json();
      
      if (result.success) {
        setDeleteStep(2);
        setPasswordError('');
      } else {
        setPasswordError(result.error || 'Incorrect password. Please try again.');
      }
    } catch (err) {
      console.error('Error verifying password:', err);
      setPasswordError('Failed to verify password. Please try again.');
    } finally {
      setPasswordVerifying(false);
    }
  };

  const handleConfirmDelete = async () => {
    try {
      setSaving(true);
      setError('');
      
      const token = localStorage.getItem('medichain_token');
      if (!token) {
        setError('Authentication token not found. Please log in again.');
        return;
      }

      const response = await fetch('https://medichainn.onrender.com/api/profile/delete-account', {
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
        setShowDeleteModal(false);
        setSuccess('✅ Your account has been successfully deleted.');
        setTimeout(() => {
          window.location.href = '/';
        }, 2000);
      } else {
        setError(result.error || 'Failed to delete account');
      }
    } catch (err) {
      console.error('Error deleting account:', err);
      setError('Failed to delete account. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const addArrayItem = (field, value) => {
    if (value.trim()) {
      setMedicalInfo({
        ...medicalInfo,
        [field]: [...medicalInfo[field], value.trim()]
      });
    }
  };

  const removeArrayItem = (field, index) => {
    setMedicalInfo({
      ...medicalInfo,
      [field]: medicalInfo[field].filter((_, i) => i !== index)
    });
  };

  if (loading) {
    return (
      <div className="profile-page">
        <div className="profile-loading-container">
          <div className="profile-loading-spinner"></div>
          <p className="profile-loading-text">Loading your profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-page">
      {/* Header */}
      <div className="profile-header-nav">
        <div className="container">
          <div className="profile-header-content">
            <div className="profile-header-left">
              <button 
                onClick={() => navigate('/dashboard')}
                className="profile-back-btn"
              >
                <ArrowLeft size={20} />
              </button>
              <h1 className="profile-header-title">Patient Profile Management</h1>
            </div>
            <div className="profile-header-right">
              <div className="profile-welcome-text">
                Welcome, {formData.first_name || 'Patient'}
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
                  <span>
                    {formData.first_name?.charAt(0)?.toUpperCase() || 'P'}
                  </span>
                </div>
                <label className="profile-avatar-upload">
                  <Upload size={16} />
                  <span className="profile-avatar-upload-label">{uploading ? 'Uploading...' : 'Upload Photo'}</span>
                  <input
                    type="file"
                    accept="image/*"
                    disabled={uploading}
                  />
                </label>
              </div>
              <div className="profile-info">
                <h2 className="profile-name">
                  {formData.first_name} {formData.last_name}
                </h2>
                <p className="profile-role">Patient</p>
                {formData.email && (
                  <p className="profile-email">{formData.email}</p>
                )}
              </div>
            </div>
            <div className="profile-card-actions">
              {editing ? (
                <>
                  <button
                    onClick={handleSavePersonalInfo}
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
                    onClick={() => {
                      setEditing(false);
                      loadProfile();
                    }}
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

        {/* Alert Messages */}
        {error && (
          <div className="profile-alert profile-alert-error">
            <AlertCircle size={20} />
            <span>{error}</span>
            <button onClick={() => setError('')}><X size={16} /></button>
          </div>
        )}
        {success && (
          <div className="profile-alert profile-alert-success">
            <CheckCircle size={20} />
            <span>{success}</span>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="profile-tabs">
          <button
            className={`profile-tab ${activeTab === 'personal' ? 'profile-tab-active' : ''}`}
            onClick={() => setActiveTab('personal')}
          >
            <User size={18} />
            Personal Info
          </button>
          <button
            className={`profile-tab ${activeTab === 'medical' ? 'profile-tab-active' : ''}`}
            onClick={() => setActiveTab('medical')}
          >
            <Heart size={18} />
            Medical Info
          </button>
          <button
            className={`profile-tab ${activeTab === 'documents' ? 'profile-tab-active' : ''}`}
            onClick={() => setActiveTab('documents')}
          >
            <FileText size={18} />
            Documents
          </button>
          <button
            className={`profile-tab ${activeTab === 'privacy' ? 'profile-tab-active' : ''}`}
            onClick={() => setActiveTab('privacy')}
          >
            <Eye size={18} />
            Privacy
          </button>
          <button
            className={`profile-tab ${activeTab === 'security' ? 'profile-tab-active' : ''}`}
            onClick={() => setActiveTab('security')}
          >
            <Shield size={18} />
            Security
          </button>
          <button
            className={`profile-tab ${activeTab === 'payments' ? 'profile-tab-active' : ''}`}
            onClick={() => setActiveTab('payments')}
          >
            <CreditCard size={18} />
            Payment History
          </button>
        </div>

        {/* Tab Content */}
        <div className="profile-tab-content">
          {/* Personal Info Tab */}
          {activeTab === 'personal' && (
            <div className="profile-tab-section">
              <h3 className="profile-tab-title">Personal Information</h3>
              
              <div className="profile-form-grid">
                <div className="profile-form-group">
                  <label className="profile-form-label">FIRST NAME</label>
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
                  <label className="profile-form-label">LAST NAME</label>
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
                  <label className="profile-form-label">EMAIL ADDRESS</label>
                  <input
                    type="email"
                    value={formData.email}
                    disabled
                    className="profile-form-input"
                    placeholder="your.email@example.com"
                  />
                </div>
                
                <div className="profile-form-group">
                  <label className="profile-form-label">PHONE NUMBER</label>
                  <input
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData({...formData, phone: e.target.value})}
                    disabled={!editing}
                    className="profile-form-input"
                    placeholder="+1 (555) 000-0000"
                  />
                </div>

                <div className="profile-form-group">
                  <label className="profile-form-label">ADDRESS</label>
                  <input
                    type="text"
                    value={formData.address}
                    onChange={(e) => setFormData({...formData, address: e.target.value})}
                    disabled={!editing}
                    className="profile-form-input"
                    placeholder="Street address"
                  />
                </div>

                <div className="profile-form-group">
                  <label className="profile-form-label">CITY</label>
                  <input
                    type="text"
                    value={formData.city}
                    onChange={(e) => setFormData({...formData, city: e.target.value})}
                    disabled={!editing}
                    className="profile-form-input"
                    placeholder="City"
                  />
                </div>

                <div className="profile-form-group">
                  <label className="profile-form-label">STATE</label>
                  <input
                    type="text"
                    value={formData.state}
                    onChange={(e) => setFormData({...formData, state: e.target.value})}
                    disabled={!editing}
                    className="profile-form-input"
                    placeholder="State"
                  />
                </div>

                <div className="profile-form-group">
                  <label className="profile-form-label">ZIP CODE</label>
                  <input
                    type="text"
                    value={formData.zip_code}
                    onChange={(e) => setFormData({...formData, zip_code: e.target.value})}
                    disabled={!editing}
                    className="profile-form-input"
                    placeholder="ZIP Code"
                  />
                </div>

                <div className="profile-form-group">
                  <label className="profile-form-label">DATE OF BIRTH</label>
                  <input
                    type="date"
                    value={formData.date_of_birth}
                    onChange={(e) => setFormData({...formData, date_of_birth: e.target.value})}
                    disabled={!editing}
                    className="profile-form-input"
                  />
                </div>

                <div className="profile-form-group">
                  <label className="profile-form-label">GENDER</label>
                  <select
                    value={formData.gender}
                    onChange={(e) => setFormData({...formData, gender: e.target.value})}
                    disabled={!editing}
                    className="profile-form-select"
                  >
                    <option value="">Select gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                  </select>
                </div>

              </div>
            </div>
          )}

          {/* Medical Info Tab */}
          {activeTab === 'medical' && (
            <div className="profile-tab-section">
              <h3 className="profile-tab-title">Medical Information</h3>
              
              <div className="profile-form-grid">
                <div className="profile-form-group">
                  <label className="profile-form-label">BLOOD TYPE</label>
                  <select
                    value={medicalInfo.blood_type}
                    onChange={(e) => setMedicalInfo({...medicalInfo, blood_type: e.target.value})}
                    className="profile-form-select"
                  >
                    <option value="">Select blood type</option>
                    <option value="A+">A+</option>
                    <option value="A-">A-</option>
                    <option value="B+">B+</option>
                    <option value="B-">B-</option>
                    <option value="O+">O+</option>
                    <option value="O-">O-</option>
                    <option value="AB+">AB+</option>
                    <option value="AB-">AB-</option>
                  </select>
                </div>

                <div className="profile-form-group">
                  <label className="profile-form-label">MEDICAL CONDITIONS</label>
                  <div className="profile-tag-input">
                    <input
                      type="text"
                      placeholder="Add a condition and press Enter"
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          addArrayItem('medical_conditions', e.target.value);
                          e.target.value = '';
                        }
                      }}
                      className="profile-form-input"
                    />
                  </div>
                  <div className="profile-tags">
                    {medicalInfo.medical_conditions.map((condition, index) => (
                      <span key={index} className="profile-tag">
                        {condition}
                        <button onClick={() => removeArrayItem('medical_conditions', index)}>
                          <X size={14} />
                        </button>
                      </span>
                    ))}
                  </div>
                </div>

                <div className="profile-form-group">
                  <label className="profile-form-label">ALLERGIES</label>
                  <div className="profile-tag-input">
                    <input
                      type="text"
                      placeholder="Add an allergy and press Enter"
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          addArrayItem('allergies', e.target.value);
                          e.target.value = '';
                        }
                      }}
                      className="profile-form-input"
                    />
                  </div>
                  <div className="profile-tags">
                    {medicalInfo.allergies.map((allergy, index) => (
                      <span key={index} className="profile-tag">
                        {allergy}
                        <button onClick={() => removeArrayItem('allergies', index)}>
                          <X size={14} />
                        </button>
                      </span>
                    ))}
                  </div>
                </div>

                <div className="profile-form-group">
                  <label className="profile-form-label">CURRENT MEDICATIONS</label>
                  <div className="profile-tag-input">
                    <input
                      type="text"
                      placeholder="Add a medication and press Enter"
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          addArrayItem('current_medications', e.target.value);
                          e.target.value = '';
                        }
                      }}
                      className="profile-form-input"
                    />
                  </div>
                  <div className="profile-tags">
                    {medicalInfo.current_medications.map((medication, index) => (
                      <span key={index} className="profile-tag">
                        {medication}
                        <button onClick={() => removeArrayItem('current_medications', index)}>
                          <X size={14} />
                        </button>
                      </span>
                    ))}
                  </div>
                </div>

                <div className="profile-form-group" style={{gridColumn: '1 / -1'}}>
                  <label className="profile-form-label">MEDICAL NOTES</label>
                  <textarea
                    value={medicalInfo.medical_notes}
                    onChange={(e) => setMedicalInfo({...medicalInfo, medical_notes: e.target.value})}
                    className="profile-form-textarea"
                    rows="4"
                    placeholder="Any additional medical information..."
                  />
                </div>
              </div>

              <div className="profile-action-buttons">
                <button 
                  className="profile-btn profile-btn-success" 
                  onClick={handleSaveMedicalInfo}
                  disabled={saving}
                >
                  {saving ? (
                    <>
                      <div className="profile-btn-spinner"></div>
                      <span>Saving...</span>
                    </>
                  ) : (
                    <>
                      <Save size={16} />
                      Save Changes
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {/* Documents Tab */}
          {activeTab === 'documents' && (
            <div className="profile-tab-section">
              <div className="profile-section-header">
                <h2>Health Documents</h2>
                <label className="profile-btn profile-btn-primary">
                  {uploading ? (
                    <>
                      <div className="profile-btn-spinner"></div>
                      <span>Uploading...</span>
                    </>
                  ) : (
                    <>
                      <Upload size={16} />
                      Upload Document
                    </>
                  )}
                  <input
                    type="file"
                    hidden
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={handleDocumentUpload}
                    disabled={uploading}
                  />
                </label>
              </div>

              <div className="profile-documents-grid">
                {documents.length === 0 ? (
                  <div className="profile-empty-state">
                    <FileText size={48} />
                    <p>No documents uploaded yet</p>
                    <p className="profile-empty-subtitle">Upload your medical records, test results, and prescriptions</p>
                  </div>
                ) : (
                  documents.map((doc, index) => (
                    <div key={index} className="profile-document-card">
                      <FileText size={32} />
                      <h3>{doc.filename}</h3>
                      <p>{new Date(doc.uploaded_at).toLocaleDateString()}</p>
                      <button className="profile-btn profile-btn-danger">
                        <Trash2 size={16} />
                        Delete
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* Privacy Tab */}
          {activeTab === 'privacy' && (
            <div className="profile-tab-section">
              <h3 className="profile-tab-title">Privacy Settings</h3>
              
              <div className="profile-form-grid">
                <div className="profile-form-group">
                  <label className="profile-form-label">PROFILE VISIBILITY</label>
                  <select
                    value={privacySettings.profile_visibility}
                    onChange={(e) => setPrivacySettings({...privacySettings, profile_visibility: e.target.value})}
                    className="profile-form-select"
                  >
                    <option value="private">Private</option>
                    <option value="doctors_only">Doctors Only</option>
                    <option value="public">Public</option>
                  </select>
                  <p className="profile-field-description">Control who can see your profile</p>
                </div>

                <div className="profile-setting-item-compact">
                  <div className="profile-setting-info">
                    <h3>Show Email</h3>
                    <p>Display your email in your profile</p>
                  </div>
                  <label className="profile-toggle">
                    <input
                      type="checkbox"
                      checked={privacySettings.show_email}
                      onChange={(e) => setPrivacySettings({...privacySettings, show_email: e.target.checked})}
                    />
                    <span className="profile-toggle-slider"></span>
                  </label>
                </div>

                <div className="profile-setting-item-compact">
                  <div className="profile-setting-info">
                    <h3>Show Phone</h3>
                    <p>Display your phone number in your profile</p>
                  </div>
                  <label className="profile-toggle">
                    <input
                      type="checkbox"
                      checked={privacySettings.show_phone}
                      onChange={(e) => setPrivacySettings({...privacySettings, show_phone: e.target.checked})}
                    />
                    <span className="profile-toggle-slider"></span>
                  </label>
                </div>

                <div className="profile-setting-item-compact">
                  <div className="profile-setting-info">
                    <h3>Medical Info for Doctors</h3>
                    <p>Allow doctors to access your medical information</p>
                  </div>
                  <label className="profile-toggle">
                    <input
                      type="checkbox"
                      checked={privacySettings.medical_info_visible_to_doctors}
                      onChange={(e) => setPrivacySettings({...privacySettings, medical_info_visible_to_doctors: e.target.checked})}
                    />
                    <span className="profile-toggle-slider"></span>
                  </label>
                </div>

                <div className="profile-setting-item-compact">
                  <div className="profile-setting-info">
                    <h3>AI Analysis</h3>
                    <p>Allow AI to analyze your health data for insights</p>
                  </div>
                  <label className="profile-toggle">
                    <input
                      type="checkbox"
                      checked={privacySettings.allow_ai_analysis}
                      onChange={(e) => setPrivacySettings({...privacySettings, allow_ai_analysis: e.target.checked})}
                    />
                    <span className="profile-toggle-slider"></span>
                  </label>
                </div>

                <div className="profile-setting-item-compact" style={{gridColumn: '1 / -1'}}>
                  <div className="profile-setting-info">
                    <h3>Research Data Sharing</h3>
                    <p>Share anonymized data for medical research</p>
                  </div>
                  <label className="profile-toggle">
                    <input
                      type="checkbox"
                      checked={privacySettings.share_data_for_research}
                      onChange={(e) => setPrivacySettings({...privacySettings, share_data_for_research: e.target.checked})}
                    />
                    <span className="profile-toggle-slider"></span>
                  </label>
                </div>
              </div>

              <div className="profile-action-buttons">
                <button 
                  className="profile-btn profile-btn-success" 
                  onClick={handleSavePrivacySettings}
                  disabled={saving}
                >
                  {saving ? (
                    <>
                      <div className="profile-btn-spinner"></div>
                      <span>Saving...</span>
                    </>
                  ) : (
                    <>
                      <Save size={16} />
                      Save Settings
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {/* Security Tab */}
          {activeTab === 'security' && (
            <div className="profile-tab-section">
              <h3 className="profile-tab-title">Account Security</h3>
              
              <div className="profile-form-grid">
                <div className="profile-security-card" style={{gridColumn: '1 / -1'}}>
                  <Lock size={24} />
                  <div>
                    <h3>Change Password</h3>
                    <p>Update your password regularly to keep your account secure</p>
                  </div>
                  <button className="profile-btn profile-btn-secondary">
                    Change Password
                  </button>
                </div>

                <div className="profile-security-card" style={{gridColumn: '1 / -1'}}>
                  <Shield size={24} />
                  <div>
                    <h3>Two-Factor Authentication</h3>
                    <p>Add an extra layer of security to your account</p>
                  </div>
                  <button className="profile-btn profile-btn-secondary">
                    Enable 2FA
                  </button>
                </div>

                <div className="profile-danger-zone" style={{gridColumn: '1 / -1'}}>
                  <h3>Danger Zone</h3>
                  <p>Permanently delete your account and all associated data</p>
                  <button 
                    className="profile-btn profile-btn-danger"
                    onClick={() => setShowDeleteModal(true)}
                  >
                    <Trash2 size={16} />
                    Delete Account
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Payment History Tab */}
          {activeTab === 'payments' && (
            <div className="profile-tab-section">
              <h3 className="profile-tab-title">Payment History</h3>
              
              {paymentHistoryLoading ? (
                <div className="profile-loading">
                  <div className="profile-spinner"></div>
                  <p>Loading payment history...</p>
                </div>
              ) : paymentHistory.length === 0 ? (
                <div className="profile-empty-state">
                  <CreditCard size={48} />
                  <h4>No payments yet</h4>
                  <p>Your payment history will appear here once you make a payment.</p>
                </div>
              ) : (
                <div className="payment-history-list">
                  {paymentHistory.map((payment) => {
                    const paymentDate = payment.created_at 
                      ? new Date(payment.created_at).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })
                      : 'N/A';
                    
                    const paymentMethod = payment.payment_method 
                      ? payment.payment_method.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
                      : 'Unknown';
                    
                    const statusClass = `payment-status payment-status-${payment.status || 'pending'}`;
                    const statusText = payment.status 
                      ? payment.status.charAt(0).toUpperCase() + payment.status.slice(1)
                      : 'Pending';
                    
                    return (
                      <div key={payment.id || payment.transaction_id} className="payment-history-item">
                        <div className="payment-history-header">
                          <div className="payment-history-left">
                            <div className="payment-transaction-id">
                              Transaction: {payment.transaction_id || 'N/A'}
                            </div>
                            <div className="payment-date">{paymentDate}</div>
                          </div>
                          <div className={`payment-status-badge ${statusClass}`}>
                            {statusText}
                          </div>
                        </div>
                        <div className="payment-history-details">
                          <div className="payment-detail-row">
                            <span className="payment-detail-label">Amount:</span>
                            <span className="payment-detail-value">
                              ₱{parseFloat(payment.amount || 0).toFixed(2)}
                            </span>
                          </div>
                          <div className="payment-detail-row">
                            <span className="payment-detail-label">Payment Method:</span>
                            <span className="payment-detail-value">{paymentMethod}</span>
                          </div>
                          {payment.verified_at && (
                            <div className="payment-detail-row">
                              <span className="payment-detail-label">Verified:</span>
                              <span className="payment-detail-value">
                                {new Date(payment.verified_at).toLocaleDateString('en-US', {
                                  year: 'numeric',
                                  month: 'short',
                                  day: 'numeric',
                                  hour: '2-digit',
                                  minute: '2-digit'
                                })}
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Delete Account Modal */}
      {showDeleteModal && (
        <div className="profile-modal-overlay">
          <div className="profile-modal-content">
            <div className="profile-modal-header">
              <div className="profile-modal-icon-warning">
                <AlertCircle size={28} />
              </div>
              <h2>Delete Account</h2>
              <button className="profile-modal-close" onClick={handleCloseDeleteModal}>
                <X size={20} />
              </button>
            </div>

            <div className="profile-modal-body">
              {deleteStep === 1 ? (
                <>
                  <div className="profile-modal-warning-box">
                    <h3 className="profile-modal-warning-title">Verify Your Identity</h3>
                    <p className="profile-modal-warning-text">
                      Please enter your password to continue with account deletion.
                    </p>
                  </div>

                  <div className="profile-form-group">
                    <label>Password</label>
                    <input
                      type="password"
                      value={deletePassword}
                      onChange={(e) => setDeletePassword(e.target.value)}
                      className="profile-input"
                      placeholder="Enter your password"
                    />
                    {passwordError && (
                      <p className="profile-error-text">{passwordError}</p>
                    )}
                  </div>
                </>
              ) : (
                <div className="profile-modal-warning-box">
                  <h3 className="profile-modal-warning-title">Are you absolutely sure?</h3>
                  <p className="profile-modal-warning-text">
                    This action cannot be undone. This will permanently delete your account and remove all your data from our servers.
                  </p>
                  <ul className="profile-modal-warning-list">
                    <li>All personal and medical information will be deleted</li>
                    <li>All uploaded documents will be removed</li>
                    <li>You will lose access to all appointments</li>
                    <li>This action is irreversible</li>
                  </ul>
                </div>
              )}
            </div>

            <div className="profile-modal-footer">
              <button 
                className="profile-btn profile-btn-secondary" 
                onClick={handleCloseDeleteModal}
                disabled={passwordVerifying || saving}
              >
                Cancel
              </button>
              {deleteStep === 1 ? (
                <button 
                  className="profile-btn profile-btn-danger" 
                  onClick={handleVerifyPassword}
                  disabled={!deletePassword || passwordVerifying}
                >
                  {passwordVerifying ? 'Verifying...' : 'Verify Password'}
                </button>
              ) : (
                <button 
                  className="profile-btn profile-btn-danger" 
                  onClick={handleConfirmDelete}
                  disabled={saving}
                >
                  {saving ? 'Deleting...' : 'Delete My Account'}
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfilePage;

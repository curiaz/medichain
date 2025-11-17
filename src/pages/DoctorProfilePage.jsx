import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { API_CONFIG } from '../config/api';
import { 
  User, Lock, ShieldOff, Edit3, Save, X, AlertCircle, CheckCircle, ArrowLeft, Camera,
  Briefcase, FileText, Eye, History, Shield, Upload
} from 'lucide-react';
import './ProfilePage.css';

const DoctorProfilePage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [activeTab, setActiveTab] = useState('personal');
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  
  // Form data
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    email: '',
    address: '',
    city: '',
    state: '',
    zip_code: ''
  });

  const [professionalInfo, setProfessionalInfo] = useState({
    specialization: '',
    license_number: '',
    years_of_experience: '',
    hospital_affiliation: ''
  });

  const [documents, setDocuments] = useState({
    medical_license: null,
    certificates: [],
    verification_docs: []
  });

  const [privacySettings, setPrivacySettings] = useState({
    profile_visibility: 'public',
    show_email: false,
    show_phone: false,
    allow_patient_messages: true,
    data_sharing: false
  });

  const [activityLog, setActivityLog] = useState([]);
  
  // Deactivate modal states
  const [showDeactivateModal, setShowDeactivateModal] = useState(false);
  const [deactivateStep, setDeactivateStep] = useState(1);
  const [deactivatePassword, setDeactivatePassword] = useState('');
  const [passwordVerifying, setPasswordVerifying] = useState(false);
  const [passwordError, setPasswordError] = useState('');

  useEffect(() => {
    if (user) {
      loadProfile();
      loadDocuments();
      loadActivityLog();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  const loadProfile = () => {
    try {
      // Don't show loading spinner if we already have user data
      if (!formData.first_name && !formData.last_name) {
        setLoading(true);
      }
      
      console.log('🔍 Loading doctor profile, user object:', user);
      
      if (!user) {
        console.error('❌ No user found, redirecting to login');
        navigate('/login');
        return;
      }

      // Extract profile data from user object
      setFormData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        phone: user.phone || '',
        email: user.email || '',
        address: user.address || '',
        city: user.city || '',
        state: user.state || '',
        zip_code: user.zip_code || ''
      });

      // Extract doctor-specific data
      const docProfile = user.doctor_profile || {};
      setProfessionalInfo({
        specialization: docProfile.specialization || '',
        license_number: docProfile.license_number || '',
        years_of_experience: docProfile.years_of_experience || '',
        hospital_affiliation: docProfile.hospital_affiliation || ''
      });

      setPrivacySettings({
        profile_visibility: docProfile.profile_visibility || 'public',
        show_email: docProfile.show_email || false,
        show_phone: docProfile.show_phone || false,
        allow_patient_messages: docProfile.allow_patient_messages !== false,
        data_sharing: docProfile.data_sharing || false
      });

      setActivityLog([
        { date: new Date().toISOString(), action: 'Profile loaded', details: 'Viewed profile page' }
      ]);

      console.log('✅ Profile loaded successfully');
      setLoading(false);
    } catch (err) {
      console.error('❌ Error loading profile:', err);
      setError('Failed to load profile');
      setLoading(false);
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

      const response = await fetch('http://localhost:5000/api/profile/doctor/update', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      const result = await response.json();
      
      if (result.success) {
        setSuccess('Personal information updated successfully!');
        setEditing(false);
        
        // Fetch updated profile data from backend
        const profileResponse = await fetch('http://localhost:5000/api/profile/doctor/details', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (profileResponse.ok) {
          const profileData = await profileResponse.json();
          if (profileData.success) {
            // Update localStorage with new data
            const updatedUser = profileData.data;
            localStorage.setItem('medichain_user', JSON.stringify(updatedUser));
            
            // Reload profile from updated data
            window.location.reload(); // Simple solution to refresh everything
          }
        }
        
        loadActivityLog(); // Refresh activity log
        setTimeout(() => setSuccess(''), 3000);
      } else {
        setError(result.error || 'Failed to update');
      }
    } catch (err) {
      console.error('Error updating:', err);
      setError('Failed to update. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  // eslint-disable-next-line no-unused-vars
  const handleSaveProfessionalInfo = async () => {
    try {
      setSaving(true);
      setError('');
      
      const token = localStorage.getItem('medichain_token');
      if (!token) {
        setError('Please log in again');
        return;
      }

      const response = await fetch('http://localhost:5000/api/profile/doctor/update', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(professionalInfo)
      });

      const result = await response.json();
      
      if (result.success) {
        setSuccess('Professional information updated successfully!');
        
        // Fetch updated profile data
        const profileResponse = await fetch('http://localhost:5000/api/profile/doctor/details', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (profileResponse.ok) {
          const profileData = await profileResponse.json();
          if (profileData.success) {
            const updatedUser = profileData.data;
            localStorage.setItem('medichain_user', JSON.stringify(updatedUser));
            
            // Update professional info state with new data
            const docProfile = updatedUser.doctor_profile || updatedUser;
            setProfessionalInfo({
              specialization: docProfile.specialization || '',
              license_number: docProfile.license_number || '',
              years_of_experience: docProfile.years_of_experience || '',
              hospital_affiliation: docProfile.hospital_affiliation || ''
            });
          }
        }
        
        loadActivityLog();
        setTimeout(() => setSuccess(''), 3000);
      } else {
        setError(result.error || 'Failed to update');
      }
    } catch (err) {
      console.error('Error updating professional info:', err);
      setError('Failed to update. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  // eslint-disable-next-line no-unused-vars
  const handleSavePrivacySettings = async () => {
    try {
      setSaving(true);
      setError('');
      
      const token = localStorage.getItem('medichain_token');
      if (!token) {
        setError('Please log in again');
        return;
      }

      const response = await fetch('http://localhost:5000/api/profile/doctor/privacy', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(privacySettings)
      });

      const result = await response.json();
      
      if (result.success) {
        setSuccess('Privacy settings updated successfully!');
        loadActivityLog();
        setTimeout(() => setSuccess(''), 3000);
      } else {
        setError(result.error || 'Failed to update');
      }
    } catch (err) {
      console.error('Error updating privacy settings:', err);
      setError('Failed to update. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleDocumentUpload = async (type, file) => {
    try {
      setUploading(true);
      setError('');
      
      const token = localStorage.getItem('medichain_token');
      if (!token) {
        setError('Please log in again');
        return;
      }

      const uploadFormData = new FormData();
      uploadFormData.append('file', file);
      uploadFormData.append('type', type);

      const response = await fetch('http://localhost:5000/api/profile/doctor/documents/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: uploadFormData
      });

      const result = await response.json();
      
      if (result.success) {
        setSuccess(`${type} uploaded successfully!`);
        loadDocuments(); // Refresh documents list
        loadActivityLog();
        setTimeout(() => setSuccess(''), 3000);
      } else {
        setError(result.error || 'Failed to upload document');
      }
    } catch (err) {
      console.error('Error uploading document:', err);
      setError('Failed to upload document. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const loadDocuments = async () => {
    try {
      const token = localStorage.getItem('medichain_token');
      if (!token) return;

      const response = await fetch('http://localhost:5000/api/profile/doctor/documents', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        console.warn('Documents endpoint not available yet');
        return;
      }

      const result = await response.json();
      
      if (result.success) {
        // Update documents state with loaded data
        const docs = result.documents.reduce((acc, doc) => {
          if (doc.document_type === 'license') {
            acc.medical_license = {
              name: doc.filename,
              size: `${(doc.file_size / 1024).toFixed(2)} KB`,
              uploadDate: new Date(doc.uploaded_at).toLocaleDateString(),
              status: doc.status
            };
          } else if (doc.document_type === 'certificate') {
            if (!Array.isArray(acc.certificates)) acc.certificates = [];
            acc.certificates.push({
              name: doc.filename,
              size: `${(doc.file_size / 1024).toFixed(2)} KB`,
              uploadDate: new Date(doc.uploaded_at).toLocaleDateString(),
              status: doc.status
            });
          } else if (doc.document_type === 'verification') {
            if (!Array.isArray(acc.verification_docs)) acc.verification_docs = [];
            acc.verification_docs.push({
              name: doc.filename,
              size: `${(doc.file_size / 1024).toFixed(2)} KB`,
              uploadDate: new Date(doc.uploaded_at).toLocaleDateString(),
              status: doc.status
            });
          }
          return acc;
        }, {});
        setDocuments(prevDocs => ({ ...prevDocs, ...docs }));
      }
    } catch (err) {
      console.error('Error loading documents:', err);
    }
  };

  const loadActivityLog = async () => {
    try {
      const token = localStorage.getItem('medichain_token');
      if (!token) return;

      const response = await fetch('http://localhost:5000/api/profile/doctor/activity', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        console.warn('Activity log endpoint not available yet');
        return;
      }

      const result = await response.json();
      
      if (result.success) {
        setActivityLog(result.activities);
      }
    } catch (err) {
      console.error('Error loading activity log:', err);
    }
  };

  const handleVerifyPassword = async () => {
    if (!deactivatePassword) {
      setPasswordError('Please enter your password');
      return;
    }

    try {
      setPasswordVerifying(true);
      setPasswordError('');

      const token = localStorage.getItem('medichain_token');
      const response = await fetch('http://localhost:5000/api/auth/verify-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          email: formData.email,
          password: deactivatePassword
        })
      });

      const result = await response.json();

      if (result.success) {
        setDeactivateStep(2);
        setPasswordError('');
      } else {
        setPasswordError(result.error || 'Incorrect password');
      }
    } catch (err) {
      console.error('Password verification error:', err);
      setPasswordError('Failed to verify password');
    } finally {
      setPasswordVerifying(false);
    }
  };

  const handleConfirmDeactivate = async () => {
    try {
      setPasswordVerifying(true);

      const token = localStorage.getItem('medichain_token');
      const response = await fetch('http://localhost:5000/api/profile/delete-account', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          email: formData.email,
          password: deactivatePassword
        })
      });

      const result = await response.json();

      if (result.success) {
        localStorage.removeItem('medichain_token');
        localStorage.removeItem('medichain_user');
        window.location.href = '/';
      } else {
        setPasswordError(result.error || 'Failed to deactivate account');
        setPasswordVerifying(false);
      }
    } catch (err) {
      console.error('Deactivation error:', err);
      setPasswordError('Failed to deactivate account');
      setPasswordVerifying(false);
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

  const userProfile = {
    first_name: formData.first_name,
    last_name: formData.last_name,
    email: formData.email,
    role: 'Doctor',
    specialization: professionalInfo.specialization || 'Doctor'
  };

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
                Welcome, Dr. {userProfile.first_name || 'User'}
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
                    {userProfile.first_name?.charAt(0)?.toUpperCase() || 'D'}
                  </span>
                </div>
                <label className="profile-avatar-upload">
                  <Camera size={16} />
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
                  Dr. {userProfile.first_name} {userProfile.last_name}
                </h2>
                <p className="profile-role">Doctor</p>
                {userProfile.specialization && (
                  <p className="profile-specialization">{userProfile.specialization}</p>
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
                { id: 'professional', label: 'Professional Info', icon: Briefcase },
                { id: 'documents', label: 'Documents', icon: FileText },
                { id: 'privacy', label: 'Privacy Settings', icon: Eye },
                { id: 'security', label: 'Account Security', icon: Lock },
                { id: 'activity', label: 'Activity History', icon: History }
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
                    <label className="profile-form-label">Email Address</label>
                    <input
                      type="email"
                      value={formData.email}
                      disabled
                      className="profile-form-input"
                      placeholder="your.email@example.com"
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
                      placeholder="+1 (555) 000-0000"
                    />
                  </div>

                  <div className="profile-form-group">
                    <label className="profile-form-label">Address</label>
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
                    <label className="profile-form-label">City</label>
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
                    <label className="profile-form-label">State</label>
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
                    <label className="profile-form-label">ZIP Code</label>
                    <input
                      type="text"
                      value={formData.zip_code}
                      onChange={(e) => setFormData({...formData, zip_code: e.target.value})}
                      disabled={!editing}
                      className="profile-form-input"
                      placeholder="ZIP Code"
                    />
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'professional' && (
              <div className="profile-tab-section">
                <h3 className="profile-tab-title">Professional Information</h3>
                
                <div className="profile-form-grid">
                  <div className="profile-form-group">
                    <label className="profile-form-label">Medical License Number</label>
                    <input
                      type="text"
                      value={professionalInfo.license_number}
                      onChange={(e) => setProfessionalInfo({...professionalInfo, license_number: e.target.value})}
                      disabled={!editing}
                      className="profile-form-input"
                      placeholder="Enter license number"
                    />
                  </div>

                  <div className="profile-form-group">
                    <label className="profile-form-label">Specialization</label>
                    <input
                      type="text"
                      value={professionalInfo.specialization}
                      onChange={(e) => setProfessionalInfo({...professionalInfo, specialization: e.target.value})}
                      disabled={!editing}
                      className="profile-form-input"
                      placeholder="e.g., Cardiology"
                    />
                  </div>

                  <div className="profile-form-group">
                    <label className="profile-form-label">Years of Experience</label>
                    <input
                      type="number"
                      value={professionalInfo.years_of_experience}
                      onChange={(e) => setProfessionalInfo({...professionalInfo, years_of_experience: e.target.value})}
                      disabled={!editing}
                      className="profile-form-input"
                      placeholder="0"
                      min="0"
                    />
                  </div>

                  <div className="profile-form-group">
                    <label className="profile-form-label">Hospital Affiliation</label>
                    <input
                      type="text"
                      value={professionalInfo.hospital_affiliation}
                      onChange={(e) => setProfessionalInfo({...professionalInfo, hospital_affiliation: e.target.value})}
                      disabled={!editing}
                      className="profile-form-input"
                      placeholder="Hospital/Clinic name"
                    />
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'documents' && (
              <div className="profile-tab-section">
                <h3 className="profile-tab-title">Documents & Verification</h3>
                
                <div className="profile-document-grid">
                  <div className="profile-document-card">
                    <div className="profile-document-header">
                      <FileText size={24} className="profile-document-icon" />
                      <div>
                        <h4 className="profile-document-title">Medical License</h4>
                        <p className="profile-document-description">Upload your medical license document</p>
                      </div>
                    </div>
                    {documents.medical_license ? (
                      <div className="profile-document-info">
                        <p className="profile-document-filename">{documents.medical_license.name}</p>
                        <p className="profile-document-meta">
                          {documents.medical_license.size} • {documents.medical_license.uploadDate}
                        </p>
                        <span className={`profile-document-status profile-status-${documents.medical_license.status}`}>
                          {documents.medical_license.status}
                        </span>
                      </div>
                    ) : (
                      <label className="profile-btn profile-btn-outline profile-btn-upload">
                        <Upload size={18} />
                        <span>{uploading ? 'Uploading...' : 'Upload License'}</span>
                        <input 
                          type="file" 
                          accept=".pdf,.jpg,.jpeg,.png" 
                          style={{display: 'none'}}
                          onChange={(e) => e.target.files[0] && handleDocumentUpload('license', e.target.files[0])}
                          disabled={uploading}
                        />
                      </label>
                    )}
                  </div>

                  <div className="profile-document-card">
                    <div className="profile-document-header">
                      <FileText size={24} className="profile-document-icon" />
                      <div>
                        <h4 className="profile-document-title">Certificates</h4>
                        <p className="profile-document-description">Upload professional certificates</p>
                      </div>
                    </div>
                    <label className="profile-btn profile-btn-outline profile-btn-upload">
                      <Upload size={18} />
                      <span>{uploading ? 'Uploading...' : 'Upload Certificates'}</span>
                      <input 
                        type="file" 
                        accept=".pdf,.jpg,.jpeg,.png" 
                        multiple 
                        style={{display: 'none'}}
                        onChange={(e) => e.target.files[0] && handleDocumentUpload('certificate', e.target.files[0])}
                        disabled={uploading}
                      />
                    </label>
                    {Array.isArray(documents.certificates) && documents.certificates.length > 0 && (
                      <div className="profile-documents-list">
                        {documents.certificates.map((cert, idx) => (
                          <div key={idx} className="profile-document-item">
                            <p className="profile-document-filename">{cert.name}</p>
                            <span className={`profile-document-status profile-status-${cert.status}`}>
                              {cert.status}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="profile-document-card">
                    <div className="profile-document-header">
                      <FileText size={24} className="profile-document-icon" />
                      <div>
                        <h4 className="profile-document-title">Verification Documents</h4>
                        <p className="profile-document-description">Upload additional verification documents</p>
                      </div>
                    </div>
                    <label className="profile-btn profile-btn-outline profile-btn-upload">
                      <Upload size={18} />
                      <span>{uploading ? 'Uploading...' : 'Upload Documents'}</span>
                      <input 
                        type="file" 
                        accept=".pdf,.jpg,.jpeg,.png" 
                        multiple 
                        style={{display: 'none'}}
                        onChange={(e) => e.target.files[0] && handleDocumentUpload('verification', e.target.files[0])}
                        disabled={uploading}
                      />
                    </label>
                    {Array.isArray(documents.verification_docs) && documents.verification_docs.length > 0 && (
                      <div className="profile-documents-list">
                        {documents.verification_docs.map((doc, idx) => (
                          <div key={idx} className="profile-document-item">
                            <p className="profile-document-filename">{doc.name}</p>
                            <span className={`profile-document-status profile-status-${doc.status}`}>
                              {doc.status}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                <div className="profile-info-box">
                  <AlertCircle size={20} />
                  <div>
                    <strong>Supported formats:</strong> PDF, JPG, PNG (Max 5MB per file)
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'privacy' && (
              <div className="profile-tab-section">
                <h3 className="profile-tab-title">Privacy Settings</h3>
                
                <div className="profile-settings-list">
                  <div className="profile-setting-item">
                    <div className="profile-setting-info">
                      <h4 className="profile-setting-title">Profile Visibility</h4>
                      <p className="profile-setting-description">Control who can see your profile</p>
                    </div>
                    <select 
                      value={privacySettings.profile_visibility}
                      onChange={(e) => setPrivacySettings({...privacySettings, profile_visibility: e.target.value})}
                      className="profile-select"
                    >
                      <option value="public">Public</option>
                      <option value="patients">Patients Only</option>
                      <option value="private">Private</option>
                    </select>
                  </div>

                  <div className="profile-setting-item">
                    <div className="profile-setting-info">
                      <h4 className="profile-setting-title">Show Email Address</h4>
                      <p className="profile-setting-description">Display email on public profile</p>
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

                  <div className="profile-setting-item">
                    <div className="profile-setting-info">
                      <h4 className="profile-setting-title">Show Phone Number</h4>
                      <p className="profile-setting-description">Display phone on public profile</p>
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

                  <div className="profile-setting-item">
                    <div className="profile-setting-info">
                      <h4 className="profile-setting-title">Allow Patient Messages</h4>
                      <p className="profile-setting-description">Let patients contact you directly</p>
                    </div>
                    <label className="profile-toggle">
                      <input
                        type="checkbox"
                        checked={privacySettings.allow_patient_messages}
                        onChange={(e) => setPrivacySettings({...privacySettings, allow_patient_messages: e.target.checked})}
                      />
                      <span className="profile-toggle-slider"></span>
                    </label>
                  </div>

                  <div className="profile-setting-item">
                    <div className="profile-setting-info">
                      <h4 className="profile-setting-title">Data Sharing</h4>
                      <p className="profile-setting-description">Share anonymized data for research</p>
                    </div>
                    <label className="profile-toggle">
                      <input
                        type="checkbox"
                        checked={privacySettings.data_sharing}
                        onChange={(e) => setPrivacySettings({...privacySettings, data_sharing: e.target.checked})}
                      />
                      <span className="profile-toggle-slider"></span>
                    </label>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'security' && (
              <div className="profile-tab-section">
                <h3 className="profile-tab-title">Account Security</h3>
                
                <div className="profile-security-grid">
                  <div className="profile-security-card">
                    <div className="profile-security-header">
                      <Lock size={24} className="profile-security-icon" />
                      <div>
                        <h4 className="profile-security-title">Change Password</h4>
                        <p className="profile-security-description">Update your account password</p>
                      </div>
                    </div>
                    <button className="profile-btn profile-btn-outline">
                      <Lock size={18} />
                      <span>Change Password</span>
                    </button>
                  </div>

                  <div className="profile-security-card">
                    <div className="profile-security-header">
                      <Shield size={24} className="profile-security-icon" />
                      <div>
                        <h4 className="profile-security-title">Two-Factor Authentication</h4>
                        <p className="profile-security-description">Add an extra layer of security</p>
                      </div>
                    </div>
                    <label className="profile-toggle">
                      <input type="checkbox" />
                      <span className="profile-toggle-slider"></span>
                    </label>
                  </div>
                </div>

                <div className="profile-danger-zone">
                  <div className="profile-danger-zone-header">
                    <ShieldOff size={24} className="profile-danger-icon" />
                    <div className="profile-danger-zone-content">
                      <h3 className="profile-danger-zone-title">Deactivate Account</h3>
                      <p className="profile-danger-zone-description">
                        Temporarily disable your account. You can reactivate it anytime by logging in with your credentials.
                      </p>
                    </div>
                  </div>
                  <button
                    className="profile-btn profile-btn-danger"
                    onClick={() => setShowDeactivateModal(true)}
                  >
                    <ShieldOff size={18} />
                    <span>Deactivate Account</span>
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'activity' && (
              <div className="profile-tab-section">
                <h3 className="profile-tab-title">Activity History</h3>
                
                {activityLog.length > 0 ? (
                  <div className="profile-activity-list">
                    {activityLog.map((activity, index) => (
                      <div key={index} className="profile-activity-item">
                        <div className="profile-activity-icon">
                          <History size={20} />
                        </div>
                        <div className="profile-activity-content">
                          <h4 className="profile-activity-title">{activity.action}</h4>
                          <p className="profile-activity-details">{activity.details}</p>
                          <span className="profile-activity-time">
                            {new Date(activity.date).toLocaleString()}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="profile-empty-state">
                    <History size={48} />
                    <p>No activity recorded yet</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Deactivate Modal */}
        {showDeactivateModal && (
        <div className="profile-modal-overlay" onClick={() => {
          setShowDeactivateModal(false);
          setDeactivateStep(1);
          setDeactivatePassword('');
          setPasswordError('');
        }}>
          <div className="profile-modal-content" onClick={(e) => e.stopPropagation()}>
            {deactivateStep === 1 ? (
              <>
                <div className="profile-modal-header">
                  <h2>Verify Your Password</h2>
                  <p>Please enter your password to continue with account deactivation.</p>
                </div>
                
                <div className="profile-modal-body">
                  <div className="profile-form-group">
                    <label className="profile-form-label">Password</label>
                    <input
                      type="password"
                      value={deactivatePassword}
                      onChange={(e) => setDeactivatePassword(e.target.value)}
                      placeholder="Enter your password"
                      disabled={passwordVerifying}
                      className="profile-form-input"
                    />
                    {passwordError && (
                      <div className="profile-form-error">
                        <AlertCircle size={16} />
                        <span>{passwordError}</span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="profile-modal-footer">
                  <button
                    className="profile-btn profile-btn-primary"
                    onClick={handleVerifyPassword}
                    disabled={passwordVerifying}
                  >
                    <Lock size={18} />
                    <span>{passwordVerifying ? 'Verifying...' : 'Continue'}</span>
                  </button>
                  <button
                    className="profile-btn profile-btn-secondary"
                    onClick={() => {
                      setShowDeactivateModal(false);
                      setDeactivateStep(1);
                      setDeactivatePassword('');
                      setPasswordError('');
                    }}
                    disabled={passwordVerifying}
                  >
                    <X size={18} />
                    <span>Cancel</span>
                  </button>
                </div>
              </>
            ) : (
              <>
                <div className="profile-modal-header">
                  <h2>Confirm Account Deactivation</h2>
                </div>

                <div className="profile-modal-body">
                  <div className="profile-modal-warning-box">
                    <h3 className="profile-modal-warning-title">What happens when you deactivate?</h3>
                    <ul className="profile-modal-warning-list">
                      <li>Your account will be temporarily disabled</li>
                      <li>Your data will be preserved and not deleted</li>
                      <li>You can reactivate anytime by logging in</li>
                      <li>Patients won't be able to book appointments with you</li>
                    </ul>
                  </div>

                  {passwordError && (
                    <div className="profile-form-error">
                      <AlertCircle size={16} />
                      <span>{passwordError}</span>
                    </div>
                  )}
                </div>

                <div className="profile-modal-footer">
                  <button
                    className="profile-btn profile-btn-danger"
                    onClick={handleConfirmDeactivate}
                    disabled={passwordVerifying}
                  >
                    <ShieldOff size={18} />
                    <span>{passwordVerifying ? 'Deactivating...' : 'Yes, Deactivate My Account'}</span>
                  </button>
                  <button
                    className="profile-btn profile-btn-secondary"
                    onClick={() => {
                      setShowDeactivateModal(false);
                      setDeactivateStep(1);
                      setDeactivatePassword('');
                      setPasswordError('');
                    }}
                    disabled={passwordVerifying}
                  >
                    <X size={18} />
                    <span>Cancel</span>
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
        )}
      </div>
    </div>
  );
};

export default DoctorProfilePage;

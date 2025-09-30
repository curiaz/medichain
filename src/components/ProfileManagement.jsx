import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { 
  User, Mail, Phone, Calendar, MapPin, Heart, Shield, Star, 
  Clock, GraduationCap, Award, Languages, Edit3, Save, X, 
  Camera, Plus, Trash2, AlertCircle, CheckCircle, UserCheck,
  Settings, Upload, FileText, Lock, Eye, EyeOff, Key, 
  Database, History, Download, Upload as UploadIcon
} from 'lucide-react';

// Import tab components
import {
  PersonalInfoTab,
  MedicalInfoTab,
  DocumentsTab,
  PrivacySettingsTab,
  CredentialsTab,
  AuditTrailTab
} from './ProfileManagementTabs';

// Import styles
import './ProfileManagement.css';

const API_URL = 'http://localhost:5000/api';

const ProfileManagement = () => {
  const { user, updateUser } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [activeTab, setActiveTab] = useState('personal');
  const [editing, setEditing] = useState(false);
  const [auditTrail, setAuditTrail] = useState([]);

  // Form states
  const [personalInfo, setPersonalInfo] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    date_of_birth: '',
    gender: '',
    address: {},
    emergency_contact: {}
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

  // Input states for dynamic fields
  const [newCondition, setNewCondition] = useState('');
  const [newAllergy, setNewAllergy] = useState('');
  const [newMedication, setNewMedication] = useState('');

  useEffect(() => {
    fetchCompleteProfile();
    fetchAuditTrail();
  }, []);

  const fetchCompleteProfile = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('medichain_token');
      const response = await axios.get(`${API_URL}/profile-management/complete-profile`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        const profileData = response.data.profile;
        setProfile(profileData);
        
        // Populate form data
        const userProfile = profileData.user_profile || {};
        setPersonalInfo({
          first_name: userProfile.first_name || '',
          last_name: userProfile.last_name || '',
          phone: userProfile.phone || '',
          date_of_birth: userProfile.date_of_birth || '',
          gender: userProfile.gender || '',
          address: userProfile.address || {},
          emergency_contact: userProfile.emergency_contact || {}
        });

        setMedicalInfo({
          medical_conditions: userProfile.medical_conditions || [],
          allergies: userProfile.allergies || [],
          current_medications: userProfile.current_medications || [],
          blood_type: userProfile.blood_type || '',
          medical_notes: userProfile.medical_notes || ''
        });

        setPrivacySettings(profileData.privacy_settings || privacySettings);
        setDocuments(profileData.documents || []);
      }
    } catch (error) {
      setError('Failed to load profile');
      console.error('Profile fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAuditTrail = async () => {
    try {
      const token = localStorage.getItem('medichain_token');
      const response = await axios.get(`${API_URL}/profile-management/audit-trail`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        setAuditTrail(response.data.audit_trail);
      }
    } catch (error) {
      console.error('Audit trail fetch error:', error);
    }
  };

  const handlePersonalInfoUpdate = async () => {
    try {
      setSaving(true);
      setError(null);
      
      const token = localStorage.getItem('medichain_token');
      const response = await axios.put(`${API_URL}/profile-management/update-personal-info`, personalInfo, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        setSuccess('Personal information updated successfully!');
        setProfile(prev => ({
          ...prev,
          user_profile: response.data.profile
        }));
        setEditing(false);
        fetchAuditTrail();
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to update personal information');
    } finally {
      setSaving(false);
    }
  };

  const handleMedicalInfoUpdate = async () => {
    try {
      setSaving(true);
      setError(null);
      
      const token = localStorage.getItem('medichain_token');
      const response = await axios.put(`${API_URL}/profile-management/update-medical-info`, medicalInfo, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        setSuccess('Medical information updated successfully!');
        setProfile(prev => ({
          ...prev,
          user_profile: response.data.profile
        }));
        setEditing(false);
        fetchAuditTrail();
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to update medical information');
    } finally {
      setSaving(false);
    }
  };

  const handlePrivacySettingsUpdate = async () => {
    try {
      setSaving(true);
      setError(null);
      
      const token = localStorage.getItem('medichain_token');
      const response = await axios.put(`${API_URL}/profile-management/privacy-settings`, privacySettings, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        setSuccess('Privacy settings updated successfully!');
        setProfile(prev => ({
          ...prev,
          privacy_settings: response.data.privacy_settings
        }));
        fetchAuditTrail();
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to update privacy settings');
    } finally {
      setSaving(false);
    }
  };

  const handleDocumentUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      setUploading(true);
      const token = localStorage.getItem('medichain_token');
      
      const formData = new FormData();
      formData.append('file', file);
      formData.append('document_type', 'general');
      formData.append('description', 'Uploaded document');

      const response = await axios.post(`${API_URL}/profile-management/upload-document`, formData, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.data.success) {
        setSuccess('Document uploaded successfully!');
        setDocuments(prev => [response.data.document, ...prev]);
        fetchAuditTrail();
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const handleDocumentDelete = async (documentId) => {
    try {
      const token = localStorage.getItem('medichain_token');
      const response = await axios.delete(`${API_URL}/profile-management/documents/${documentId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        setSuccess('Document deleted successfully!');
        setDocuments(prev => prev.filter(doc => doc.id !== documentId));
        fetchAuditTrail();
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to delete document');
    }
  };

  const addToArray = (arrayName, value, setter) => {
    if (value.trim()) {
      setter(prev => ({
        ...prev,
        [arrayName]: [...prev[arrayName], value.trim()]
      }));
    }
  };

  const removeFromArray = (arrayName, index, setter) => {
    setter(prev => ({
      ...prev,
      [arrayName]: prev[arrayName].filter((_, i) => i !== index)
    }));
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  const userProfile = profile?.user_profile || {};
  const doctorProfile = profile?.doctor_profile || {};
  const isDoctor = userProfile.role === 'doctor';

  return (
    <div className="profile-management-container">
      {/* Profile Header */}
      <div className="profile-header">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="profile-avatar-container">
              <div className="profile-avatar">
                {userProfile.avatar_url ? (
                  <img 
                    src={userProfile.avatar_url} 
                    alt="Avatar" 
                    className="w-full h-full rounded-full object-cover"
                  />
                ) : (
                  <span>
                    {userProfile.first_name?.charAt(0)?.toUpperCase() || 'U'}
                  </span>
                )}
              </div>
              <label className="avatar-upload-btn">
                <Camera size={16} />
                <input
                  type="file"
                  accept="image/*"
                  className="hidden"
                />
              </label>
            </div>
            <div className="profile-info">
              <h1>
                {userProfile.first_name} {userProfile.last_name}
              </h1>
              <p className="profile-role">{userProfile.role}</p>
              {isDoctor && doctorProfile.specialization && (
                <p className="profile-specialization">{doctorProfile.specialization}</p>
              )}
            </div>
          </div>
          <div className="profile-actions">
            {editing ? (
              <>
                <button
                  onClick={() => {
                    if (activeTab === 'personal') handlePersonalInfoUpdate();
                    else if (activeTab === 'medical') handleMedicalInfoUpdate();
                    else if (activeTab === 'privacy') handlePrivacySettingsUpdate();
                  }}
                  disabled={saving}
                  className="btn-success"
                >
                  <Save size={16} />
                  <span>{saving ? 'Saving...' : 'Save'}</span>
                </button>
                <button
                  onClick={() => setEditing(false)}
                  className="btn-secondary"
                >
                  <X size={16} />
                  <span>Cancel</span>
                </button>
              </>
            ) : (
              <button
                onClick={() => setEditing(true)}
                className="btn-primary"
              >
                <Edit3 size={16} />
                <span>Edit Profile</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Success/Error Messages */}
      {success && (
        <div className="alert-success">
          <CheckCircle size={20} />
          {success}
        </div>
      )}
      {error && (
        <div className="alert-error">
          <AlertCircle size={20} />
          {error}
        </div>
      )}

      {/* Tab Navigation */}
      <div className="tab-container">
        <div className="tab-navigation">
          <nav className="tab-nav-list">
            {[
              { id: 'personal', label: 'Personal Info', icon: User },
              { id: 'medical', label: 'Medical Info', icon: Heart },
              { id: 'documents', label: 'Documents', icon: FileText },
              { id: 'privacy', label: 'Privacy & Security', icon: Lock },
              { id: 'credentials', label: 'Credentials', icon: Key },
              { id: 'audit', label: 'Audit Trail', icon: History }
            ].map(tab => (
              <li key={tab.id} className="tab-nav-item">
                <button
                  onClick={() => setActiveTab(tab.id)}
                  className={`tab-nav-button ${activeTab === tab.id ? 'active' : ''}`}
                >
                  <tab.icon size={16} />
                  <span>{tab.label}</span>
                </button>
              </li>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="tab-content">
          {activeTab === 'personal' && (
            <PersonalInfoTab 
              personalInfo={personalInfo} 
              setPersonalInfo={setPersonalInfo} 
              editing={editing} 
            />
          )}
          {activeTab === 'medical' && (
            <MedicalInfoTab 
              medicalInfo={medicalInfo} 
              setMedicalInfo={setMedicalInfo} 
              editing={editing}
              newCondition={newCondition}
              setNewCondition={setNewCondition}
              newAllergy={newAllergy}
              setNewAllergy={setNewAllergy}
              newMedication={newMedication}
              setNewMedication={setNewMedication}
              addToArray={addToArray}
              removeFromArray={removeFromArray}
            />
          )}
          {activeTab === 'documents' && (
            <DocumentsTab 
              documents={documents}
              uploading={uploading}
              handleDocumentUpload={handleDocumentUpload}
              handleDocumentDelete={handleDocumentDelete}
            />
          )}
          {activeTab === 'privacy' && (
            <PrivacySettingsTab 
              privacySettings={privacySettings} 
              setPrivacySettings={setPrivacySettings} 
              editing={editing} 
            />
          )}
          {activeTab === 'credentials' && (
            <CredentialsTab userProfile={userProfile} />
          )}
          {activeTab === 'audit' && (
            <AuditTrailTab auditTrail={auditTrail} />
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfileManagement;

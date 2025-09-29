import React from 'react';
import { 
  Plus, Trash2, FileText, UploadIcon, History, Database
} from 'lucide-react';

// Personal Information Tab Component
export const PersonalInfoTab = ({ personalInfo, setPersonalInfo, editing }) => (
  <div className="form-section">
    <h3>Personal Information</h3>
    
    <div className="form-grid">
      <div className="form-group">
        <label className="form-label">First Name</label>
        <input
          type="text"
          value={personalInfo.first_name}
          onChange={(e) => setPersonalInfo({...personalInfo, first_name: e.target.value})}
          disabled={!editing}
          className="form-input"
        />
      </div>
      
      <div className="form-group">
        <label className="form-label">Last Name</label>
        <input
          type="text"
          value={personalInfo.last_name}
          onChange={(e) => setPersonalInfo({...personalInfo, last_name: e.target.value})}
          disabled={!editing}
          className="form-input"
        />
      </div>
      
      <div className="form-group">
        <label className="form-label">Phone Number</label>
        <input
          type="tel"
          value={personalInfo.phone}
          onChange={(e) => setPersonalInfo({...personalInfo, phone: e.target.value})}
          disabled={!editing}
          className="form-input"
        />
      </div>
      
      <div className="form-group">
        <label className="form-label">Date of Birth</label>
        <input
          type="date"
          value={personalInfo.date_of_birth}
          onChange={(e) => setPersonalInfo({...personalInfo, date_of_birth: e.target.value})}
          disabled={!editing}
          className="form-input"
        />
      </div>
      
      <div className="form-group">
        <label className="form-label">Gender</label>
        <select
          value={personalInfo.gender}
          onChange={(e) => setPersonalInfo({...personalInfo, gender: e.target.value})}
          disabled={!editing}
          className="form-select"
        >
          <option value="">Select Gender</option>
          <option value="male">Male</option>
          <option value="female">Female</option>
          <option value="other">Other</option>
        </select>
      </div>
    </div>

    {/* Address Section */}
    <div className="form-section">
      <h4>Address Information</h4>
      <div className="form-grid">
        <div className="form-group">
          <label className="form-label">Street Address</label>
          <input
            type="text"
            value={personalInfo.address.street || ''}
            onChange={(e) => setPersonalInfo({
              ...personalInfo, 
              address: {...personalInfo.address, street: e.target.value}
            })}
            disabled={!editing}
            className="form-input"
          />
        </div>
        <div className="form-group">
          <label className="form-label">City</label>
          <input
            type="text"
            value={personalInfo.address.city || ''}
            onChange={(e) => setPersonalInfo({
              ...personalInfo, 
              address: {...personalInfo.address, city: e.target.value}
            })}
            disabled={!editing}
            className="form-input"
          />
        </div>
        <div className="form-group">
          <label className="form-label">State/Province</label>
          <input
            type="text"
            value={personalInfo.address.state || ''}
            onChange={(e) => setPersonalInfo({
              ...personalInfo, 
              address: {...personalInfo.address, state: e.target.value}
            })}
            disabled={!editing}
            className="form-input"
          />
        </div>
        <div className="form-group">
          <label className="form-label">Postal Code</label>
          <input
            type="text"
            value={personalInfo.address.postal_code || ''}
            onChange={(e) => setPersonalInfo({
              ...personalInfo, 
              address: {...personalInfo.address, postal_code: e.target.value}
            })}
            disabled={!editing}
            className="form-input"
          />
        </div>
      </div>
    </div>

    {/* Emergency Contact Section */}
    <div className="form-section">
      <h4>Emergency Contact</h4>
      <div className="form-grid">
        <div className="form-group">
          <label className="form-label">Contact Name</label>
          <input
            type="text"
            value={personalInfo.emergency_contact.name || ''}
            onChange={(e) => setPersonalInfo({
              ...personalInfo, 
              emergency_contact: {...personalInfo.emergency_contact, name: e.target.value}
            })}
            disabled={!editing}
            className="form-input"
          />
        </div>
        <div className="form-group">
          <label className="form-label">Contact Phone</label>
          <input
            type="tel"
            value={personalInfo.emergency_contact.phone || ''}
            onChange={(e) => setPersonalInfo({
              ...personalInfo, 
              emergency_contact: {...personalInfo.emergency_contact, phone: e.target.value}
            })}
            disabled={!editing}
            className="form-input"
          />
        </div>
        <div className="form-group">
          <label className="form-label">Relationship</label>
          <input
            type="text"
            value={personalInfo.emergency_contact.relationship || ''}
            onChange={(e) => setPersonalInfo({
              ...personalInfo, 
              emergency_contact: {...personalInfo.emergency_contact, relationship: e.target.value}
            })}
            disabled={!editing}
            className="form-input"
          />
        </div>
      </div>
    </div>
  </div>
);

// Medical Information Tab Component
export const MedicalInfoTab = ({ 
  medicalInfo, 
  setMedicalInfo, 
  editing,
  newCondition,
  setNewCondition,
  newAllergy,
  setNewAllergy,
  newMedication,
  setNewMedication,
  addToArray,
  removeFromArray
}) => (
  <div className="form-section">
    <h3>Medical Information</h3>
    
    {/* Medical Conditions */}
    <div className="form-group">
      <label className="form-label">Medical Conditions</label>
      <div className="array-container">
        {medicalInfo.medical_conditions.map((condition, index) => (
          <div key={index} className="array-item">
            <span className="array-item-content">{condition}</span>
            {editing && (
              <button
                onClick={() => removeFromArray('medical_conditions', index, setMedicalInfo)}
                className="array-item-delete"
              >
                <Trash2 size={16} />
              </button>
            )}
          </div>
        ))}
        {editing && (
          <div className="array-input-group">
            <input
              type="text"
              value={newCondition}
              onChange={(e) => setNewCondition(e.target.value)}
              placeholder="Add medical condition"
              className="array-input"
            />
            <button
              onClick={() => {
                addToArray('medical_conditions', newCondition, setMedicalInfo);
                setNewCondition('');
              }}
              className="array-add-btn"
            >
              <Plus size={16} />
            </button>
          </div>
        )}
      </div>
    </div>
    
    {/* Allergies */}
    <div className="form-group">
      <label className="form-label">Allergies</label>
      <div className="array-container">
        {medicalInfo.allergies.map((allergy, index) => (
          <div key={index} className="array-item">
            <span className="array-item-content">{allergy}</span>
            {editing && (
              <button
                onClick={() => removeFromArray('allergies', index, setMedicalInfo)}
                className="array-item-delete"
              >
                <Trash2 size={16} />
              </button>
            )}
          </div>
        ))}
        {editing && (
          <div className="array-input-group">
            <input
              type="text"
              value={newAllergy}
              onChange={(e) => setNewAllergy(e.target.value)}
              placeholder="Add allergy"
              className="array-input"
            />
            <button
              onClick={() => {
                addToArray('allergies', newAllergy, setMedicalInfo);
                setNewAllergy('');
              }}
              className="array-add-btn"
            >
              <Plus size={16} />
            </button>
          </div>
        )}
      </div>
    </div>

    {/* Current Medications */}
    <div className="form-group">
      <label className="form-label">Current Medications</label>
      <div className="array-container">
        {medicalInfo.current_medications.map((medication, index) => (
          <div key={index} className="array-item">
            <span className="array-item-content">{medication}</span>
            {editing && (
              <button
                onClick={() => removeFromArray('current_medications', index, setMedicalInfo)}
                className="array-item-delete"
              >
                <Trash2 size={16} />
              </button>
            )}
          </div>
        ))}
        {editing && (
          <div className="array-input-group">
            <input
              type="text"
              value={newMedication}
              onChange={(e) => setNewMedication(e.target.value)}
              placeholder="Add current medication"
              className="array-input"
            />
            <button
              onClick={() => {
                addToArray('current_medications', newMedication, setMedicalInfo);
                setNewMedication('');
              }}
              className="array-add-btn"
            >
              <Plus size={16} />
            </button>
          </div>
        )}
      </div>
    </div>

    {/* Blood Type */}
    <div className="form-group">
      <label className="form-label">Blood Type</label>
      <select
        value={medicalInfo.blood_type}
        onChange={(e) => setMedicalInfo({...medicalInfo, blood_type: e.target.value})}
        disabled={!editing}
        className="form-select"
      >
        <option value="">Select Blood Type</option>
        <option value="A+">A+</option>
        <option value="A-">A-</option>
        <option value="B+">B+</option>
        <option value="B-">B-</option>
        <option value="AB+">AB+</option>
        <option value="AB-">AB-</option>
        <option value="O+">O+</option>
        <option value="O-">O-</option>
      </select>
    </div>

    {/* Medical Notes */}
    <div className="form-group">
      <label className="form-label">Medical Notes</label>
      <textarea
        value={medicalInfo.medical_notes}
        onChange={(e) => setMedicalInfo({...medicalInfo, medical_notes: e.target.value})}
        disabled={!editing}
        className="form-textarea"
        placeholder="Additional medical notes..."
      />
    </div>
  </div>
);

// Documents Tab Component
export const DocumentsTab = ({ documents, uploading, handleDocumentUpload, handleDocumentDelete }) => (
  <div className="form-section">
    <div className="documents-header">
      <h3>Document Management</h3>
      <label className="documents-upload-btn">
        <UploadIcon size={16} />
        <span>{uploading ? 'Uploading...' : 'Upload Document'}</span>
        <input
          type="file"
          accept=".pdf,.png,.jpg,.jpeg,.doc,.docx,.txt"
          onChange={handleDocumentUpload}
          className="hidden"
          disabled={uploading}
        />
      </label>
    </div>

    {documents.length === 0 ? (
      <div className="documents-empty">
        <FileText size={48} className="documents-empty-icon" />
        <p>No documents uploaded yet</p>
        <p className="text-sm">Upload medical certificates, IDs, prescriptions, and other important documents</p>
      </div>
    ) : (
      <div className="documents-grid">
        {documents.map((doc) => (
          <div key={doc.id} className="document-card">
            <div className="document-header">
              <div className="document-info">
                <FileText size={20} className="document-icon" />
                <span className="document-name">{doc.filename}</span>
              </div>
              <button
                onClick={() => handleDocumentDelete(doc.id)}
                className="document-delete"
              >
                <Trash2 size={16} />
              </button>
            </div>
            <div className="document-meta">
              <p>Type: {doc.document_type}</p>
              <p>Size: {(doc.file_size / 1024).toFixed(1)} KB</p>
              <p>Uploaded: {new Date(doc.upload_date).toLocaleDateString()}</p>
            </div>
            {doc.description && (
              <p className="document-description">{doc.description}</p>
            )}
          </div>
        ))}
      </div>
    )}
  </div>
);

// Privacy Settings Tab Component
export const PrivacySettingsTab = ({ privacySettings, setPrivacySettings, editing }) => (
  <div className="form-section">
    <h3>Privacy & Security Controls</h3>
    
    <div className="privacy-section">
      {/* Profile Visibility */}
      <div className="form-group">
        <label className="form-label">Profile Visibility</label>
        <select
          value={privacySettings.profile_visibility}
          onChange={(e) => setPrivacySettings({...privacySettings, profile_visibility: e.target.value})}
          disabled={!editing}
          className="form-select"
        >
          <option value="private">Private</option>
          <option value="doctors_only">Doctors Only</option>
          <option value="public">Public</option>
        </select>
      </div>

      {/* Medical Information Sharing */}
      <div className="privacy-section">
        <h4>Medical Information Sharing</h4>
        <div className="privacy-options">
          <label className="privacy-option">
            <input
              type="checkbox"
              checked={privacySettings.medical_info_visible_to_doctors}
              onChange={(e) => setPrivacySettings({
                ...privacySettings, 
                medical_info_visible_to_doctors: e.target.checked
              })}
              disabled={!editing}
              className="privacy-checkbox"
            />
            <span className="privacy-label">Visible to Doctors</span>
          </label>
          <label className="privacy-option">
            <input
              type="checkbox"
              checked={privacySettings.medical_info_visible_to_hospitals}
              onChange={(e) => setPrivacySettings({
                ...privacySettings, 
                medical_info_visible_to_hospitals: e.target.checked
              })}
              disabled={!editing}
              className="privacy-checkbox"
            />
            <span className="privacy-label">Visible to Hospitals</span>
          </label>
          <label className="privacy-option">
            <input
              type="checkbox"
              checked={privacySettings.medical_info_visible_to_admins}
              onChange={(e) => setPrivacySettings({
                ...privacySettings, 
                medical_info_visible_to_admins: e.target.checked
              })}
              disabled={!editing}
              className="privacy-checkbox"
            />
            <span className="privacy-label">Visible to Administrators</span>
          </label>
        </div>
      </div>

      {/* AI and Research */}
      <div className="privacy-section">
        <h4>AI Analysis & Research</h4>
        <div className="privacy-options">
          <label className="privacy-option">
            <input
              type="checkbox"
              checked={privacySettings.allow_ai_analysis}
              onChange={(e) => setPrivacySettings({
                ...privacySettings, 
                allow_ai_analysis: e.target.checked
              })}
              disabled={!editing}
              className="privacy-checkbox"
            />
            <span className="privacy-label">Allow AI Analysis</span>
          </label>
          <label className="privacy-option">
            <input
              type="checkbox"
              checked={privacySettings.share_data_for_research}
              onChange={(e) => setPrivacySettings({
                ...privacySettings, 
                share_data_for_research: e.target.checked
              })}
              disabled={!editing}
              className="privacy-checkbox"
            />
            <span className="privacy-label">Share Data for Research (Anonymized)</span>
          </label>
        </div>
      </div>

      {/* Security Settings */}
      <div className="privacy-section">
        <h4>Security Settings</h4>
        <div className="privacy-options">
          <label className="privacy-option">
            <input
              type="checkbox"
              checked={privacySettings.emergency_access_enabled}
              onChange={(e) => setPrivacySettings({
                ...privacySettings, 
                emergency_access_enabled: e.target.checked
              })}
              disabled={!editing}
              className="privacy-checkbox"
            />
            <span className="privacy-label">Emergency Access Enabled</span>
          </label>
          <label className="privacy-option">
            <input
              type="checkbox"
              checked={privacySettings.two_factor_enabled}
              onChange={(e) => setPrivacySettings({
                ...privacySettings, 
                two_factor_enabled: e.target.checked
              })}
              disabled={!editing}
              className="privacy-checkbox"
            />
            <span className="privacy-label">Two-Factor Authentication</span>
          </label>
          <label className="privacy-option">
            <input
              type="checkbox"
              checked={privacySettings.login_notifications}
              onChange={(e) => setPrivacySettings({
                ...privacySettings, 
                login_notifications: e.target.checked
              })}
              disabled={!editing}
              className="privacy-checkbox"
            />
            <span className="privacy-label">Login Notifications</span>
          </label>
        </div>
      </div>

      {/* Data Control */}
      <div className="privacy-section">
        <h4>Data Control</h4>
        <div className="privacy-options">
          <label className="privacy-option">
            <input
              type="checkbox"
              checked={privacySettings.data_export_enabled}
              onChange={(e) => setPrivacySettings({
                ...privacySettings, 
                data_export_enabled: e.target.checked
              })}
              disabled={!editing}
              className="privacy-checkbox"
            />
            <span className="privacy-label">Allow Data Export</span>
          </label>
        </div>
      </div>
    </div>
  </div>
);

// Credentials Tab Component
export const CredentialsTab = ({ userProfile }) => (
  <div className="form-section">
    <h3>Login Credentials</h3>
    
    <div className="credentials-info">
      <h4>Account Information</h4>
      <div className="credentials-details">
        <p><strong>Email:</strong> {userProfile.email}</p>
        <p><strong>Role:</strong> {userProfile.role}</p>
        <p><strong>Member since:</strong> {new Date(userProfile.created_at).toLocaleDateString()}</p>
        <p><strong>Last login:</strong> {userProfile.last_login ? new Date(userProfile.last_login).toLocaleString() : 'Never'}</p>
      </div>
    </div>
    
    <div className="credentials-security-notice">
      <h4>Security Notice</h4>
      <p>
        For security reasons, password changes must be done through Firebase Authentication. 
        Contact support if you need assistance with account security.
      </p>
    </div>

    <div className="credentials-actions">
      <div className="credential-action">
        <div className="credential-info">
          <h4>Email Address</h4>
          <p>Update your email address</p>
        </div>
        <button className="btn-primary">
          Update Email
        </button>
      </div>

      <div className="credential-action">
        <div className="credential-info">
          <h4>Password</h4>
          <p>Change your password</p>
        </div>
        <button className="btn-primary">
          Change Password
        </button>
      </div>

      <div className="credential-action">
        <div className="credential-info">
          <h4>Two-Factor Authentication</h4>
          <p>Add an extra layer of security</p>
        </div>
        <button className="btn-success">
          Enable 2FA
        </button>
      </div>
    </div>
  </div>
);

// Audit Trail Tab Component
export const AuditTrailTab = ({ auditTrail }) => (
  <div className="form-section">
    <h3>Audit Trail & Blockchain History</h3>
    
    {auditTrail.length === 0 ? (
      <div className="audit-trail-empty">
        <History size={48} className="audit-trail-empty-icon" />
        <p>No audit trail available</p>
        <p className="text-sm">All profile changes will be recorded here</p>
      </div>
    ) : (
      <div className="audit-trail-list">
        {auditTrail.map((entry, index) => (
          <div key={index} className="audit-trail-item">
            <div className="audit-trail-header">
              <div className="audit-trail-action">
                <Database size={16} className="audit-trail-icon" />
                <span className="audit-trail-action-name">{entry.action}</span>
              </div>
              <span className="audit-trail-timestamp">
                {new Date(entry.timestamp).toLocaleString()}
              </span>
            </div>
            <div className="audit-trail-details">
              <p>Type: {entry.type}</p>
              {entry.data_hash && <p>Hash: {entry.data_hash.substring(0, 16)}...</p>}
              {entry.filename && <p>File: {entry.filename}</p>}
              {entry.credential_type && <p>Credential: {entry.credential_type}</p>}
            </div>
          </div>
        ))}
      </div>
    )}
  </div>
);
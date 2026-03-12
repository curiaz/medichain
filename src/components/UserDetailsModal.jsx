import React, { useState, useEffect } from 'react';
import { X, Save, Shield, User, Stethoscope } from 'lucide-react';
import adminService from '../services/adminService';
import './UserDetailsModal.css';

const UserDetailsModal = ({ user, onClose, onUpdate }) => {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    role: '',
    gender: '',
    date_of_birth: '',
    is_active: true,
    is_verified: false
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (user) {
      setFormData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        phone: user.phone || '',
        role: user.role || '',
        gender: user.gender || '',
        date_of_birth: user.date_of_birth || '',
        is_active: user.is_active !== undefined ? user.is_active : true,
        is_verified: user.is_verified !== undefined ? user.is_verified : false
      });
    }
  }, [user]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleRoleChange = async (newRole) => {
    if (window.confirm(`Are you sure you want to change this user's role to ${newRole}?`)) {
      try {
        setLoading(true);
        setError(null);
        const response = await adminService.changeUserRole(user.firebase_uid, newRole);
        if (response.success) {
          setSuccess(true);
          setTimeout(() => {
            onUpdate();
          }, 1000);
        }
      } catch (error) {
        setError('Failed to change user role. Please try again.');
      } finally {
        setLoading(false);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      setSuccess(false);

      const response = await adminService.updateUser(user.firebase_uid, formData);
      if (response.success) {
        setSuccess(true);
        setTimeout(() => {
          onUpdate();
        }, 1000);
      }
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to update user. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getRoleIcon = (role) => {
    switch (role) {
      case 'admin':
        return <Shield size={18} className="role-icon role-icon-admin" />;
      case 'doctor':
        return <Stethoscope size={18} className="role-icon role-icon-doctor" />;
      default:
        return <User size={18} className="role-icon role-icon-patient" />;
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>User Details</h2>
          <button className="modal-close" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <div className="modal-body">
          {error && (
            <div className="alert alert-error">
              {error}
            </div>
          )}

          {success && (
            <div className="alert alert-success">
              User updated successfully!
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-section">
              <h3>Basic Information</h3>
              <div className="form-grid">
                <div className="form-group">
                  <label>First Name</label>
                  <input
                    type="text"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Last Name</label>
                  <input
                    type="text"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Email</label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    disabled
                    className="disabled-input"
                  />
                  <small>Email cannot be changed</small>
                </div>

                <div className="form-group">
                  <label>Phone</label>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                  />
                </div>

                <div className="form-group">
                  <label>Gender</label>
                  <select name="gender" value={formData.gender} onChange={handleChange}>
                    <option value="">Select gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Date of Birth</label>
                  <input
                    type="date"
                    name="date_of_birth"
                    value={formData.date_of_birth}
                    onChange={handleChange}
                  />
                </div>
              </div>
            </div>

            <div className="form-section">
              <h3>Role & Status</h3>
              <div className="form-grid">
                <div className="form-group">
                  <label>Current Role</label>
                  <div className="role-display">
                    {getRoleIcon(formData.role)}
                    <span className="role-text">{formData.role}</span>
                  </div>
                  <div className="role-actions">
                    {formData.role !== 'patient' && (
                      <button
                        type="button"
                        className="btn-role-change"
                        onClick={() => handleRoleChange('patient')}
                        disabled={loading}
                      >
                        Change to Patient
                      </button>
                    )}
                    {formData.role !== 'doctor' && (
                      <button
                        type="button"
                        className="btn-role-change"
                        onClick={() => handleRoleChange('doctor')}
                        disabled={loading}
                      >
                        Change to Doctor
                      </button>
                    )}
                    {formData.role !== 'admin' && (
                      <button
                        type="button"
                        className="btn-role-change btn-role-change-admin"
                        onClick={() => handleRoleChange('admin')}
                        disabled={loading}
                      >
                        Change to Admin
                      </button>
                    )}
                  </div>
                </div>

                <div className="form-group">
                  <label>Account Status</label>
                  <div className="checkbox-group">
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        name="is_active"
                        checked={formData.is_active}
                        onChange={handleChange}
                      />
                      <span>Active Account</span>
                    </label>
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        name="is_verified"
                        checked={formData.is_verified}
                        onChange={handleChange}
                      />
                      <span>Verified Account</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <div className="modal-actions">
              <button type="button" className="btn-secondary" onClick={onClose}>
                Cancel
              </button>
              <button type="submit" className="btn-primary" disabled={loading}>
                {loading ? 'Saving...' : (
                  <>
                    <Save size={18} />
                    Save Changes
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default UserDetailsModal;


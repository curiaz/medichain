import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, Eye, Stethoscope } from 'lucide-react';
import adminService from '../services/adminService';
import DoctorDetailsModal from './DoctorDetailsModal';
import './DoctorVerificationTable.css';

const DoctorVerificationTable = () => {
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDoctor, setSelectedDoctor] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [declineReason, setDeclineReason] = useState('');
  const [showDeclineModal, setShowDeclineModal] = useState(null);

  useEffect(() => {
    fetchPendingDoctors();
  }, []);

  const fetchPendingDoctors = async () => {
    try {
      setLoading(true);
      console.log('🔍 Fetching pending doctors...');
      const response = await adminService.getPendingDoctors();
      console.log('📥 Response received:', response);
      if (response && response.success) {
        console.log(`✅ Found ${response.count || response.doctors?.length || 0} pending doctors`);
        setDoctors(response.doctors || []);
      } else {
        console.warn('⚠️ Response not successful:', response);
        setDoctors([]);
      }
    } catch (error) {
      console.error('❌ Error fetching pending doctors:', error);
      console.error('Error details:', error.response?.data || error.message);
      setDoctors([]);
    } finally {
      setLoading(false);
    }
  };

  const handleView = (doctor) => {
    setSelectedDoctor(doctor);
    setShowDetailsModal(true);
  };

  const handleApprove = async (doctor) => {
    if (window.confirm(`Are you sure you want to approve Dr. ${doctor.user_info?.first_name || ''} ${doctor.user_info?.last_name || ''}?`)) {
      try {
        const response = await adminService.approveDoctor(doctor.id);
        if (response.success) {
          alert('Doctor approved successfully! An email notification has been sent.');
          fetchPendingDoctors();
        }
      } catch (error) {
        alert('Failed to approve doctor. Please try again.');
        console.error('Error:', error);
      }
    }
  };

  const handleDecline = async (doctorId) => {
    if (!declineReason.trim()) {
      alert('Please provide a reason for declining the application.');
      return;
    }

    try {
      const response = await adminService.declineDoctor(doctorId, declineReason);
      if (response.success) {
        alert('Doctor application declined. An email notification has been sent.');
        setShowDeclineModal(null);
        setDeclineReason('');
        fetchPendingDoctors();
      }
    } catch (error) {
      alert('Failed to decline doctor. Please try again.');
      console.error('Error:', error);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  const getDaysPending = (createdAt) => {
    if (!createdAt) return 'N/A';
    const created = new Date(createdAt);
    const now = new Date();
    const diffTime = Math.abs(now - created);
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  if (loading) {
    return (
      <div className="loading-state">
        <div className="spinner"></div>
        <p>Loading pending doctor applications...</p>
      </div>
    );
  }

  if (doctors.length === 0) {
    return (
      <div className="empty-state">
        <Stethoscope size={48} className="empty-icon" />
        <h3>No Pending Applications</h3>
        <p>All doctor verification requests have been processed.</p>
        <p style={{ fontSize: '0.75rem', color: '#999', marginTop: '0.5rem' }}>
          (Check browser console for debug info)
        </p>
      </div>
    );
  }

  return (
    <div className="doctor-verification-table">
      <div className="verification-header">
        <div>
          <h2>Doctor Verification Requests</h2>
          <p>{doctors.length} pending application{doctors.length !== 1 ? 's' : ''}</p>
        </div>
      </div>

      <div className="verification-table-container">
        <table className="verification-table">
          <thead>
            <tr>
              <th>Doctor</th>
              <th>Email</th>
              <th>Specialization</th>
              <th>Submitted</th>
              <th>Days Pending</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {doctors.map((doctor) => {
              const userInfo = doctor.user_info || {};
              const fullName = `${userInfo.first_name || ''} ${userInfo.last_name || ''}`.trim();
              
              return (
                <tr key={doctor.id}>
                  <td>
                    <div className="doctor-info-cell">
                      <div className="doctor-avatar">
                        <Stethoscope size={20} />
                      </div>
                      <div>
                        <div className="doctor-name">{fullName || 'N/A'}</div>
                        {userInfo.phone && (
                          <div className="doctor-phone">{userInfo.phone}</div>
                        )}
                      </div>
                    </div>
                  </td>
                  <td>{userInfo.email || 'N/A'}</td>
                  <td>
                    <span className="specialization-badge">{doctor.specialization || 'General Practitioner'}</span>
                  </td>
                  <td>{formatDate(doctor.created_at)}</td>
                  <td>
                    <span className="days-pending">{getDaysPending(doctor.created_at)} day{getDaysPending(doctor.created_at) !== 1 ? 's' : ''}</span>
                  </td>
                  <td>
                    <div className="action-buttons-group">
                      <button
                        className="action-btn action-btn-view"
                        onClick={() => handleView(doctor)}
                        title="View Details"
                      >
                        <Eye size={16} />
                        View
                      </button>
                      <button
                        className="action-btn action-btn-approve"
                        onClick={() => handleApprove(doctor)}
                        title="Approve"
                      >
                        <CheckCircle size={16} />
                        Approve
                      </button>
                      <button
                        className="action-btn action-btn-decline"
                        onClick={() => setShowDeclineModal(doctor.id)}
                        title="Decline"
                      >
                        <XCircle size={16} />
                        Decline
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {showDetailsModal && selectedDoctor && (
        <DoctorDetailsModal
          doctor={selectedDoctor}
          onClose={() => {
            setShowDetailsModal(false);
            setSelectedDoctor(null);
          }}
          onApprove={() => {
            handleApprove(selectedDoctor);
            setShowDetailsModal(false);
          }}
          onDecline={() => {
            setShowDetailsModal(false);
            setShowDeclineModal(selectedDoctor.id);
          }}
        />
      )}

      {showDeclineModal && (
        <div className="modal-overlay" onClick={() => setShowDeclineModal(null)}>
          <div className="modal-content decline-modal" onClick={(e) => e.stopPropagation()}>
            <h3>Decline Doctor Application</h3>
            <p>Please provide a reason for declining this application. The doctor will receive this message via email.</p>
            <textarea
              className="decline-reason-input"
              value={declineReason}
              onChange={(e) => setDeclineReason(e.target.value)}
              placeholder="Enter reason for declining..."
              rows={4}
            />
            <div className="modal-actions">
              <button
                className="btn-secondary"
                onClick={() => {
                  setShowDeclineModal(null);
                  setDeclineReason('');
                }}
              >
                Cancel
              </button>
              <button
                className="btn-danger"
                onClick={() => handleDecline(showDeclineModal)}
                disabled={!declineReason.trim()}
              >
                Decline Application
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DoctorVerificationTable;


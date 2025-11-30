import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, Eye, Clock, AlertCircle } from 'lucide-react';
import { API_CONFIG } from '../config/api';
import '../assets/styles/ESignatureApprovalTable.css';

const ESignatureApprovalTable = () => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [reviewNotes, setReviewNotes] = useState('');
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    loadRequests();
  }, [statusFilter]);

  const loadRequests = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('medichain_token');
      const response = await fetch(
        `${API_CONFIG.API_URL}/auth/admin/e-signatures/requests?status=${statusFilter}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setRequests(result.requests || []);
        }
      }
    } catch (err) {
      console.error('Error loading signature requests:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (requestId) => {
    if (!window.confirm('Are you sure you want to approve this signature update request?')) {
      return;
    }

    try {
      setProcessing(true);
      const token = localStorage.getItem('medichain_token');
      const response = await fetch(
        `${API_CONFIG.API_URL}/auth/admin/e-signatures/requests/${requestId}/approve`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            review_notes: reviewNotes
          })
        }
      );

      const result = await response.json();
      if (result.success) {
        alert('Signature update approved successfully!');
        setSelectedRequest(null);
        setReviewNotes('');
        loadRequests();
      } else {
        alert(result.error || 'Failed to approve request');
      }
    } catch (err) {
      console.error('Error approving request:', err);
      alert('Failed to approve request');
    } finally {
      setProcessing(false);
    }
  };

  const handleReject = async (requestId) => {
    if (!window.confirm('Are you sure you want to reject this signature update request?')) {
      return;
    }

    try {
      setProcessing(true);
      const token = localStorage.getItem('medichain_token');
      const response = await fetch(
        `${API_CONFIG.API_URL}/auth/admin/e-signatures/requests/${requestId}/reject`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            review_notes: reviewNotes
          })
        }
      );

      const result = await response.json();
      if (result.success) {
        alert('Signature update request rejected.');
        setSelectedRequest(null);
        setReviewNotes('');
        loadRequests();
      } else {
        alert(result.error || 'Failed to reject request');
      }
    } catch (err) {
      console.error('Error rejecting request:', err);
      alert('Failed to reject request');
    } finally {
      setProcessing(false);
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      pending: { color: '#f59e0b', icon: Clock, label: 'Pending Approval' },
      approved: { color: '#10b981', icon: CheckCircle, label: 'Approved' },
      rejected: { color: '#ef4444', icon: XCircle, label: 'Rejected' }
    };
    const badge = badges[status] || badges.pending;
    const Icon = badge.icon;
    return (
      <span className="status-badge" style={{ backgroundColor: `${badge.color}20`, color: badge.color }}>
        <Icon size={14} />
        {badge.label}
      </span>
    );
  };

  if (loading) {
    return <div className="loading-container">Loading signature requests...</div>;
  }

  return (
    <div className="e-signature-approval-table">
      <div className="table-header">
        <h2>E-Signature Update Requests</h2>
        <div className="filter-buttons">
          <button
            className={statusFilter === 'all' ? 'active' : ''}
            onClick={() => setStatusFilter('all')}
          >
            All
          </button>
          <button
            className={statusFilter === 'pending' ? 'active' : ''}
            onClick={() => setStatusFilter('pending')}
          >
            Pending
          </button>
          <button
            className={statusFilter === 'approved' ? 'active' : ''}
            onClick={() => setStatusFilter('approved')}
          >
            Approved
          </button>
          <button
            className={statusFilter === 'rejected' ? 'active' : ''}
            onClick={() => setStatusFilter('rejected')}
          >
            Rejected
          </button>
        </div>
      </div>

      {requests.length === 0 ? (
        <div className="empty-state">
          <AlertCircle size={48} />
          <p>No signature update requests found</p>
        </div>
      ) : (
        <div className="requests-grid">
          {requests.map((request) => (
            <div key={request.id} className="request-card">
              <div className="request-header">
                <div>
                  <h3>{request.doctor_name || 'Unknown Doctor'}</h3>
                  <p className="doctor-email">{request.doctor_email}</p>
                  <p className="prc-license">PRC: {request.prc_license || 'N/A'}</p>
                </div>
                {getStatusBadge(request.status)}
              </div>

              <div className="request-content">
                <div className="signatures-comparison">
                  <div className="signature-box">
                    <h4>Old Signature</h4>
                    {request.old_signature ? (
                      <img src={request.old_signature.signature_data} alt="Old Signature" />
                    ) : (
                      <p className="no-signature">No old signature</p>
                    )}
                  </div>
                  <div className="signature-box">
                    <h4>New Signature</h4>
                    <img src={request.new_signature.signature_data} alt="New Signature" />
                  </div>
                </div>

                <div className="request-details">
                  <div className="detail-item">
                    <strong>Reason:</strong>
                    <p>{request.reason}</p>
                  </div>
                  <div className="detail-item">
                    <strong>Requested:</strong>
                    <p>{new Date(request.created_at).toLocaleString()}</p>
                  </div>
                  {request.ip_address && (
                    <div className="detail-item">
                      <strong>IP Address:</strong>
                      <p>{request.ip_address}</p>
                    </div>
                  )}
                </div>

                {request.status === 'pending' && (
                  <div className="request-actions">
                    <button
                      className="btn-approve"
                      onClick={() => {
                        setSelectedRequest(request);
                        setReviewNotes('');
                      }}
                      disabled={processing}
                    >
                      <CheckCircle size={18} />
                      Approve
                    </button>
                    <button
                      className="btn-reject"
                      onClick={() => {
                        setSelectedRequest(request);
                        setReviewNotes('');
                      }}
                      disabled={processing}
                    >
                      <XCircle size={18} />
                      Reject
                    </button>
                  </div>
                )}

                {request.status !== 'pending' && request.reviewed_at && (
                  <div className="review-info">
                    <p>
                      <strong>{request.status === 'approved' ? 'Approved' : 'Rejected'}</strong> on{' '}
                      {new Date(request.reviewed_at).toLocaleString()}
                    </p>
                    {request.review_notes && (
                      <p className="review-notes">{request.review_notes}</p>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Review Modal */}
      {selectedRequest && (
        <div className="review-modal-overlay" onClick={() => setSelectedRequest(null)}>
          <div className="review-modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Review Signature Update Request</h3>
            <div className="review-form">
              <label>
                Review Notes (Optional):
                <textarea
                  value={reviewNotes}
                  onChange={(e) => setReviewNotes(e.target.value)}
                  placeholder="Add any notes about your decision..."
                  rows={4}
                />
              </label>
              <div className="review-actions">
                <button
                  className="btn-approve"
                  onClick={() => handleApprove(selectedRequest.id)}
                  disabled={processing}
                >
                  Approve & Replace
                </button>
                <button
                  className="btn-reject"
                  onClick={() => handleReject(selectedRequest.id)}
                  disabled={processing}
                >
                  Reject Request
                </button>
                <button
                  className="btn-cancel"
                  onClick={() => {
                    setSelectedRequest(null);
                    setReviewNotes('');
                  }}
                  disabled={processing}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ESignatureApprovalTable;




import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { CreditCard, Check, X, Clock, DollarSign, User, Calendar } from 'lucide-react';
import axios from 'axios';
import { API_CONFIG } from '../config/api';
import '../assets/styles/AdminDashboard.css';

const PaymentManagement = () => {
  const { getFirebaseToken } = useAuth();
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // all, pending, paid
  const [editingReference, setEditingReference] = useState(null);
  const [referenceInput, setReferenceInput] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchPayments();
  }, []);

  const fetchPayments = async () => {
    try {
      setLoading(true);
      setError(null);
      const token = await getFirebaseToken();
      
      const response = await axios.get(
        `${API_CONFIG.API_URL}/admin/payments`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.data.success) {
        setPayments(response.data.payments || []);
      } else {
        setError(response.data.error || 'Failed to load payments');
      }
    } catch (err) {
      console.error('Error fetching payments:', err);
      setError(err.response?.data?.error || 'Failed to load payments');
    } finally {
      setLoading(false);
    }
  };

  const handleAddReference = async (transactionId) => {
    if (!referenceInput.trim()) {
      setError('Please enter a GCash reference number');
      return;
    }

    try {
      setSaving(true);
      setError(null);
      const token = await getFirebaseToken();
      
      const response = await axios.post(
        `${API_CONFIG.API_URL}/admin/payments/${transactionId}/gcash-reference`,
        {
          gcash_reference_number: referenceInput.trim()
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.data.success) {
        setEditingReference(null);
        setReferenceInput('');
        fetchPayments(); // Refresh list
      } else {
        setError(response.data.error || 'Failed to add reference number');
      }
    } catch (err) {
      console.error('Error adding reference:', err);
      setError(err.response?.data?.error || 'Failed to add reference number');
    } finally {
      setSaving(false);
    }
  };

  const filteredPayments = payments.filter(payment => {
    if (filter === 'pending') return payment.status === 'pending';
    if (filter === 'paid') return payment.status === 'paid';
    return true;
  });

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="admin-payment-loading">
        <div className="spinner"></div>
        <p>Loading payments...</p>
      </div>
    );
  }

  return (
    <div className="admin-payment-management">
      <div className="admin-payment-header">
        <h2>Payment Management</h2>
        <p>Manage GCash payments and verify reference numbers</p>
      </div>

      {error && (
        <div className="admin-payment-error">
          <X size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* Filter Tabs */}
      <div className="admin-payment-filters">
        <button
          className={`admin-payment-filter-btn ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          All Payments ({payments.length})
        </button>
        <button
          className={`admin-payment-filter-btn ${filter === 'pending' ? 'active' : ''}`}
          onClick={() => setFilter('pending')}
        >
          Pending ({payments.filter(p => p.status === 'pending').length})
        </button>
        <button
          className={`admin-payment-filter-btn ${filter === 'paid' ? 'active' : ''}`}
          onClick={() => setFilter('paid')}
        >
          Paid ({payments.filter(p => p.status === 'paid').length})
        </button>
      </div>

      {/* Payments Table */}
      <div className="admin-payment-table-container">
        {filteredPayments.length === 0 ? (
          <div className="admin-payment-empty">
            <CreditCard size={48} />
            <p>No payments found</p>
          </div>
        ) : (
          <table className="admin-payment-table">
            <thead>
              <tr>
                <th>Transaction ID</th>
                <th>User</th>
                <th>Amount</th>
                <th>Method</th>
                <th>Status</th>
                <th>GCash Reference</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredPayments.map((payment) => (
                <tr key={payment.id}>
                  <td className="payment-transaction-id">
                    {payment.transaction_id}
                  </td>
                  <td>
                    <div className="payment-user-info">
                      <User size={16} />
                      <div>
                        <div className="payment-user-name">{payment.user_name || 'Unknown'}</div>
                        <div className="payment-user-email">{payment.user_email || ''}</div>
                      </div>
                    </div>
                  </td>
                  <td className="payment-amount">
                    <DollarSign size={16} />
                    ₱{parseFloat(payment.amount || 0).toFixed(2)}
                  </td>
                  <td>
                    <span className={`payment-method-badge payment-method-${payment.payment_method}`}>
                      {payment.payment_method?.replace('_', ' ').toUpperCase() || 'N/A'}
                    </span>
                  </td>
                  <td>
                    <span className={`payment-status-badge payment-status-${payment.status}`}>
                      {payment.status?.toUpperCase() || 'PENDING'}
                    </span>
                  </td>
                  <td>
                    {payment.gcash_reference_number ? (
                      <span className="payment-reference-verified">
                        <Check size={16} />
                        {payment.gcash_reference_number}
                      </span>
                    ) : (
                      <span className="payment-reference-missing">Not added</span>
                    )}
                  </td>
                  <td>
                    <div className="payment-date-info">
                      <Calendar size={14} />
                      {formatDate(payment.created_at)}
                    </div>
                  </td>
                  <td>
                    {payment.status === 'pending' && payment.payment_method === 'gcash' && !payment.gcash_reference_number ? (
                      editingReference === payment.transaction_id ? (
                        <div className="payment-reference-form">
                          <input
                            type="text"
                            className="payment-reference-input"
                            placeholder="Enter GCash reference"
                            value={referenceInput}
                            onChange={(e) => setReferenceInput(e.target.value.toUpperCase())}
                            disabled={saving}
                          />
                          <div className="payment-reference-actions">
                            <button
                              className="payment-reference-save-btn"
                              onClick={() => handleAddReference(payment.transaction_id)}
                              disabled={saving || !referenceInput.trim()}
                            >
                              {saving ? 'Saving...' : 'Save'}
                            </button>
                            <button
                              className="payment-reference-cancel-btn"
                              onClick={() => {
                                setEditingReference(null);
                                setReferenceInput('');
                              }}
                              disabled={saving}
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      ) : (
                        <button
                          className="payment-add-reference-btn"
                          onClick={() => {
                            setEditingReference(payment.transaction_id);
                            setReferenceInput('');
                          }}
                        >
                          <CreditCard size={16} />
                          Add Reference
                        </button>
                      )
                    ) : payment.status === 'paid' ? (
                      <span className="payment-verified-badge">
                        <Check size={16} />
                        Verified
                      </span>
                    ) : null}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default PaymentManagement;


import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import '../assets/styles/AuditLedger.css';

import { API_CONFIG } from '../config/api';
const API_BASE_URL = API_CONFIG?.BASE_URL || process.env.REACT_APP_API_URL || 'https://medichainn.onrender.com';

const AuditLedger = () => {
  const { user, getFirebaseToken } = useAuth();
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    admin_id: '',
    action_type: '',
    entity_type: '',
    entity_id: '',
    start_date: '',
    end_date: ''
  });
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 50,
    total: 0,
    total_pages: 0
  });
  const [expandedEntry, setExpandedEntry] = useState(null);

  useEffect(() => {
    if (user) {
      fetchLedgerEntries();
    }
  }, [pagination.page, filters, user]);

  const fetchLedgerEntries = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get authentication token with multiple fallback strategies
      let token = null;
      
      // Strategy 1: Try to get Firebase token using AuthContext helper
      try {
        if (getFirebaseToken) {
          token = await getFirebaseToken();
        }
      } catch (authContextError) {
        console.warn("Could not get token via AuthContext:", authContextError);
      }
      
      // Strategy 2: Try to get Firebase token from auth.currentUser
      if (!token) {
        try {
          const { auth } = await import('../config/firebase');
          const currentUser = auth.currentUser;
          if (currentUser) {
            token = await currentUser.getIdToken(true);
          }
        } catch (firebaseError) {
          console.warn("Could not get Firebase token:", firebaseError);
        }
      }
      
      // Strategy 3: Fallback to stored tokens
      if (!token) {
        token = sessionStorage.getItem('firebase_id_token') || 
                localStorage.getItem('firebase_id_token') ||
                localStorage.getItem('medichain_token');
      }
      
      if (!token) {
        setError('Authentication required. Please log in again.');
        setLoading(false);
        return;
      }
      const params = new URLSearchParams({
        page: pagination.page.toString(),
        limit: pagination.limit.toString()
      });

      // Add filters to params
      Object.entries(filters).forEach(([key, value]) => {
        if (value) {
          params.append(key, value);
        }
      });

      const response = await axios.get(`${API_BASE_URL}/api/admin/audit/ledger?${params.toString()}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.data.success) {
        setEntries(response.data.entries || []);
        setPagination(prev => ({
          ...prev,
          total: response.data.pagination?.total || 0,
          total_pages: response.data.pagination?.total_pages || 0
        }));
        // Clear error if successful (even if no entries)
        if (response.data.entries && response.data.entries.length === 0) {
          setError(null); // No error, just empty
        }
      } else {
        setError(response.data.error || 'Failed to fetch audit ledger');
      }
    } catch (err) {
      console.error('Error fetching audit ledger:', err);
      console.error('Full error details:', {
        status: err.response?.status,
        statusText: err.response?.statusText,
        data: err.response?.data,
        message: err.message,
        config: err.config
      });
      
      // Extract error message from various possible formats
      let errorMessage = 'Failed to fetch audit ledger';
      if (err.response?.data) {
        if (err.response.data.error) {
          errorMessage = err.response.data.error;
        } else if (err.response.data.message) {
          errorMessage = err.response.data.message;
        } else if (typeof err.response.data === 'string') {
          errorMessage = err.response.data;
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      // Add status code info if available
      if (err.response?.status) {
        errorMessage += ` (Status: ${err.response.status})`;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPagination(prev => ({ ...prev, page: 1 })); // Reset to first page
  };

  const handlePageChange = (newPage) => {
    setPagination(prev => ({ ...prev, page: newPage }));
  };

  const toggleEntryExpansion = (entryId) => {
    setExpandedEntry(expandedEntry === entryId ? null : entryId);
  };

  const getActionBadgeClass = (actionType) => {
    const actionMap = {
      'CREATE': 'badge-create',
      'UPDATE': 'badge-update',
      'DELETE': 'badge-delete',
      'VIEW': 'badge-view',
      'APPROVE': 'badge-approve',
      'DECLINE': 'badge-decline',
      'UPDATE_ROLE': 'badge-role',
      'UPDATE_STATUS': 'badge-status'
    };
    return actionMap[actionType] || 'badge-default';
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading && entries.length === 0) {
    return (
      <div className="audit-ledger-loading">
        <div className="spinner"></div>
        <p>Loading audit ledger...</p>
      </div>
    );
  }

  return (
    <div className="audit-ledger-container">
      <div className="audit-ledger-header">
        <h2>Blockchain Audit Ledger</h2>
        <p className="audit-ledger-subtitle">
          Immutable history of all admin actions - Who did what, when, and on whose data
        </p>
      </div>

      {/* Filters */}
      <div className="audit-ledger-filters">
        <div className="filter-row">
          <div className="filter-group">
            <label>Action Type</label>
            <select
              value={filters.action_type}
              onChange={(e) => handleFilterChange('action_type', e.target.value)}
            >
              <option value="">All Actions</option>
              <option value="CREATE">Create</option>
              <option value="UPDATE">Update</option>
              <option value="DELETE">Delete</option>
              <option value="VIEW">View</option>
              <option value="APPROVE">Approve</option>
              <option value="DECLINE">Decline</option>
              <option value="UPDATE_ROLE">Update Role</option>
              <option value="UPDATE_STATUS">Update Status</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Entity Type</label>
            <select
              value={filters.entity_type}
              onChange={(e) => handleFilterChange('entity_type', e.target.value)}
            >
              <option value="">All Entities</option>
              <option value="user">User</option>
              <option value="doctor_profile">Doctor Profile</option>
              <option value="appointment">Appointment</option>
              <option value="prescription">Prescription</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Admin ID</label>
            <input
              type="text"
              placeholder="Filter by admin..."
              value={filters.admin_id}
              onChange={(e) => handleFilterChange('admin_id', e.target.value)}
            />
          </div>

          <div className="filter-group">
            <label>Entity ID</label>
            <input
              type="text"
              placeholder="Filter by entity..."
              value={filters.entity_id}
              onChange={(e) => handleFilterChange('entity_id', e.target.value)}
            />
          </div>
        </div>

        <div className="filter-row">
          <div className="filter-group">
            <label>Start Date</label>
            <input
              type="date"
              value={filters.start_date}
              onChange={(e) => handleFilterChange('start_date', e.target.value)}
            />
          </div>

          <div className="filter-group">
            <label>End Date</label>
            <input
              type="date"
              value={filters.end_date}
              onChange={(e) => handleFilterChange('end_date', e.target.value)}
            />
          </div>

          <button className="btn-clear-filters" onClick={() => {
            setFilters({
              admin_id: '',
              action_type: '',
              entity_type: '',
              entity_id: '',
              start_date: '',
              end_date: ''
            });
            setPagination(prev => ({ ...prev, page: 1 }));
          }}>
            Clear Filters
          </button>
        </div>
      </div>

      {error && (
        <div className="audit-ledger-error">
          <p style={{ fontSize: '1.1rem', fontWeight: '600', marginBottom: '0.5rem' }}>Error: {error}</p>
          <p style={{ fontSize: '0.9rem', opacity: 0.9 }}>
            Check browser console for more details. Make sure the backend server is running.
          </p>
        </div>
      )}

      {/* Ledger Entries - Blockchain Chain View */}
      <div className="audit-ledger-entries">
        {!loading && entries.length === 0 && !error ? (
          <div className="audit-ledger-empty">
            <p>No audit entries found</p>
            <p>
              Perform admin actions (create/update users, approve doctors) to see entries here.
            </p>
          </div>
        ) : entries.length === 0 && error ? null : (
          <div className="blockchain-chain">
            {entries.map((entry, index) => {
              // For chain verification: previous entry in the DISPLAYED list (newest first)
              // But we need to check if THIS entry's previous_hash matches the NEXT entry's current_hash
              // Because entries are displayed newest first, but chain goes oldest to newest
              const nextEntry = index < entries.length - 1 ? entries[index + 1] : null;
              // This entry's previous_hash should match the next (older) entry's current_hash
              const isLinked = nextEntry ? entry.previous_hash === nextEntry.current_hash : true;
              
              return (
                <div key={entry.id} className="blockchain-block-wrapper">
                  {/* Chain Link Line - Show link to next (older) block */}
                  {index < entries.length - 1 && (
                    <div className={`chain-link ${isLinked ? 'linked' : 'broken'}`}>
                      <div className="chain-link-line"></div>
                      <div className="chain-link-hash">
                        {isLinked ? (
                          <span className="hash-match">Linked to Block #{nextEntry?.block_number}</span>
                        ) : (
                          <span className="hash-mismatch">Chain Broken</span>
                        )}
                      </div>
                    </div>
                  )}
                  
                  {/* Block */}
                  <div className={`blockchain-block ${expandedEntry === entry.id ? 'expanded' : ''}`}>
                    <div className="block-header" onClick={() => toggleEntryExpansion(entry.id)}>
                      <div className="block-number">Block #{entry.block_number}</div>
                      <div className="block-content">
                        <div className="block-action">
                          <span className={`action-badge ${getActionBadgeClass(entry.action_type)}`}>
                            {entry.action_type}
                          </span>
                          <span className="block-description">{entry.action_description}</span>
                        </div>
                        <div className="block-meta">
                          <span className="block-admin">{entry.admin_name || entry.admin_email || entry.admin_id}</span>
                          <span className="block-separator">•</span>
                          <span className="block-entity">{entry.entity_type}</span>
                          <span className="block-separator">•</span>
                          <span className="block-date">{formatDate(entry.created_at)}</span>
                        </div>
                      </div>
                      <div className="block-hash-preview">
                        <div className="hash-label">Hash:</div>
                        <div className="hash-preview">{entry.current_hash?.substring(0, 16)}...</div>
                      </div>
                      <div className="block-toggle">{expandedEntry === entry.id ? '−' : '+'}</div>
                    </div>
                    
                    {expandedEntry === entry.id && (
                      <div className="block-details">
                        <div className="blockchain-hash-section">
                          <div className="hash-row">
                            <div className="hash-item">
                              <div className="hash-label">Previous Hash</div>
                              <div className="hash-value-full">
                                {entry.previous_hash || <span className="genesis">Genesis Block (No Previous Hash)</span>}
                              </div>
                              {nextEntry && (
                                <div className="hash-link-info">
                                  {isLinked ? (
                                    <span className="link-verified">Linked to Block #{nextEntry.block_number}</span>
                                  ) : (
                                    <span className="link-broken">Chain link broken - hash mismatch</span>
                                  )}
                                </div>
                              )}
                              {!nextEntry && entry.previous_hash && (
                                <div className="hash-link-info">
                                  <span className="link-verified">Genesis Block (First Entry)</span>
                                </div>
                              )}
                            </div>
                            <div className="hash-arrow">→</div>
                            <div className="hash-item">
                              <div className="hash-label">Current Hash (SHA-256)</div>
                              <div className="hash-value-full">{entry.current_hash}</div>
                              <div className="hash-link-info">
                                <span className="hash-verified">SHA-256 Verified</span>
                              </div>
                            </div>
                          </div>
                        </div>
                        
                        <div className="block-info-grid">
                          <div className="info-item">
                            <div className="info-label">Admin</div>
                            <div className="info-value">{entry.admin_name || entry.admin_email || entry.admin_id}</div>
                            <div className="info-sub">{entry.admin_id}</div>
                          </div>
                          <div className="info-item">
                            <div className="info-label">Action</div>
                            <div className="info-value">{entry.action_type}</div>
                            <div className="info-sub">{entry.entity_type}</div>
                          </div>
                          <div className="info-item">
                            <div className="info-label">Entity ID</div>
                            <div className="info-value">{entry.entity_id || 'N/A'}</div>
                          </div>
                          <div className="info-item">
                            <div className="info-label">IP Address</div>
                            <div className="info-value">{entry.ip_address || 'N/A'}</div>
                          </div>
                        </div>
                        
                        {entry.data_changes && Object.keys(entry.data_changes).length > 0 && (
                          <div className="block-changes">
                            <div className="changes-title">Data Changes</div>
                            <div className="changes-list">
                              {Object.entries(entry.data_changes).map(([key, change]) => (
                                <div key={key} className="change-row">
                                  <div className="change-field">{key}</div>
                                  {typeof change === 'object' && change !== null ? (
                                    <div className="change-comparison">
                                      <div className="change-before-value">
                                        <span className="change-label">Before:</span>
                                        {JSON.stringify(change.before)}
                                      </div>
                                      <div className="change-arrow">→</div>
                                      <div className="change-after-value">
                                        <span className="change-label">After:</span>
                                        {JSON.stringify(change.after)}
                                      </div>
                                    </div>
                                  ) : (
                                    <div className="change-single">{JSON.stringify(change)}</div>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {(entry.data_before || entry.data_after) && (
                          <div className="block-data">
                            {entry.data_before && (
                              <div className="data-section">
                                <div className="data-title">Data Before</div>
                                <pre className="data-json">{JSON.stringify(entry.data_before, null, 2)}</pre>
                              </div>
                            )}
                            {entry.data_after && (
                              <div className="data-section">
                                <div className="data-title">Data After</div>
                                <pre className="data-json">{JSON.stringify(entry.data_after, null, 2)}</pre>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Pagination */}
      {pagination.total_pages > 1 && (
        <div className="audit-ledger-pagination">
          <button
            onClick={() => handlePageChange(pagination.page - 1)}
            disabled={pagination.page === 1}
            className="btn-pagination"
          >
            Previous
          </button>
          <span className="pagination-info">
            Page {pagination.page} of {pagination.total_pages} ({pagination.total} total entries)
          </span>
          <button
            onClick={() => handlePageChange(pagination.page + 1)}
            disabled={pagination.page >= pagination.total_pages}
            className="btn-pagination"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default AuditLedger;


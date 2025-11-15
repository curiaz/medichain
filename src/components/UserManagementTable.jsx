import React, { useState, useEffect } from 'react';
import { Search, Filter, Edit, Trash2, UserPlus, MoreVertical, CheckCircle, XCircle, Shield, User, Stethoscope } from 'lucide-react';
import adminService from '../services/adminService';
import UserDetailsModal from './UserDetailsModal';
import CreateUserModal from './CreateUserModal';
import './UserManagementTable.css';

const UserManagementTable = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedUser, setSelectedUser] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [pagination, setPagination] = useState({ page: 1, limit: 20, total: 0, total_pages: 0 });
  const [actionMenuOpen, setActionMenuOpen] = useState(null);

  useEffect(() => {
    fetchUsers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [roleFilter, statusFilter, pagination.page, searchTerm]);

  // Close action menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (actionMenuOpen && !event.target.closest('.actions-cell')) {
        setActionMenuOpen(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [actionMenuOpen]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const filters = {
        page: pagination.page,
        limit: pagination.limit,
      };

      if (roleFilter !== 'all') {
        filters.role = roleFilter;
      }

      if (statusFilter !== 'all') {
        filters.is_active = statusFilter === 'active';
      }

      if (searchTerm) {
        filters.search = searchTerm;
      }

      const response = await adminService.getUsers(filters);
      if (response.success) {
        setUsers(response.users);
        setPagination(response.pagination);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handleRoleChange = (e) => {
    setRoleFilter(e.target.value);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handleStatusChange = (e) => {
    setStatusFilter(e.target.value);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handleEdit = (user) => {
    setSelectedUser(user);
    setShowDetailsModal(true);
    setActionMenuOpen(null);
  };

  const handleDelete = async (user) => {
    if (window.confirm(`Are you sure you want to delete user ${user.first_name} ${user.last_name}?`)) {
      try {
        const response = await adminService.deleteUser(user.firebase_uid);
        if (response.success) {
          fetchUsers();
        }
      } catch (error) {
        console.error('Error deleting user:', error);
        alert('Failed to delete user. Please try again.');
      }
    }
    setActionMenuOpen(null);
  };

  const handleToggleStatus = async (user) => {
    try {
      const response = await adminService.updateUserStatus(user.firebase_uid, !user.is_active);
      if (response.success) {
        fetchUsers();
      }
    } catch (error) {
      console.error('Error updating user status:', error);
      alert('Failed to update user status. Please try again.');
    }
    setActionMenuOpen(null);
  };

  const handleUserUpdated = () => {
    fetchUsers();
    setShowDetailsModal(false);
    setSelectedUser(null);
  };

  const handleUserCreated = () => {
    fetchUsers();
    setShowCreateModal(false);
  };

  const getRoleIcon = (role) => {
    switch (role) {
      case 'admin':
        return <Shield size={16} className="role-icon role-icon-admin" />;
      case 'doctor':
        return <Stethoscope size={16} className="role-icon role-icon-doctor" />;
      default:
        return <User size={16} className="role-icon role-icon-patient" />;
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  };

  return (
    <div className="user-management-table">
      <div className="user-management-header">
        <div className="user-management-title">
          <h2>User Management</h2>
          <p>Manage all users in the system</p>
        </div>
        <button 
          className="btn-create-user"
          onClick={() => setShowCreateModal(true)}
        >
          <UserPlus size={20} />
          Create User
        </button>
      </div>

      <div className="user-management-filters">
        <div className="search-box">
          <Search size={20} className="search-icon" />
          <input
            type="text"
            placeholder="Search by name, email, or phone..."
            value={searchTerm}
            onChange={handleSearch}
            className="search-input"
          />
        </div>

        <div className="filter-group">
          <Filter size={18} />
          <select value={roleFilter} onChange={handleRoleChange} className="filter-select">
            <option value="all">All Roles</option>
            <option value="patient">Patients</option>
            <option value="doctor">Doctors</option>
            <option value="admin">Admins</option>
          </select>

          <select value={statusFilter} onChange={handleStatusChange} className="filter-select">
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading users...</p>
        </div>
      ) : users.length === 0 ? (
        <div className="empty-state">
          <User size={48} className="empty-icon" />
          <p>No users found</p>
        </div>
      ) : (
        <>
          <div className="table-container">
            <table className="users-table">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.firebase_uid}>
                    <td>
                      <div className="user-info">
                        <div className="user-avatar">
                          {user.first_name?.[0]?.toUpperCase() || 'U'}
                        </div>
                        <div>
                          <div className="user-name">
                            {user.first_name} {user.last_name}
                          </div>
                          {user.phone && (
                            <div className="user-phone">{user.phone}</div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td>{user.email}</td>
                    <td>
                      <div className="role-badge">
                        {getRoleIcon(user.role)}
                        <span className="role-text">{user.role}</span>
                      </div>
                    </td>
                    <td>
                      {user.is_active ? (
                        <span className="status-badge status-active">
                          <CheckCircle size={14} />
                          Active
                        </span>
                      ) : (
                        <span className="status-badge status-inactive">
                          <XCircle size={14} />
                          Inactive
                        </span>
                      )}
                    </td>
                    <td>{formatDate(user.created_at)}</td>
                    <td>
                      <div className="actions-cell">
                        <button
                          className="action-btn"
                          onClick={() => setActionMenuOpen(actionMenuOpen === user.firebase_uid ? null : user.firebase_uid)}
                        >
                          <MoreVertical size={18} />
                        </button>
                        {actionMenuOpen === user.firebase_uid && (
                          <div className="action-menu">
                            <button onClick={() => handleEdit(user)} className="action-menu-item">
                              <Edit size={16} />
                              Edit
                            </button>
                            <button onClick={() => handleToggleStatus(user)} className="action-menu-item">
                              {user.is_active ? (
                                <>
                                  <XCircle size={16} />
                                  Deactivate
                                </>
                              ) : (
                                <>
                                  <CheckCircle size={16} />
                                  Activate
                                </>
                              )}
                            </button>
                            <button onClick={() => handleDelete(user)} className="action-menu-item action-menu-item-danger">
                              <Trash2 size={16} />
                              Delete
                            </button>
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {pagination.total_pages > 1 && (
            <div className="pagination">
              <button
                className="pagination-btn"
                onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
                disabled={pagination.page === 1}
              >
                Previous
              </button>
              <span className="pagination-info">
                Page {pagination.page} of {pagination.total_pages} ({pagination.total} total)
              </span>
              <button
                className="pagination-btn"
                onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
                disabled={pagination.page >= pagination.total_pages}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}

      {showDetailsModal && selectedUser && (
        <UserDetailsModal
          user={selectedUser}
          onClose={() => {
            setShowDetailsModal(false);
            setSelectedUser(null);
          }}
          onUpdate={handleUserUpdated}
        />
      )}

      {showCreateModal && (
        <CreateUserModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={handleUserCreated}
        />
      )}
    </div>
  );
};

export default UserManagementTable;


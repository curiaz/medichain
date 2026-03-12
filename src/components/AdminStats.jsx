import React, { useState, useEffect } from 'react';
import { Users, UserCheck, Activity, Shield, Stethoscope } from 'lucide-react';
import adminService from '../services/adminService';

const AdminStats = () => {
  const [stats, setStats] = useState({
    total_users: 0,
    patients: 0,
    doctors: 0,
    admins: 0,
    active_users: 0,
    inactive_users: 0,
    verified_doctors: 0,
    recent_registrations: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await adminService.getStats();
      if (response.success) {
        setStats(response.stats);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="admin-stats-loading">
        <div className="spinner"></div>
        <p>Loading statistics...</p>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Users',
      value: stats.total_users,
      icon: Users,
      color: 'blue',
      change: null
    },
    {
      title: 'Patients',
      value: stats.patients,
      icon: UserCheck,
      color: 'green',
      change: null
    },
    {
      title: 'Doctors',
      value: stats.doctors,
      icon: Stethoscope,
      color: 'purple',
      subtitle: `${stats.verified_doctors} verified`
    },
    {
      title: 'Admins',
      value: stats.admins,
      icon: Shield,
      color: 'red',
      change: null
    },
    {
      title: 'Active Users',
      value: stats.active_users,
      icon: Activity,
      color: 'green',
      subtitle: `${stats.inactive_users} inactive`
    },
    {
      title: 'New Registrations',
      value: stats.recent_registrations,
      icon: Activity,
      color: 'blue',
      subtitle: 'Last 30 days'
    }
  ];

  return (
    <div className="admin-stats">
      <div className="admin-stats-grid">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className={`admin-stat-card admin-stat-card-${stat.color}`}>
              <div className="admin-stat-card-icon">
                <Icon size={28} />
              </div>
              <div className="admin-stat-card-content">
                <h3 className="admin-stat-card-title">{stat.title}</h3>
                <p className="admin-stat-card-value">{stat.value}</p>
                {stat.subtitle && (
                  <p className="admin-stat-card-subtitle">{stat.subtitle}</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default AdminStats;


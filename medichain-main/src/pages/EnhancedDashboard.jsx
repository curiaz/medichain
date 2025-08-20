import React, { useState, useEffect } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import DashboardStats from '../components/DashboardStats';
import QuickActions from '../components/QuickActions';
import { useAuth } from '../context/AuthContext';
import { Activity, Clock, CheckCircle, AlertCircle } from 'lucide-react';

const EnhancedDashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalPatients: 1247,
    recentDiagnoses: 89,
    blockchainRecords: 3421,
    aiAccuracy: '96.8%',
    pendingApprovals: 12,
    activeRecords: 2847
  });

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading dashboard data
    setTimeout(() => {
      setLoading(false);
    }, 1000);
  }, []);

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Welcome Section */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white">
          <h1 className="text-2xl font-bold mb-2">
            Welcome back, {user?.name}!
          </h1>
          <p className="text-blue-100">
            {user?.role === 'doctor' 
              ? 'Manage your patients and track medical insights with AI-powered analytics.'
              : 'Track your health journey and access your medical records securely.'
            }
          </p>
        </div>

        {/* Stats Overview */}
        <DashboardStats stats={stats} />

        {/* Quick Actions */}
        <QuickActions userRole={user?.role} />

        {/* Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Activity className="mr-2 text-blue-500" size={20} />
              Recent Activity
            </h3>
            <div className="space-y-3">
              <div className="flex items-center p-3 bg-gray-50 rounded-lg">
                <CheckCircle className="text-green-500 mr-3" size={16} />
                <div>
                  <p className="text-sm font-medium">New diagnosis completed</p>
                  <p className="text-xs text-gray-500">2 hours ago</p>
                </div>
              </div>
              <div className="flex items-center p-3 bg-gray-50 rounded-lg">
                <Clock className="text-orange-500 mr-3" size={16} />
                <div>
                  <p className="text-sm font-medium">Appointment scheduled</p>
                  <p className="text-xs text-gray-500">5 hours ago</p>
                </div>
              </div>
              <div className="flex items-center p-3 bg-gray-50 rounded-lg">
                <AlertCircle className="text-red-500 mr-3" size={16} />
                <div>
                  <p className="text-sm font-medium">Prescription updated</p>
                  <p className="text-xs text-gray-500">1 day ago</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              System Status
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Blockchain Sync</span>
                <span className="text-sm font-medium text-green-600">Active</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">AI Model Status</span>
                <span className="text-sm font-medium text-green-600">Running</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Data Encryption</span>
                <span className="text-sm font-medium text-green-600">Enabled</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Last Backup</span>
                <span className="text-sm font-medium text-gray-600">2 hours ago</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default EnhancedDashboard;

import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { X, User, LogOut, Home, Users, FileText, Calendar, Activity, ChevronDown, TrendingUp, Brain, Database, Bell, Settings, AlertCircle } from 'lucide-react';

const DashboardLayout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  // Role-based menu items
  const doctorMenu = [
    { name: 'Dashboard', icon: Home, path: '/dashboard', color: 'text-blue-500' },
    { name: 'Patients', icon: Users, path: '/patients', color: 'text-green-500' },
    { name: 'Diagnoses', icon: FileText, path: '/diagnoses', color: 'text-purple-500' },
    { name: 'Appointments', icon: Calendar, path: '/appointments', color: 'text-orange-500' },
    { name: 'Analytics', icon: TrendingUp, path: '/analytics', color: 'text-pink-500' },
    { name: 'Blockchain Records', icon: Database, path: '/records', color: 'text-indigo-500' },
  ];

  const patientMenu = [
    { name: 'Dashboard', icon: Home, path: '/dashboard', color: 'text-blue-500' },
    { name: 'Health Record', icon: FileText, path: '/health-record', color: 'text-green-500' },
    { name: 'Appointments', icon: Calendar, path: '/appointments', color: 'text-orange-500' },
    { name: 'Notifications', icon: Bell, path: '/notifications', color: 'text-red-500' },
    { name: 'AI Assistant', icon: Brain, path: '/ai-assistant', color: 'text-purple-500' },
    { name: 'Health Tracking', icon: Activity, path: '/health-tracking', color: 'text-pink-500' },
  ];

  const adminMenu = [
    { name: 'Dashboard', icon: Home, path: '/dashboard', color: 'text-blue-500' },
    { name: 'User Management', icon: Users, path: '/dashboard', color: 'text-green-500' },
    { name: 'System Settings', icon: Settings, path: '/admin/settings', color: 'text-purple-500' },
    { name: 'Reports', icon: TrendingUp, path: '/admin/reports', color: 'text-orange-500' },
  ];

  const getMenuItems = () => {
    const userRole = user?.role || user?.profile?.role;
    if (userRole === 'admin') {
      return adminMenu;
    } else if (userRole === 'doctor') {
      return doctorMenu;
    } else {
      return patientMenu;
    }
  };

  const menuItems = getMenuItems();

  const handleLogoutClick = () => {
    setProfileOpen(false);
    setShowLogoutConfirm(true);
  };

  const handleLogoutConfirm = () => {
    setShowLogoutConfirm(false);
    logout();
    navigate('/');
  };

  const handleLogoutCancel = () => {
    setShowLogoutConfirm(false);
  };

  const handleProfileClick = () => {
    console.log('Profile clicked - navigating to profile page');
    // Navigate to appropriate profile page based on user role
    if (user?.profile?.role === 'doctor') {
      navigate('/doctor-profile');
    } else {
      navigate('/profile');
    }
    setProfileOpen(false);
  };

  const toggleProfileDropdown = () => {
    console.log('Profile dropdown toggled');
    setProfileOpen(!profileOpen);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        
        {/* Sidebar header */}
        <div className="flex items-center justify-between h-16 px-4 border-b">
          <div className="flex items-center">
            <img 
              src="/medichain-logo.svg" 
              alt="MediChain" 
              className="h-8 w-auto"
            />
            <span className="ml-2 text-lg font-bold text-gray-800">MediChain</span>
          </div>
          <button 
            className="lg:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={24} className="text-gray-600" />
          </button>
        </div>

        {/* User info */}
        <div className="p-4 border-b">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <span className="text-white font-semibold">
                {(user?.profile?.first_name || user?.first_name || user?.name || 'U').charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-900">
                {user?.profile?.first_name || user?.first_name || user?.name || 'User'}
              </p>
              <p className="text-xs text-gray-500 capitalize">{user?.role || user?.profile?.role || 'user'}</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="mt-4 px-2">
          {menuItems.map((item) => {
            const isActive = window.location.pathname === item.path;
            return (
              <a
                key={item.name}
                href={item.path}
                className={`flex items-center px-2 py-2 mb-1 text-sm font-medium rounded-lg transition-colors duration-200 ${
                  isActive 
                    ? 'bg-blue-50 text-blue-700' 
                    : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                }`}
              >
                <item.icon size={20} className={`mr-3 ${item.color}`} />
                {item.name}
              </a>
            );
          })}
        </nav>
      </div>

      {/* Main content */}
      <div className="lg:ml-64 flex-1">
        {/* Top navigation */}
        <header className="bg-white shadow-sm border-b sticky top-0 z-30">
          <div className="flex items-center justify-end px-6 py-3">
            {/* Profile dropdown */}
            <div className="relative">
              <button
                className="flex items-center space-x-2 text-sm hover:bg-gray-50 rounded-lg px-3 py-2 transition-colors"
                onClick={toggleProfileDropdown}
              >
                <div className="w-9 h-9 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-sm">
                  <span className="text-white text-sm font-semibold">
                    {(user?.profile?.first_name || user?.first_name || user?.name || 'U').charAt(0).toUpperCase()}
                  </span>
                </div>
                <div className="hidden md:block text-left">
                  <div className="text-sm font-medium text-gray-900">
                    {user?.profile?.first_name || user?.first_name || user?.name || 'User'}
                  </div>
                  <div className="text-xs text-gray-500 capitalize">
                    {user?.role || user?.profile?.role || 'user'}
                  </div>
                </div>
                <ChevronDown size={16} className="text-gray-400 ml-1" />
              </button>

              {profileOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-1 z-50 border">
                  <button 
                    onClick={handleProfileClick}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                  >
                    <User size={16} className="mr-2" />
                    Profile
                  </button>
                  <button
                    onClick={handleLogoutClick}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                  >
                    <LogOut size={16} className="mr-2" />
                    Logout
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-6 lg:p-8 bg-gray-50 min-h-screen">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>

      {/* Logout Confirmation Modal */}
      {showLogoutConfirm && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
          onClick={handleLogoutCancel}
        >
          <div 
            className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center mb-4">
              <div className="flex-shrink-0 w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mr-4">
                <AlertCircle className="w-6 h-6 text-orange-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Confirm Logout</h3>
            </div>
            <div className="mb-6">
              <p className="text-sm text-gray-600">Are you sure you want to log out?</p>
            </div>
            <div className="flex justify-end gap-3">
              <button
                onClick={handleLogoutCancel}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Cancel
              </button>
              <button
                onClick={handleLogoutConfirm}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                Log Out
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardLayout;

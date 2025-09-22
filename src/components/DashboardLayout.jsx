import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Menu, X, User, LogOut, Home, Users, FileText, Calendar, Activity, Shield, ChevronDown, TrendingUp, Heart, Brain, Database } from 'lucide-react';

const DashboardLayout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const { user, logout } = useAuth();

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
    { name: 'My Records', icon: FileText, path: '/my-records', color: 'text-green-500' },
    { name: 'Appointments', icon: Calendar, path: '/appointments', color: 'text-orange-500' },
    { name: 'Prescriptions', icon: Heart, path: '/prescriptions', color: 'text-red-500' },
    { name: 'AI Assistant', icon: Brain, path: '/ai-assistant', color: 'text-purple-500' },
    { name: 'Health Tracking', icon: Activity, path: '/health-tracking', color: 'text-pink-500' },
  ];

  const menuItems = user?.role === 'doctor' ? doctorMenu : patientMenu;

  const handleLogout = () => {
    logout();
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
                {user?.name?.charAt(0)?.toUpperCase()}
              </span>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-900">{user?.name}</p>
              <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="mt-4 px-2">
          {menuItems.map((item) => (
            <a
              key={item.name}
              href={item.path}
              className="flex items-center px-2 py-2 mb-1 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-100 hover:text-gray-900 transition-colors duration-200"
            >
              <item.icon size={20} className={`mr-3 ${item.color}`} />
              {item.name}
            </a>
          ))}
        </nav>
      </div>

      {/* Main content */}
      <div className="lg:ml-64">
        {/* Top navigation */}
        <header className="bg-white shadow-sm border-b">
          <div className="flex items-center justify-between px-4 py-4">
            <div className="flex items-center">
              <button
                className="lg:hidden mr-4"
                onClick={() => setSidebarOpen(true)}
              >
                <Menu size={24} className="text-gray-600" />
              </button>
              <h1 className="text-xl font-semibold text-gray-800">Dashboard</h1>
            </div>

            <div className="flex items-center space-x-4">
              {/* Notifications */}
              <button className="relative p-2 text-gray-400 hover:text-gray-500">
                <Activity size={20} />
                <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 rounded-full text-xs text-white flex items-center justify-center">
                  3
                </span>
              </button>

              {/* Profile dropdown */}
              <div className="relative">
                <button
                  className="flex items-center space-x-2 text-sm"
                  onClick={() => setProfileOpen(!profileOpen)}
                >
                  <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm font-semibold">
                      {user?.name?.charAt(0)?.toUpperCase()}
                    </span>
                  </div>
                  <span className="hidden md:block text-gray-700">{user?.name}</span>
                  <ChevronDown size={16} className="text-gray-400" />
                </button>

                {profileOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-1 z-50">
                    <a href="/profile" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                      <User size={16} className="inline mr-2" />
                      Profile
                    </a>
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      <LogOut size={16} className="inline mr-2" />
                      Logout
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-4 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;

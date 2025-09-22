import React from 'react';
import { Plus, Eye, Calendar, Upload, Heart, Brain, FileText, Users } from 'lucide-react';

const QuickActions = ({ userRole }) => {
  const doctorActions = [
    {
      title: 'New Diagnosis',
      icon: Plus,
      color: 'from-blue-500 to-blue-600',
      description: 'Create new patient diagnosis',
      bgColor: 'bg-blue-50'
    },
    {
      title: 'View Health Records',
      icon: Eye,
      color: 'from-green-500 to-green-600',
      description: 'Access patient medical history',
      bgColor: 'bg-green-50'
    },
    {
      title: 'Manage Appointments',
      icon: Calendar,
      color: 'from-purple-500 to-purple-600',
      description: 'Schedule and manage appointments',
      bgColor: 'bg-purple-50'
    },
    {
      title: 'Upload Reports',
      icon: Upload,
      color: 'from-orange-500 to-orange-600',
      description: 'Upload medical reports & images',
      bgColor: 'bg-orange-50'
    }
  ];

  const patientActions = [
    {
      title: 'Book Appointment',
      icon: Calendar,
      color: 'from-blue-500 to-blue-600',
      description: 'Schedule with your doctor',
      bgColor: 'bg-blue-50'
    },
    {
      title: 'View Health Records',
      icon: Eye,
      color: 'from-green-500 to-green-600',
      description: 'Access your medical history',
      bgColor: 'bg-green-50'
    },
    {
      title: 'My Prescriptions',
      icon: FileText,
      color: 'from-red-500 to-red-600',
      description: 'View current medications',
      bgColor: 'bg-red-50'
    },
    {
      title: 'AI Health Assistant',
      icon: Brain,
      color: 'from-purple-500 to-purple-600',
      description: 'Get AI health insights',
      bgColor: 'bg-purple-50'
    }
  ];

  const actions = userRole === 'doctor' ? doctorActions : patientActions;

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Quick Actions</h2>
        <span className="text-sm text-gray-500">Get started quickly</span>
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {actions.map((action, index) => (
          <button
            key={index}
            className={`${action.bgColor} rounded-lg p-4 text-left hover:shadow-md transition-all duration-300 group hover:scale-105`}
          >
            <div className={`p-3 rounded-lg bg-gradient-to-r ${action.color} w-fit mb-3`}>
              <action.icon size={20} className="text-white" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-1">{action.title}</h3>
            <p className="text-sm text-gray-600">{action.description}</p>
          </button>
        ))}
      </div>
    </div>
  );
};

export default QuickActions;

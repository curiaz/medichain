import React from 'react';
import { Users, FileText, Shield, Brain, TrendingUp } from 'lucide-react';

const DashboardStats = ({ stats }) => {
  const statCards = [
    {
      title: 'Total Patients',
      value: stats.totalPatients || 1247,
      icon: Users,
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-50',
      trend: '+12%',
      trendColor: 'text-blue-600'
    },
    {
      title: 'Recent Diagnoses',
      value: stats.recentDiagnoses || 89,
      icon: FileText,
      color: 'from-green-500 to-green-600',
      bgColor: 'bg-green-50',
      trend: '+8%',
      trendColor: 'text-green-600'
    },
    {
      title: 'Blockchain Records',
      value: stats.blockchainRecords || 3421,
      icon: Shield,
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-50',
      trend: '+24%',
      trendColor: 'text-purple-600'
    },
    {
      title: 'AI Accuracy',
      value: stats.aiAccuracy || '96.8%',
      icon: Brain,
      color: 'from-orange-500 to-orange-600',
      bgColor: 'bg-orange-50',
      trend: '+3%',
      trendColor: 'text-orange-600'
    }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
      {statCards.map((card, index) => (
        <div key={index} className={`${card.bgColor} rounded-xl p-6 shadow-sm hover:shadow-md transition-all duration-300`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{card.title}</p>
              <p className="text-2xl lg:text-3xl font-bold text-gray-900 mt-1">{card.value}</p>
            </div>
            <div className={`p-3 rounded-lg bg-gradient-to-r ${card.color}`}>
              <card.icon size={24} className="text-white" />
            </div>
          </div>
          <div className="mt-4 flex items-center">
            <TrendingUp size={16} className={card.trendColor} />
            <span className={`ml-1 text-sm ${card.trendColor}`}>{card.trend}</span>
            <span className="ml-2 text-xs text-gray-500">vs last week</span>
          </div>
        </div>
      ))}
    </div>
  );
};

export default DashboardStats;

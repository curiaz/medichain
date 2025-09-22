import React from 'react';
import Header from './Header';
import { FileText, Calendar, Pill, Activity, AlertCircle, User, Heart, Clock } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import '../assets/styles/Dashboard.css';

const HealthRecord = () => {
  const { user } = useAuth();

  return (
    <div className="dashboard-container">
      {/* Background crosses */}
      <div className="background-crosses">
        {[...Array(24)].map((_, i) => (
          <span key={i} className={`cross cross-${i + 1}`}>
            +
          </span>
        ))}
      </div>

      <Header />

      <main className="dashboard-main-content">
        <div className="dashboard-header-section">
          <div className="dashboard-title-section">
            <h1 className="dashboard-title">MY HEALTH RECORD</h1>
            {user && (
              <div className="user-welcome">
                <span>Health record for <strong>{user.first_name ? `${user.first_name} ${user.last_name}` : user.name}</strong></span>
              </div>
            )}
          </div>
        </div>

        <div className="coming-soon-container">
          <div className="coming-soon-content">
            <div className="coming-soon-icon">
              <FileText size={80} />
            </div>
            <h2>Health Record Coming Soon</h2>
            <p>Your comprehensive digital health record is currently being developed. Soon you'll be able to:</p>
            
            <div className="features-grid">
              <div className="feature-item">
                <Calendar size={24} />
                <h4>Medical History</h4>
                <p>View your complete medical history and past consultations</p>
              </div>
              
              <div className="feature-item">
                <Pill size={24} />
                <h4>Prescriptions</h4>
                <p>Track your medications and prescription history</p>
              </div>
              
              <div className="feature-item">
                <Activity size={24} />
                <h4>Health Metrics</h4>
                <p>Monitor vital signs and health indicators over time</p>
              </div>
              
              <div className="feature-item">
                <Heart size={24} />
                <h4>AI Consultations</h4>
                <p>Review your AI diagnosis history and doctor reviews</p>
              </div>
              
              <div className="feature-item">
                <User size={24} />
                <h4>Doctor Access</h4>
                <p>Share your record securely with healthcare providers</p>
              </div>
              
              <div className="feature-item">
                <Clock size={24} />
                <h4>Appointment History</h4>
                <p>Keep track of all your medical appointments</p>
              </div>
            </div>

            <div className="notification-signup">
              <AlertCircle size={20} />
              <span>You'll be notified when this feature becomes available</span>
            </div>

            <div className="current-options">
              <h3>What you can do now:</h3>
              <div className="option-buttons">
                <button 
                  className="option-btn primary"
                  onClick={() => window.location.href = '/ai-health'}
                >
                  <Activity size={16} />
                  Use AI Health Assistant
                </button>
                <button 
                  className="option-btn secondary"
                  onClick={() => window.location.href = '/dashboard'}
                >
                  <User size={16} />
                  Back to Dashboard
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>

      <style jsx>{`
        .coming-soon-container {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 60vh;
          padding: 2rem;
        }

        .coming-soon-content {
          text-align: center;
          max-width: 800px;
          background: white;
          border-radius: 20px;
          padding: 3rem;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .coming-soon-icon {
          color: #00d4aa;
          margin-bottom: 2rem;
        }

        .coming-soon-content h2 {
          color: #333;
          margin-bottom: 1rem;
          font-size: 2.5rem;
          font-weight: 700;
        }

        .coming-soon-content p {
          color: #666;
          font-size: 1.2rem;
          line-height: 1.6;
          margin-bottom: 3rem;
        }

        .features-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 2rem;
          margin-bottom: 3rem;
        }

        .feature-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          text-align: center;
          padding: 1.5rem;
          background: #f8f9fa;
          border-radius: 12px;
          transition: transform 0.3s ease;
        }

        .feature-item:hover {
          transform: translateY(-4px);
        }

        .feature-item svg {
          color: #00d4aa;
          margin-bottom: 1rem;
        }

        .feature-item h4 {
          color: #333;
          margin-bottom: 0.5rem;
          font-size: 1.1rem;
          font-weight: 600;
        }

        .feature-item p {
          color: #666;
          font-size: 0.9rem;
          line-height: 1.4;
          margin: 0;
        }

        .notification-signup {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
          background: #e8f5ff;
          border: 1px solid #00d4aa;
          border-radius: 8px;
          padding: 1rem;
          margin-bottom: 2rem;
          color: #333;
        }

        .notification-signup svg {
          color: #00d4aa;
        }

        .current-options {
          background: #f8f9fa;
          border-radius: 12px;
          padding: 2rem;
        }

        .current-options h3 {
          color: #333;
          margin-bottom: 1.5rem;
          font-size: 1.3rem;
        }

        .option-buttons {
          display: flex;
          gap: 1rem;
          justify-content: center;
          flex-wrap: wrap;
        }

        .option-btn {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-weight: 500;
          font-size: 1rem;
          transition: all 0.3s ease;
          text-decoration: none;
        }

        .option-btn.primary {
          background: #00d4aa;
          color: white;
        }

        .option-btn.primary:hover {
          background: #00b899;
        }

        .option-btn.secondary {
          background: white;
          color: #333;
          border: 1px solid #ddd;
        }

        .option-btn.secondary:hover {
          background: #f5f5f5;
        }

        @media (max-width: 768px) {
          .coming-soon-content {
            padding: 2rem;
          }

          .coming-soon-content h2 {
            font-size: 2rem;
          }

          .features-grid {
            grid-template-columns: 1fr;
            gap: 1rem;
          }

          .option-buttons {
            flex-direction: column;
            align-items: center;
          }

          .option-btn {
            width: 100%;
            max-width: 300px;
            justify-content: center;
          }
        }
      `}</style>
    </div>
  );
};

export default HealthRecord;

import React from 'react';
import { CheckCircle } from 'lucide-react';
import '../assets/styles/WelcomePopup.css';

const WelcomePopup = ({ onGetStarted }) => {
  return (
    <div className="welcome-popup-overlay">
      <div className="welcome-popup-content" onClick={(e) => e.stopPropagation()}>
        <div className="welcome-popup-icon">
          <CheckCircle size={64} color="#2196F3" strokeWidth={2} />
        </div>
        
        <h2 className="welcome-popup-title">Welcome to MediChain!</h2>
        
        <p className="welcome-popup-message">Your account is ready.</p>
        
        <button className="welcome-popup-button" onClick={onGetStarted}>
          Get started
        </button>
      </div>
    </div>
  );
};

export default WelcomePopup;


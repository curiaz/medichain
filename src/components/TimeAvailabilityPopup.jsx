import React from 'react';
import { Clock } from 'lucide-react';
import '../assets/styles/WelcomePopup.css';

const TimeAvailabilityPopup = ({ onContinue }) => {
  return (
    <div className="welcome-popup-overlay">
      <div className="welcome-popup-content" onClick={(e) => e.stopPropagation()}>
        <div className="welcome-popup-icon">
          <Clock size={64} color="#2196F3" strokeWidth={2} />
        </div>
        
        <h2 className="welcome-popup-title">Set Your Availability</h2>
        
        <p className="welcome-popup-message">
          You can input your time availability now or later. This helps patients book appointments with you at convenient times.
        </p>
        
        <button className="welcome-popup-button" onClick={onContinue}>
          Continue
        </button>
      </div>
    </div>
  );
};

export default TimeAvailabilityPopup;


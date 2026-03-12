import React from 'react';
import { CheckCircle } from 'lucide-react';
import '../assets/styles/SuccessPopup.css';

const SuccessPopup = ({ onContinue }) => {
  return (
    <div className="success-popup-overlay">
      <div className="success-popup-content" onClick={(e) => e.stopPropagation()}>
        <div className="success-popup-icon">
          <CheckCircle size={64} color="#4CAF50" strokeWidth={2} />
        </div>
        
        <h2 className="success-popup-title">Your details are now updated. You're all set!</h2>
        
        <button className="success-popup-button" onClick={onContinue}>
          Continue to dashboard
        </button>
      </div>
    </div>
  );
};

export default SuccessPopup;


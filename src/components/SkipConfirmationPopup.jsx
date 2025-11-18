import React from 'react';
import { Info } from 'lucide-react';
import '../assets/styles/SkipConfirmationPopup.css';

const SkipConfirmationPopup = ({ onOk }) => {
  return (
    <div className="skip-confirmation-popup-overlay">
      <div className="skip-confirmation-popup-content" onClick={(e) => e.stopPropagation()}>
        <div className="skip-confirmation-popup-icon">
          <Info size={48} color="#2196F3" strokeWidth={2} />
        </div>
        
        <h2 className="skip-confirmation-popup-title">You can update this information anytime in your profile.</h2>
        
        <button className="skip-confirmation-popup-button" onClick={onOk}>
          OK
        </button>
      </div>
    </div>
  );
};

export default SkipConfirmationPopup;


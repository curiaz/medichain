import React from 'react';
import './RoleSelectionModal.css';

const RoleSelectionModal = ({ isOpen, onClose, onRoleSelect, title, subtitle }) => {
  if (!isOpen) return null;

  const handleRoleSelection = (role) => {
    onRoleSelect(role);
    // Don't close modal here - let parent handle it after registration
  };

  return (
    <div className="role-modal-overlay" onClick={onClose}>
      <div className="role-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">{title || "Select Your Role"}</h2>
          <p className="modal-subtitle">{subtitle || "Choose your role to get started with MediChain"}</p>
        </div>
        
        <div className="role-options">
          <button 
            className="role-option doctor-option"
            onClick={() => handleRoleSelection('doctor')}
          >
            <div className="role-icon">👨‍⚕️</div>
            <h3 className="role-title">Doctor</h3>
            <p className="role-description">Access AI-powered diagnostics and patient management tools</p>
          </button>
          
          <button 
            className="role-option patient-option"
            onClick={() => handleRoleSelection('patient')}
          >
            <div className="role-icon">👤</div>
            <h3 className="role-title">Patient</h3>
            <p className="role-description">Secure access to your health records and medical history</p>
          </button>
        </div>
        
        <button className="close-modal" onClick={onClose}>×</button>
      </div>
    </div>
  );
};

export default RoleSelectionModal;
